from datetime import datetime, date
from models import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    highlights = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(500), nullable=False, default='https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80')
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(20), nullable=False, default='10:00 AM')
    end_time = db.Column(db.String(20), nullable=True, default='05:00 PM')
    venue = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='published', index=True)  # 'published', 'draft', 'cancelled'
    cancellation_policy = db.Column(db.Text, nullable=True, default='Free cancellation up to 48 hours before the event start time. 100% refund will be credited back.')
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ticket_types = db.relationship('TicketType', backref='event', lazy=True, cascade='all, delete-orphan', order_by='TicketType.price')
    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')

    @property
    def starting_price(self):
        active_tickets = [t for t in self.ticket_types if t.price is not None]
        if not active_tickets:
            return 0.0
        return min(t.price for t in active_tickets)

    @property
    def total_capacity(self):
        return sum(t.capacity for t in self.ticket_types)

    @property
    def total_available_tickets(self):
        return sum(t.available_quantity for t in self.ticket_types)

    @property
    def is_sold_out(self):
        return self.total_available_tickets <= 0

    @property
    def is_limited_availability(self):
        return 0 < self.total_available_tickets <= 15

    @property
    def is_past(self):
        return self.date < date.today()

    @property
    def formatted_date(self):
        return self.date.strftime('%a, %d %b %Y') if self.date else ''

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'highlights': self.highlights,
            'image': self.image,
            'date': self.date.isoformat() if self.date else None,
            'formatted_date': self.formatted_date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'venue': self.venue,
            'address': self.address,
            'city': self.city,
            'status': self.status,
            'category': self.category.to_dict() if self.category else None,
            'organizer_name': self.organizer.name if self.organizer else 'Event Organizer',
            'starting_price': float(self.starting_price),
            'total_available': self.total_available_tickets,
            'is_sold_out': self.is_sold_out,
            'is_limited': self.is_limited_availability,
            'ticket_types': [t.to_dict() for t in self.ticket_types]
        }

    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'
