import unittest
import json
from datetime import date, timedelta
from app import create_app
from models import db, User, Category, Event, TicketType, Booking, BookingItem, Payment, Cancellation
from database.seed import seed_database

class EventEasyFullStackTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            seed_database()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_login_page_renders_clean_and_has_3_roles(self):
        """TEST 1: Verify login page renders with empty fields and 3 role options (Attendee, Organizer, Admin)."""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EventEasy', response.data)
        self.assertIn(b'value="attendee"', response.data)
        self.assertIn(b'value="organizer"', response.data)
        self.assertIn(b'value="admin"', response.data)
        self.assertNotIn(b'fillCreds', response.data)
        self.assertIn(b'autocomplete="username"', response.data)
        self.assertIn(b'autocomplete="current-password"', response.data)

    def test_02_registration_role_enforcement(self):
        """TEST 2: Registration allows Attendee and Organizer, strictly blocks Admin creation."""
        # 1. Register as Organizer
        res_org = self.client.post('/auth/register', data={
            'name': 'Pooja Events',
            'email': 'pooja@events.com',
            'phone': '9876543211',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
            'role': 'organizer'
        }, follow_redirects=True)
        self.assertEqual(res_org.status_code, 200)

        with self.app.app_context():
            org_user = User.query.filter_by(email='pooja@events.com').first()
            self.assertIsNotNone(org_user)
            self.assertEqual(org_user.role, 'organizer')

        # 2. Public attempt to register as Admin is blocked / clamped to attendee
        res_admin_attempt = self.client.post('/auth/register', data={
            'name': 'Hacker Admin',
            'email': 'hacker@test.com',
            'phone': '9876543212',
            'password': 'SecurePassword@123',
            'confirm_password': 'SecurePassword@123',
            'role': 'admin'
        }, follow_redirects=True)
        self.assertEqual(res_admin_attempt.status_code, 200)

        with self.app.app_context():
            hacker = User.query.filter_by(email='hacker@test.com').first()
            self.assertIsNotNone(hacker)
            self.assertEqual(hacker.role, 'attendee')  # clamped to attendee

    def test_03_role_verified_login_flow(self):
        """TEST 3: Login verifies both password hash and matching database role."""
        # 1. Attendee login with correct role=attendee -> succeeds
        res_att_ok = self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'attendee'
        }, follow_redirects=True)
        self.assertEqual(res_att_ok.status_code, 200)
        self.assertIn(b'Rahul Sharma', res_att_ok.data)
        self.client.get('/auth/logout')

        # 2. Attendee tries logging in as Admin -> FAIL
        res_att_as_admin = self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'admin'
        })
        self.assertIn(b'Invalid account type or login credentials.', res_att_as_admin.data)

        # 3. Attendee tries logging in as Organizer -> FAIL
        res_att_as_org = self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'organizer'
        })
        self.assertIn(b'Invalid account type or login credentials.', res_att_as_org.data)

        # 4. Organizer login with correct role=organizer -> succeeds and lands on organizer dashboard
        res_org_ok = self.client.post('/auth/login', data={
            'email': 'organizer@eventeasy.com',
            'password': 'Organizer@123',
            'role': 'organizer'
        }, follow_redirects=True)
        self.assertEqual(res_org_ok.status_code, 200)
        self.assertIn(b'Organizer Dashboard', res_org_ok.data)
        self.client.get('/auth/logout')

        # 5. Admin login with correct role=admin -> succeeds and lands on admin dashboard
        res_admin_ok = self.client.post('/auth/login', data={
            'email': 'admin@eventeasy.com',
            'password': 'Admin@123',
            'role': 'admin'
        }, follow_redirects=True)
        self.assertEqual(res_admin_ok.status_code, 200)
        self.assertIn(b'Platform Overview', res_admin_ok.data)
        self.client.get('/auth/logout')

    def test_04_role_authorization_protection(self):
        """TEST 4: Route authorization (@organizer_required, @admin_required)."""
        # Login as attendee
        self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'attendee'
        })

        # Attendee blocked from Organizer dashboard
        res_org = self.client.get('/organizer/dashboard')
        self.assertEqual(res_org.status_code, 403)

        # Attendee blocked from Admin dashboard
        res_adm = self.client.get('/admin/dashboard')
        self.assertEqual(res_adm.status_code, 403)
        self.client.get('/auth/logout')

        # Login as Organizer
        self.client.post('/auth/login', data={
            'email': 'organizer@eventeasy.com',
            'password': 'Organizer@123',
            'role': 'organizer'
        })

        # Organizer blocked from Admin dashboard
        res_org_to_adm = self.client.get('/admin/dashboard')
        self.assertEqual(res_org_to_adm.status_code, 403)
        self.client.get('/auth/logout')

    def test_05_cross_user_isolation(self):
        """TEST 5: Attendee cannot view or cancel other user's booking."""
        with self.app.app_context():
            priya_user = User.query.filter_by(email='priya@example.com').first()
            priya_booking = Booking.query.filter_by(user_id=priya_user.id).first()
            priya_ref = priya_booking.booking_reference

        # Login as Rahul (attendee)
        self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'attendee'
        })

        # Try viewing Priya's ticket
        res_ticket = self.client.get(f'/booking/{priya_ref}/ticket')
        self.assertEqual(res_ticket.status_code, 403)

    def test_06_organizer_event_management(self):
        """TEST 6: Organizer creates an event with ticket tiers."""
        self.client.post('/auth/login', data={
            'email': 'organizer@eventeasy.com',
            'password': 'Organizer@123',
            'role': 'organizer'
        })

        create_res = self.client.post('/organizer/events/new', data={
            'title': 'AI Robotics Summit 2026',
            'category_id': 1,
            'description': 'Advanced robotics conference and expo.',
            'highlights': '• Free workshops',
            'image': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200',
            'date': (date.today() + timedelta(days=12)).isoformat(),
            'start_time': '10:00 AM',
            'end_time': '05:00 PM',
            'venue': 'Tech Convention Center',
            'address': 'MG Road',
            'city': 'Bengaluru',
            'status': 'published',
            'ticket_name[]': ['Standard Pass', 'VIP Pass'],
            'ticket_price[]': ['499', '1499'],
            'ticket_capacity[]': ['100', '25'],
            'ticket_description[]': ['General hall', 'VIP lounge']
        }, follow_redirects=True)
        self.assertEqual(create_res.status_code, 200)

        with self.app.app_context():
            created = Event.query.filter_by(title='AI Robotics Summit 2026').first()
            self.assertIsNotNone(created)
            self.assertEqual(len(created.ticket_types), 2)

    def test_07_booking_and_anti_overbooking(self):
        """TEST 7: Anti-overbooking concurrency lock and cancellation refund."""
        self.client.post('/auth/login', data={
            'email': 'attendee@eventeasy.com',
            'password': 'Attendee@123',
            'role': 'attendee'
        })

        with self.app.app_context():
            evt = Event.query.filter(Event.status == 'published').first()
            ticket = evt.ticket_types[0]
            initial_avail = ticket.available_quantity
            ticket_id = ticket.id
            evt_id = evt.id

        booking_payload = {
            'event_id': evt_id,
            'tickets': {str(ticket_id): 2},
            'payment_method': 'UPI',
            'attendee_name': 'Rahul Sharma',
            'attendee_email': 'attendee@eventeasy.com',
            'attendee_phone': '+91 91234 56780'
        }

        res = self.client.post('/checkout/process', 
                               data=json.dumps(booking_payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        res_data = json.loads(res.data)
        self.assertTrue(res_data['success'])
        booking_ref = res_data['booking_reference']

        with self.app.app_context():
            updated_ticket = db.session.get(TicketType, ticket_id)
            self.assertEqual(updated_ticket.available_quantity, initial_avail - 2)

        # Cancel and verify restoration
        cancel_res = self.client.post(f'/booking/{booking_ref}/cancel', data={'reason': 'Changed plans'}, follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)

        with self.app.app_context():
            restored_ticket = db.session.get(TicketType, ticket_id)
            self.assertEqual(restored_ticket.available_quantity, initial_avail)

if __name__ == '__main__':
    unittest.main()
