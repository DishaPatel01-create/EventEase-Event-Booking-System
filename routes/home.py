from datetime import date
from flask import Blueprint, render_template
from models import Event, Category

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    today = date.today()
    
    # Get all active categories with event counts
    categories = Category.query.all()
    
    # Featured events (published, upcoming or ongoing)
    featured_events = Event.query.filter(
        Event.status == 'published',
        Event.date >= today,
        Event.featured == True
    ).order_by(Event.date.asc()).limit(6).all()
    
    # If not enough featured, fill with upcoming published events
    if len(featured_events) < 3:
        featured_events = Event.query.filter(
            Event.status == 'published',
            Event.date >= today
        ).order_by(Event.date.asc()).limit(6).all()

    # Upcoming events section
    upcoming_events = Event.query.filter(
        Event.status == 'published',
        Event.date >= today
    ).order_by(Event.date.asc()).limit(8).all()

    # Get distinct cities for hero location picker
    cities = [c[0] for c in Event.query.with_entities(Event.city).distinct().all() if c[0]]

    return render_template(
        'index.html',
        categories=categories,
        featured_events=featured_events,
        upcoming_events=upcoming_events,
        cities=cities
    )
