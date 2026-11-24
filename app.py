import os
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from config import config_by_name, Config
from models import db, User, Category

def create_app(config_name=None):
    """Application factory for EventEasy."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, Config))

    # Initialize extensions
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(amount):
        try:
            val = float(amount)
            if val == 0:
                return 'Free'
            # Indian numbering format or clean standard comma separation
            return f"₹{val:,.2f}".replace('.00', '')
        except (ValueError, TypeError):
            return '₹0'

    @app.template_filter('badge_status')
    def badge_status_filter(status):
        status_map = {
            'published': 'bg-success-subtle text-success border border-success-subtle',
            'draft': 'bg-secondary-subtle text-secondary border border-secondary-subtle',
            'cancelled': 'bg-danger-subtle text-danger border border-danger-subtle',
            'confirmed': 'bg-success-subtle text-success border border-success-subtle',
            'completed': 'bg-info-subtle text-info border border-info-subtle',
            'refunded': 'bg-warning-subtle text-warning border border-warning-subtle',
            'refund_pending': 'bg-warning-subtle text-warning border border-warning-subtle',
        }
        return status_map.get(str(status).lower(), 'bg-secondary-subtle text-secondary')

    # Context processors
    @app.context_processor
    def inject_global_context():
        categories = []
        try:
            categories = Category.query.order_by(Category.name).all()
        except Exception:
            pass
        return {
            'app_name': app.config.get('APP_NAME', 'EventEasy'),
            'currency_symbol': app.config.get('CURRENCY_SYMBOL', '₹'),
            'nav_categories': categories
        }

    # Register Blueprints
    from routes.home import home_bp
    from routes.auth import auth_bp
    from routes.events import events_bp
    from routes.booking import booking_bp
    from routes.organizer import organizer_bp
    from routes.admin import admin_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(booking_bp)
    app.register_blueprint(organizer_bp, url_prefix='/organizer')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # CLI database commands
    @app.cli.command('init-db')
    def init_db_command():
        """Creates database tables."""
        with app.app_context():
            db.create_all()
            print("[OK] Database tables created successfully.")

    @app.cli.command('seed-db')
    def seed_db_command():
        """Seeds the database with rich sample data."""
        from database.seed import seed_database
        with app.app_context():
            db.create_all()
            seed_database()
            print("[OK] Database seeded successfully.")

    # Automatically create tables if not existing
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Warning: Could not automatically run create_all on startup: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
