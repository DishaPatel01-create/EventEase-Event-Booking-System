from models import db

class TicketType(db.Model):
    __tablename__ = 'ticket_types'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    capacity = db.Column(db.Integer, nullable=False, default=100)
    available_quantity = db.Column(db.Integer, nullable=False, default=100)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    booking_items = db.relationship('BookingItem', backref='ticket_type', lazy=True)

    @property
    def is_sold_out(self):
        return self.available_quantity <= 0

    @property
    def is_limited(self):
        return 0 < self.available_quantity <= 10

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'name': self.name,
            'price': float(self.price),
            'capacity': self.capacity,
            'available_quantity': self.available_quantity,
            'description': self.description,
            'is_sold_out': self.is_sold_out,
            'is_limited': self.is_limited
        }

    def __repr__(self):
        return f'<TicketType {self.name} - ₹{self.price} ({self.available_quantity}/{self.capacity} left)>'
