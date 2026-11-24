from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import db, User, Event, Booking, Payment, Category
from routes import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_organizers = User.query.filter_by(role='organizer').count()
    total_attendees = User.query.filter_by(role='attendee').count()
    total_events = Event.query.count()
    total_bookings = Booking.query.count()
    
    confirmed_bookings = Booking.query.filter_by(status='confirmed').all()
    total_revenue = sum(b.total_amount for b in confirmed_bookings)

    users = User.query.order_by(User.created_at.desc()).all()
    events = Event.query.order_by(Event.created_at.desc()).all()
    bookings = Booking.query.order_by(Booking.booked_at.desc()).limit(20).all()
    categories = Category.query.all()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_organizers=total_organizers,
        total_attendees=total_attendees,
        total_events=total_events,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        users=users,
        events=events,
        bookings=bookings,
        categories=categories
    )


@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    user = db.session.get(User, user_id)
    if not user:
        abort(404)

    if user.id == current_user.id:
        flash('You cannot change your own admin role.', 'warning')
        return redirect(url_for('admin.dashboard'))

    new_role = request.form.get('role')
    if new_role in ['attendee', 'organizer', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'Role for {user.name} ({user.email}) updated to {new_role}.', 'success')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    event = db.session.get(Event, event_id)
    if not event:
        abort(404)

    title = event.title
    db.session.delete(event)
    db.session.commit()
    flash(f'Admin deleted event "{title}".', 'info')

    return redirect(url_for('admin.dashboard'))
