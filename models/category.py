from models import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fa-calendar-alt')
    badge_color = db.Column(db.String(30), default='primary')

    # Relationships
    events = db.relationship('Event', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'badge_color': self.badge_color,
            'event_count': len([e for e in self.events if e.status == 'published'])
        }

    def __repr__(self):
        return f'<Category {self.name}>'
