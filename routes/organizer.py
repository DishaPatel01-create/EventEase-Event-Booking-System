from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, Event, Category, TicketType, Booking, BookingItem, Payment
from routes import organizer_required

organizer_bp = Blueprint('organizer', __name__)

@organizer_bp.route('/dashboard')
@login_required
@organizer_required
def dashboard():
    today = date.today()
    organizer_id = current_user.id

    # Base query for organizer's events
    events = Event.query.filter_by(organizer_id=organizer_id).order_by(Event.created_at.desc()).all()
    event_ids = [e.id for e in events]

    total_events = len(events)
    upcoming_events = len([e for e in events if e.date >= today and e.status == 'published'])

    # Bookings for this organizer's events
    if event_ids:
        bookings = Booking.query.filter(Booking.event_id.in_(event_ids)).order_by(Booking.booked_at.desc()).all()
        confirmed_bookings = [b for b in bookings if b.status == 'confirmed']
        
        total_bookings = len(confirmed_bookings)
        total_revenue = sum(b.total_amount for b in confirmed_bookings)
        
        # Calculate tickets sold
        tickets_sold = sum(
            sum(item.quantity for item in b.items)
            for b in confirmed_bookings
        )
    else:
        bookings = []
        total_bookings = 0
        total_revenue = 0.0
        tickets_sold = 0

    # Prepare chart data for dashboard
    category_counts = {}
    for e in events:
        cat_name = e.category.name if e.category else 'General'
        category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

    chart_labels = list(category_counts.keys())
    chart_data = list(category_counts.values())

    return render_template(
        'organizer_dashboard.html',
        events=events,
        bookings=bookings[:10],  # Recent 10 bookings
        total_events=total_events,
        upcoming_events=upcoming_events,
        total_bookings=total_bookings,
        tickets_sold=tickets_sold,
        total_revenue=total_revenue,
        chart_labels=chart_labels,
        chart_data=chart_data
    )


