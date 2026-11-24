import json
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, session
from flask_login import login_required, current_user
from models import db, Event, TicketType, Booking, BookingItem, Payment, Cancellation

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/checkout', methods=['GET'])
@login_required
def checkout():
    event_id = request.args.get('event_id', type=int)
    if not event_id:
        flash('Invalid event selected.', 'danger')
        return redirect(url_for('events.explore'))

    event = db.session.get(Event, event_id)
    if not event or event.status != 'published':
        flash('Event is not available for booking.', 'warning')
        return redirect(url_for('events.explore'))

    # Parse tickets selected from query string (e.g., tickets[1]=2&tickets[2]=1 or raw json)
    # Format: ?event_id=1&tickets={"1": 2, "2": 1} or individual query params
    tickets_data = {}
    raw_tickets = request.args.get('tickets')
    if raw_tickets:
        try:
            tickets_data = json.loads(raw_tickets)
        except Exception:
            pass
    else:
        # Check tickets[id] format
        for key, val in request.args.items():
            if key.startswith('tickets[') and key.endswith(']'):
                t_id = key[8:-1]
                try:
                    qty = int(val)
                    if qty > 0:
                        tickets_data[t_id] = qty
                except ValueError:
                    pass

    if not tickets_data:
        flash('Please select at least one ticket to proceed with booking.', 'warning')
        return redirect(url_for('events.details', event_id=event.id))

    selected_items = []
    subtotal = 0.0

    for t_id_str, qty in tickets_data.items():
        try:
            t_id = int(t_id_str)
            qty = int(qty)
        except (ValueError, TypeError):
            continue

        if qty <= 0:
            continue

        ticket = db.session.get(TicketType, t_id)
        if not ticket or ticket.event_id != event.id:
            continue

        # Check availability
        if ticket.available_quantity < qty:
            flash(f'Sorry! Only {ticket.available_quantity} tickets are available for "{ticket.name}".', 'danger')
            return redirect(url_for('events.details', event_id=event.id))

        item_subtotal = ticket.price * qty
        subtotal += item_subtotal

        selected_items.append({
            'ticket': ticket,
            'quantity': qty,
            'unit_price': ticket.price,
            'subtotal': item_subtotal
        })

    if not selected_items:
        flash('Please select valid tickets to proceed.', 'warning')
        return redirect(url_for('events.details', event_id=event.id))

    # Fee calculation (Nominal convenience fee / platform fee)
    platform_fee = round(subtotal * 0.02, 2) if subtotal > 0 else 0.0
    gst_tax = round(platform_fee * 0.18, 2) if platform_fee > 0 else 0.0
    total_amount = round(subtotal + platform_fee + gst_tax, 2)

    return render_template(
        'checkout.html',
        event=event,
        selected_items=selected_items,
        subtotal=subtotal,
        platform_fee=platform_fee,
        gst_tax=gst_tax,
        total_amount=total_amount,
        tickets_json=json.dumps({str(item['ticket'].id): item['quantity'] for item in selected_items})
    )


