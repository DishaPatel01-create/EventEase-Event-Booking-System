import uuid
from datetime import datetime, date
from models import db

def generate_booking_reference():
    return f"EE-{datetime.utcnow().year}-{uuid.uuid4().hex[:8].upper()}"

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    booking_reference = db.Column(db.String(32), unique=True, nullable=False, default=generate_booking_reference, index=True)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(30), nullable=False, default='confirmed', index=True)  # 'confirmed', 'completed', 'cancelled'
    
    # Attendee Details snapshot at booking time
    attendee_name = db.Column(db.String(100), nullable=True)
    attendee_email = db.Column(db.String(120), nullable=True)
    attendee_phone = db.Column(db.String(20), nullable=True)
    
    booked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('BookingItem', backref='booking', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='booking', uselist=False, lazy=True, cascade='all, delete-orphan')
    cancellation = db.relationship('Cancellation', backref='booking', uselist=False, lazy=True, cascade='all, delete-orphan')

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items)

    @property
    def is_cancellable(self):
        if self.status != 'confirmed':
            return False
        if not self.event:
            return False
        return self.event.date >= date.today()

    @property
    def formatted_booked_at(self):
        return self.booked_at.strftime('%d %b %Y, %I:%M %p') if self.booked_at else ''

    def to_dict(self):
        return {
            'id': self.id,
            'booking_reference': self.booking_reference,
            'event_id': self.event_id,
            'event_title': self.event.title if self.event else 'Unknown Event',
            'event_date': self.event.formatted_date if self.event else '',
            'venue': self.event.venue if self.event else '',
            'total_amount': float(self.total_amount),
            'status': self.status,
            'total_quantity': self.total_quantity,
            'attendee_name': self.attendee_name,
            'attendee_email': self.attendee_email,
            'booked_at': self.formatted_booked_at,
            'is_cancellable': self.is_cancellable,
            'items': [item.to_dict() for item in self.items]
        }

    def __repr__(self):
        return f'<Booking {self.booking_reference} - {self.status}>'


class BookingItem(db.Model):
    __tablename__ = 'booking_items'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, index=True)
    ticket_type_id = db.Column(db.Integer, db.ForeignKey('ticket_types.id', ondelete='SET NULL'), nullable=True, index=True)
    ticket_name = db.Column(db.String(100), nullable=True)  # Snapshot in case ticket type is changed
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_type_id': self.ticket_type_id,
            'ticket_name': self.ticket_name or (self.ticket_type.name if self.ticket_type else 'General Pass'),
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'subtotal': float(self.subtotal)
        }

    def __repr__(self):
        return f'<BookingItem {self.ticket_name} x {self.quantity}>'
