from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, request, jsonify, abort
from sqlalchemy import or_, and_, func
from models import db, Event, Category, TicketType, User

events_bp = Blueprint('events', __name__)

@events_bp.route('/', strict_slashes=False)
@events_bp.route('', strict_slashes=False)
def explore():
    # Fetch filter parameters
    q = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    city = request.args.get('city', '').strip()
    date_preset = request.args.get('date_preset', '').strip()
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()
    price_range = request.args.get('price_range', '').strip()
    min_price_str = request.args.get('min_price', '').strip()
    max_price_str = request.args.get('max_price', '').strip()
    availability = request.args.get('availability', '').strip()
    sort_by = request.args.get('sort', 'soonest').strip()
    
    # Base query for published events
    query = Event.query.filter(Event.status == 'published')

    # Text Search (Title, Description, Venue, City, Organizer)
    if q:
        search_filter = or_(
            Event.title.ilike(f'%{q}%'),
            Event.description.ilike(f'%{q}%'),
            Event.venue.ilike(f'%{q}%'),
            Event.city.ilike(f'%{q}%'),
            Event.organizer.has(User.name.ilike(f'%{q}%'))
        )
        query = query.filter(search_filter)

    # Category Filter
    if category_slug:
        query = query.filter(Event.category.has(Category.slug == category_slug))

    # City Filter
    if city and city != 'all':
        query = query.filter(Event.city.ilike(f'%{city}%'))

    # Date Filters
    today = date.today()
    if date_preset == 'today':
        query = query.filter(Event.date == today)
    elif date_preset == 'tomorrow':
        query = query.filter(Event.date == today + timedelta(days=1))
    elif date_preset == 'this_week':
        end_week = today + timedelta(days=(6 - today.weekday()))
        query = query.filter(Event.date >= today, Event.date <= end_week)
    elif date_preset == 'this_month':
        next_month = today.replace(day=28) + timedelta(days=4)
        end_month = next_month - timedelta(days=next_month.day)
        query = query.filter(Event.date >= today, Event.date <= end_month)
    elif date_preset == 'custom' or (start_date_str or end_date_str):
        if start_date_str:
            try:
                s_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(Event.date >= s_date)
            except ValueError:
                pass
        if end_date_str:
            try:
                e_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(Event.date <= e_date)
            except ValueError:
                pass
    else:
        # Default: Only upcoming or current events unless explicit past search
        query = query.filter(Event.date >= today)

    # Price Filters
    if price_range == 'free':
        query = query.filter(Event.ticket_types.any(TicketType.price == 0))
    elif price_range == '0-500':
        query = query.filter(Event.ticket_types.any(and_(TicketType.price >= 0, TicketType.price <= 500)))
    elif price_range == '500-1000':
        query = query.filter(Event.ticket_types.any(and_(TicketType.price >= 500, TicketType.price <= 1000)))
    elif price_range == '1000-2500':
        query = query.filter(Event.ticket_types.any(and_(TicketType.price >= 1000, TicketType.price <= 2500)))
    elif price_range == '2500+':
        query = query.filter(Event.ticket_types.any(TicketType.price >= 2500))

    if min_price_str:
        try:
            min_val = float(min_price_str)
            query = query.filter(Event.ticket_types.any(TicketType.price >= min_val))
        except ValueError:
            pass

    if max_price_str:
        try:
            max_val = float(max_price_str)
            query = query.filter(Event.ticket_types.any(TicketType.price <= max_val))
        except ValueError:
            pass

    # Availability filter
    if availability == 'available':
        query = query.filter(Event.ticket_types.any(TicketType.available_quantity > 0))
    elif availability == 'limited':
        query = query.filter(Event.ticket_types.any(and_(TicketType.available_quantity > 0, TicketType.available_quantity <= 15)))
    elif availability == 'sold_out':
        query = query.filter(~Event.ticket_types.any(TicketType.available_quantity > 0))

    # Sorting
    if sort_by == 'soonest':
        query = query.order_by(Event.date.asc(), Event.id.asc())
    elif sort_by == 'latest':
        query = query.order_by(Event.date.desc())
    elif sort_by == 'recommended':
        query = query.order_by(Event.featured.desc(), Event.date.asc())
    elif sort_by == 'price_asc':
        # Handled in python sorting for accurate starting price if needed or via join
        events = query.all()
        events.sort(key=lambda x: x.starting_price)
    elif sort_by == 'price_desc':
        events = query.all()
        events.sort(key=lambda x: x.starting_price, reverse=True)
    elif sort_by == 'popular':
        # Sort by bookings count
        events = query.all()
        events.sort(key=lambda x: len(x.bookings), reverse=True)

    if sort_by not in ['price_asc', 'price_desc', 'popular']:
        events = query.all()

    # If AJAX request or JSON format requested
    if request.args.get('format') == 'json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'count': len(events),
            'events': [e.to_dict() for e in events]
        })

    # Available filters metadata for the UI
    categories = Category.query.order_by(Category.name).all()
    cities = [c[0] for c in db.session.query(Event.city).filter(Event.status == 'published').distinct().all() if c[0]]

    return render_template(
        'events.html',
        events=events,
        categories=categories,
        cities=cities,
        selected_category=category_slug,
        selected_city=city,
        selected_date_preset=date_preset,
        selected_price_range=price_range,
        selected_availability=availability,
        selected_sort=sort_by,
        search_query=q
    )


@events_bp.route('/<int:event_id>')
def details(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    # If draft or cancelled, only the organizer or admin can view
    if event.status != 'published':
        from flask_login import current_user
        if not current_user.is_authenticated or (current_user.id != event.organizer_id and not current_user.is_admin):
            abort(404)

    # Similar events in same category
    similar_events = Event.query.filter(
        Event.status == 'published',
        Event.category_id == event.category_id,
        Event.id != event.id,
        Event.date >= date.today()
    ).limit(3).all()

    return render_template('event_details.html', event=event, similar_events=similar_events)
