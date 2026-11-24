import uuid
from datetime import datetime
from models import db

def generate_payment_reference():
    return f"PAY-{datetime.utcnow().year}-{uuid.uuid4().hex[:10].upper()}"

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    payment_reference = db.Column(db.String(50), unique=True, nullable=False, default=generate_payment_reference, index=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='UPI')  # 'UPI', 'Credit/Debit Card', 'Net Banking'
    status = db.Column(db.String(30), nullable=False, default='completed')   # 'completed', 'refunded', 'pending'
    paid_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'payment_reference': self.payment_reference,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'status': self.status,
            'paid_at': self.paid_at.strftime('%d %b %Y, %I:%M %p') if self.paid_at else ''
        }

    def __repr__(self):
        return f'<Payment {self.payment_reference} - ₹{self.amount} ({self.status})>'