@organizer_bp.route('/events/new', methods=['GET', 'POST'])
@login_required
@organizer_required
def create_event():
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        description = request.form.get('description', '').strip()
        highlights = request.form.get('highlights', '').strip()
        image = request.form.get('image', '').strip()
        date_str = request.form.get('date', '').strip()
        start_time = request.form.get('start_time', '10:00 AM').strip()
        end_time = request.form.get('end_time', '05:00 PM').strip()
        venue = request.form.get('venue', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        cancellation_policy = request.form.get('cancellation_policy', '').strip()
        status = request.form.get('status', 'published')
        featured = bool(request.form.get('featured'))

        if not title or not description or not date_str or not venue or not city:
            flash('Please fill in all required event details.', 'danger')
            return render_template('create_event.html', categories=categories)

        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('create_event.html', categories=categories)

        if not image:
            image = 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80'

        new_event = Event(
            organizer_id=current_user.id,
            category_id=category_id,
            title=title,
            description=description,
            highlights=highlights,
            image=image,
            date=event_date,
            start_time=start_time,
            end_time=end_time,
            venue=venue,
            address=address or venue,
            city=city,
            cancellation_policy=cancellation_policy or 'Free cancellation up to 48 hours before the event.',
            status=status,
            featured=featured
        )

        try:
            db.session.add(new_event)
            db.session.flush()

            # Process Ticket Types
            ticket_names = request.form.getlist('ticket_name[]')
            ticket_prices = request.form.getlist('ticket_price[]')
            ticket_capacities = request.form.getlist('ticket_capacity[]')
            ticket_descs = request.form.getlist('ticket_description[]')

            if not ticket_names:
                # Default ticket type
                default_ticket = TicketType(
                    event_id=new_event.id,
                    name='General Admission',
                    price=499.0,
                    capacity=100,
                    available_quantity=100,
                    description='Standard entry ticket.'
                )
                db.session.add(default_ticket)
            else:
                for i in range(len(ticket_names)):
                    t_name = ticket_names[i].strip()
                    if not t_name:
                        continue
                    t_price = float(ticket_prices[i]) if i < len(ticket_prices) and ticket_prices[i] else 0.0
                    t_cap = int(ticket_capacities[i]) if i < len(ticket_capacities) and ticket_capacities[i] else 50
                    t_desc = ticket_descs[i].strip() if i < len(ticket_descs) else ''

                    tt = TicketType(
                        event_id=new_event.id,
                        name=t_name,
                        price=t_price,
                        capacity=t_cap,
                        available_quantity=t_cap,
                        description=t_desc
                    )
                    db.session.add(tt)

            db.session.commit()
            flash(f'Event "{new_event.title}" has been successfully created!', 'success')
            return redirect(url_for('organizer.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating event: {str(e)}', 'danger')

    return render_template('create_event.html', categories=categories)


@organizer_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@organizer_required
def edit_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        event.title = request.form.get('title', '').strip()
        event.category_id = request.form.get('category_id', type=int)
        event.description = request.form.get('description', '').strip()
        event.highlights = request.form.get('highlights', '').strip()
        event.image = request.form.get('image', '').strip() or event.image
        date_str = request.form.get('date', '').strip()
        event.start_time = request.form.get('start_time', '').strip()
        event.end_time = request.form.get('end_time', '').strip()
        event.venue = request.form.get('venue', '').strip()
        event.address = request.form.get('address', '').strip()
        event.city = request.form.get('city', '').strip()
        event.cancellation_policy = request.form.get('cancellation_policy', '').strip()
        event.status = request.form.get('status', event.status)
        event.featured = bool(request.form.get('featured'))

        if date_str:
            try:
                event.date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Update / add tickets
        ticket_ids = request.form.getlist('ticket_id[]')
        ticket_names = request.form.getlist('ticket_name[]')
        ticket_prices = request.form.getlist('ticket_price[]')
        ticket_capacities = request.form.getlist('ticket_capacity[]')
        ticket_descs = request.form.getlist('ticket_description[]')

        for i in range(len(ticket_names)):
            t_name = ticket_names[i].strip()
            if not t_name:
                continue

            t_price = float(ticket_prices[i]) if i < len(ticket_prices) and ticket_prices[i] else 0.0
            t_cap = int(ticket_capacities[i]) if i < len(ticket_capacities) and ticket_capacities[i] else 50
            t_desc = ticket_descs[i].strip() if i < len(ticket_descs) else ''
            
            t_id = int(ticket_ids[i]) if i < len(ticket_ids) and ticket_ids[i] else None

            if t_id:
                existing_tt = db.session.get(TicketType, t_id)
                if existing_tt and existing_tt.event_id == event.id:
                    diff = t_cap - existing_tt.capacity
                    existing_tt.name = t_name
                    existing_tt.price = t_price
                    existing_tt.capacity = t_cap
                    existing_tt.available_quantity = max(0, existing_tt.available_quantity + diff)
                    existing_tt.description = t_desc
            else:
                new_tt = TicketType(
                    event_id=event.id,
                    name=t_name,
                    price=t_price,
                    capacity=t_cap,
                    available_quantity=t_cap,
                    description=t_desc
                )
                db.session.add(new_tt)

        try:
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('organizer.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update event: {str(e)}', 'danger')

    return render_template('edit_event.html', event=event, categories=categories)


@organizer_bp.route('/events/<int:event_id>/bookings')
@login_required
@organizer_required
def event_bookings(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    bookings = Booking.query.filter_by(event_id=event.id).order_by(Booking.booked_at.desc()).all()
    return render_template('organizer_bookings.html', event=event, bookings=bookings)


@organizer_bp.route('/events/<int:event_id>/toggle-status', methods=['POST'])
@login_required
@organizer_required
def toggle_status(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    new_status = request.form.get('status')
    if new_status in ['published', 'draft', 'cancelled']:
        event.status = new_status
        db.session.commit()
        flash(f'Event status updated to {new_status.capitalize()}.', 'success')

    return redirect(url_for('organizer.dashboard'))


@organizer_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@organizer_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    if event.organizer_id != current_user.id and not current_user.is_admin:
        abort(403)

    try:
        title = event.title
        db.session.delete(event)
        db.session.commit()
        flash(f'Event "{title}" has been deleted.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Cannot delete event with existing confirmed bookings.', 'danger')

    return redirect(url_for('organizer.dashboard'))
