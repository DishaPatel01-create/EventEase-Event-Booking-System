# Routes package
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def organizer_required(f):
    """Decorator to require Organizer or Admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in as an Organizer to access this section.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_organizer:
            flash('Access restricted. Organizer privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require Admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in as an Administrator.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access restricted. Administrator privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
