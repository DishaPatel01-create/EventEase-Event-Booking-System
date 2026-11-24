import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_REGEX = re.compile(r'^[6-9]\d{9}$')

def sanitize_phone(phone_input):
    """Sanitizes phone input to a clean 10-digit string."""
    if not phone_input:
        return ''
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone_input)
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    elif cleaned.startswith('0') and len(cleaned) == 11:
        cleaned = cleaned[1:]
    return cleaned

@auth_bp.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_organizer:
            return redirect(url_for('organizer.dashboard'))
        return redirect(url_for('home.index'))

    role_preselect = request.args.get('role', 'attendee').lower()
    if role_preselect not in ['attendee', 'organizer']:
        role_preselect = 'attendee'

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        raw_phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'attendee').lower()

        # 1. Required field checks
        if not name or not email or not raw_phone or not password or not confirm_password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 2. Email format validation
        if not EMAIL_REGEX.match(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 3. Phone validation (10-digit Indian standard)
        phone = sanitize_phone(raw_phone)
        if not PHONE_REGEX.match(phone):
            flash('Please enter a valid 10-digit mobile number.', 'danger')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 4. Password validation (Min 8 characters)
        if len(password) < 8:
            flash('Password must contain at least 8 characters.', 'danger')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 5. Confirm password match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 6. Restrict admin self-registration strictly
        if role not in ['attendee', 'organizer']:
            role = 'attendee'

        # 7. Check duplicate email in DB
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login', role=role))

        # 8. Check duplicate phone in DB
        if User.query.filter_by(phone=f"+91 {phone}").first() or User.query.filter_by(phone=phone).first():
            flash('An account with this phone number already exists.', 'warning')
            return render_template('register.html', name=name, email=email, phone=raw_phone, role=role)

        # 9. Create user with hashed password
        new_user = User(
            name=name,
            email=email,
            role=role,
            phone=f"+91 {phone}"
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash(f'Welcome to EventEasy, {new_user.name}! Your account has been created.', 'success')

            if new_user.is_organizer:
                return redirect(url_for('organizer.dashboard'))
            return redirect(url_for('home.index'))
        except Exception:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', role=role_preselect)


@auth_bp.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_organizer:
            return redirect(url_for('organizer.dashboard'))
        return redirect(url_for('home.index'))

    # Default role selection
    selected_role = request.args.get('role', 'attendee').lower()
    if selected_role not in ['attendee', 'organizer', 'admin']:
        selected_role = 'attendee'

    if request.method == 'POST':
        selected_role = request.form.get('role', 'attendee').lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        # Role sanitization
        if selected_role not in ['attendee', 'organizer', 'admin']:
            selected_role = 'attendee'

        # Email & password validation
        if not email or not password or not EMAIL_REGEX.match(email):
            flash('Invalid account type or login credentials.', 'danger')
            return render_template('login.html', selected_role=selected_role, email=email)

        # Database lookup
        user = User.query.filter_by(email=email).first()

        # Secure password hash check AND role verification
        if user and user.check_password(password):
            # Verify selected role against user's actual database role
            if user.role != selected_role:
                flash('Invalid account type or login credentials.', 'danger')
                return render_template('login.html', selected_role=selected_role, email=email)

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.name}!', 'success')

            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/auth') and not next_page.startswith('http'):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_organizer:
                return redirect(url_for('organizer.dashboard'))
            return redirect(url_for('home.index'))
        else:
            # Generic error message to prevent enumeration
            flash('Invalid account type or login credentials.', 'danger')
            return render_template('login.html', selected_role=selected_role, email=email)

    # Clean GET request: empty fields
    return render_template('login.html', selected_role=selected_role)


@auth_bp.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        raw_phone = request.form.get('phone', '').strip()

        if not name:
            flash('Name cannot be empty.', 'danger')
        else:
            current_user.name = name
            if raw_phone:
                phone = sanitize_phone(raw_phone)
                if PHONE_REGEX.match(phone):
                    current_user.phone = f"+91 {phone}"
                else:
                    flash('Please enter a valid 10-digit mobile number.', 'warning')
                    return render_template('profile.html')
            db.session.commit()
            flash('Profile updated successfully!', 'success')

    return render_template('profile.html')