@booking_bp.route('/checkout/process', methods=['POST'], strict_slashes=False)
@login_required
def process_checkout():
    """Processes booking and simulated payment with anti-overbooking lock."""
    if request.is_json:
        data = request.get_json() or {}
        event_id = int(data.get('event_id', 0)) if data.get('event_id') else None
    else:
        data = request.form
        event_id = request.form.get('event_id', type=int)

    tickets_json_str = data.get('tickets')
    payment_method = data.get('payment_method', 'UPI')
    attendee_name = (data.get('attendee_name') or current_user.name).strip()
    attendee_email = (data.get('attendee_email') or current_user.email).strip()
    attendee_phone = (data.get('attendee_phone') or current_user.phone or '').strip()

    if not event_id or not tickets_json_str:
        return jsonify({'success': False, 'message': 'Missing booking parameters.'}), 400

    try:
        if isinstance(tickets_json_str, str):
            tickets_data = json.loads(tickets_json_str)
        else:
            tickets_data = tickets_json_str
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid ticket data.'}), 400

    event = db.session.get(Event, event_id)
    if not event or event.status != 'published':
        return jsonify({'success': False, 'message': 'Event is currently not active for bookings.'}), 400

    # Execute inside a transaction with lock logic to prevent race conditions / overbooking
    try:
        subtotal = 0.0
        booking_items_to_create = []

        for t_id_str, qty_val in tickets_data.items():
            t_id = int(t_id_str)
            qty = int(qty_val)

            if qty <= 0:
                continue

            # Query with row lock where supported or atomic check
            ticket = TicketType.query.filter_by(id=t_id, event_id=event.id).with_for_update().first()
            if not ticket:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Ticket type ID {t_id} not found.'}), 400

            # Strict anti-overbooking check
            if ticket.available_quantity < qty:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Only {ticket.available_quantity} tickets remain for "{ticket.name}". You tried booking {qty}.'
                }), 400

            # Decrement availability
            ticket.available_quantity -= qty
            item_subtotal = ticket.price * qty
            subtotal += item_subtotal

            booking_items_to_create.append({
                'ticket_type_id': ticket.id,
                'ticket_name': ticket.name,
                'quantity': qty,
                'unit_price': ticket.price,
                'subtotal': item_subtotal
            })

        if not booking_items_to_create:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'No valid tickets selected.'}), 400

        # Calculate final bill
        platform_fee = round(subtotal * 0.02, 2) if subtotal > 0 else 0.0
        gst_tax = round(platform_fee * 0.18, 2) if platform_fee > 0 else 0.0
        total_amount = round(subtotal + platform_fee + gst_tax, 2)

        # 1. Create Booking
        booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            total_amount=total_amount,
            status='confirmed',
            attendee_name=attendee_name,
            attendee_email=attendee_email,
            attendee_phone=attendee_phone,
            booked_at=datetime.utcnow()
        )
        db.session.add(booking)
        db.session.flush()  # populate booking.id & default reference

        # 2. Create Booking Items
        for item_data in booking_items_to_create:
            item = BookingItem(
                booking_id=booking.id,
                ticket_type_id=item_data['ticket_type_id'],
                ticket_name=item_data['ticket_name'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal']
            )
            db.session.add(item)

        # 3. Create Payment Record (Simulated Success)
        payment = Payment(
            booking_id=booking.id,
            amount=total_amount,
            payment_method=payment_method,
            status='completed',
            paid_at=datetime.utcnow()
        )
        db.session.add(payment)

        # Commit transaction
        db.session.commit()

        redirect_url = url_for('booking.confirmation', booking_ref=booking.booking_reference)

        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Booking confirmed successfully!',
                'booking_reference': booking.booking_reference,
                'redirect_url': redirect_url
            })
        
        flash('Booking confirmed successfully!', 'success')
        return redirect(redirect_url)

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Booking failed: {str(e)}'}), 500


@booking_bp.route('/booking/<string:booking_ref>/confirmation')
@login_required
def confirmation(booking_ref):
    booking = Booking.query.filter_by(booking_reference=booking_ref).first()
    if not booking:
        abort(404)

    # Permission: Owner, Organizer, or Admin
    if booking.user_id != current_user.id and not current_user.is_admin and current_user.id != booking.event.organizer_id:
        abort(403)

    return render_template('booking_confirmation.html', booking=booking)


@booking_bp.route('/booking/<string:booking_ref>/ticket')
@login_required
def digital_ticket(booking_ref):
    booking = Booking.query.filter_by(booking_reference=booking_ref).first()
    if not booking:
        abort(404)

    # Permission check
    if booking.user_id != current_user.id and not current_user.is_admin and current_user.id != booking.event.organizer_id:
        abort(403)

    return render_template('ticket.html', booking=booking)


@booking_bp.route('/my-bookings')
@login_required
def my_bookings():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
    
    today = date.today()
    upcoming = []
    completed = []
    cancelled = []

    for b in user_bookings:
        if b.status == 'cancelled':
            cancelled.append(b)
        elif b.event and b.event.date < today:
            completed.append(b)
        else:
            upcoming.append(b)

    return render_template(
        'bookings.html',
        upcoming=upcoming,
        completed=completed,
        cancelled=cancelled,
        all_bookings=user_bookings
    )


@booking_bp.route('/booking/<string:booking_ref>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_ref):
    booking = Booking.query.filter_by(booking_reference=booking_ref).first()
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('booking.my_bookings'))

    # Security check
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if not booking.is_cancellable:
        flash('This booking is not eligible for cancellation.', 'warning')
        return redirect(url_for('booking.my_bookings'))

    reason = request.form.get('reason', 'User requested cancellation')

    try:
        # Restore ticket quantities back to inventory
        for item in booking.items:
            if item.ticket_type_id:
                ticket = db.session.get(TicketType, item.ticket_type_id)
                if ticket:
                    ticket.available_quantity += item.quantity

        # Update booking status
        booking.status = 'cancelled'

        # Update payment status
        if booking.payment:
            booking.payment.status = 'refunded'

        # Record cancellation & refund
        cancellation = Cancellation(
            booking_id=booking.id,
            reason=reason,
            refund_amount=booking.total_amount,
            status='refunded',
            requested_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        db.session.add(cancellation)
        db.session.commit()

        flash(f'Booking {booking.booking_reference} cancelled successfully. ₹{booking.total_amount:,.2f} will be refunded to your source payment method.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to cancel booking. Please try again.', 'danger')

    return redirect(url_for('booking.my_bookings'))
