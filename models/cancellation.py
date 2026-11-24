import uuid
from datetime import datetime
from models import db

def generate_refund_reference():
    return f"REF-{datetime.utcnow().year}-{uuid.uuid4().hex[:8].upper()}"

class Cancellation(db.Model):
    __tablename__ = 'cancellations'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    reason = db.Column(db.String(255), nullable=True)
    refund_amount = db.Column(db.Float, nullable=False, default=0.0)
    refund_reference = db.Column(db.String(50), unique=True, nullable=False, default=generate_refund_reference)
    status = db.Column(db.String(30), nullable=False, default='refunded')  # 'refund_pending', 'refunded', 'rejected'
    requested_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'reason': self.reason,
            'refund_amount': float(self.refund_amount),
            'refund_reference': self.refund_reference,
            'status': self.status,
            'requested_at': self.requested_at.strftime('%d %b %Y, %I:%M %p') if self.requested_at else '',
            'processed_at': self.processed_at.strftime('%d %b %Y, %I:%M %p') if self.processed_at else ''
        }

    def __repr__(self):
        return f'<Cancellation for Booking #{self.booking_id} - {self.status}>'
