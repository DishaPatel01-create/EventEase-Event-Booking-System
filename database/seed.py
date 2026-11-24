import os
import sys
from datetime import date, timedelta, datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from models import db, User, Category, Event, TicketType, Booking, BookingItem, Payment, Cancellation

def seed_database():
    print("Starting database seeding...")

    # Clear existing data in reverse order of relationships
    Cancellation.query.delete()
    Payment.query.delete()
    BookingItem.query.delete()
    Booking.query.delete()
    TicketType.query.delete()
    Event.query.delete()
    Category.query.delete()
    User.query.delete()
    db.session.commit()
    print("Cleared existing records.")

    # 1. Create Categories
    categories_data = [
        {'name': 'Concerts & Music', 'slug': 'concerts', 'icon': 'fa-music', 'badge_color': 'danger', 'description': 'Live concerts, music festivals, acoustic nights, and DJ performances.'},
        {'name': 'Workshops & Bootcamps', 'slug': 'workshops', 'icon': 'fa-laptop-code', 'badge_color': 'primary', 'description': 'Hands-on practical workshops, coding bootcamps, and skill building.'},
        {'name': 'Conferences', 'slug': 'conferences', 'icon': 'fa-chalkboard-user', 'badge_color': 'info', 'description': 'Industry summits, academic symposiums, and keynote conventions.'},
        {'name': 'College Events', 'slug': 'college-events', 'icon': 'fa-graduation-cap', 'badge_color': 'warning', 'description': 'Inter-college fests, department symposiums, and student galas.'},
        {'name': 'Hackathons & Tech', 'slug': 'hackathons', 'icon': 'fa-code', 'badge_color': 'success', 'description': 'Coding marathons, innovation sprints, and robotics challenges.'},
        {'name': 'Seminars & Talks', 'slug': 'seminars', 'icon': 'fa-microphone', 'badge_color': 'secondary', 'description': 'Expert panel discussions, masterclasses, and career sessions.'},
        {'name': 'Sports & Fitness', 'slug': 'sports', 'icon': 'fa-trophy', 'badge_color': 'warning', 'description': 'Tournaments, marathons, gaming leagues, and sports meets.'},
        {'name': 'Cultural & Arts', 'slug': 'cultural', 'icon': 'fa-masks-theater', 'badge_color': 'danger', 'description': 'Drama, open mics, dance showcases, and cultural celebrations.'},
        {'name': 'Exhibitions & Expos', 'slug': 'exhibitions', 'icon': 'fa-palette', 'badge_color': 'info', 'description': 'Art galleries, photography expos, trade shows, and auto expos.'},
        {'name': 'Networking & Business', 'slug': 'networking', 'icon': 'fa-users', 'badge_color': 'primary', 'description': 'Startup pitch meets, angel network mixers, and career fairs.'}
    ]

    category_map = {}
    for c_data in categories_data:
        cat = Category(**c_data)
        db.session.add(cat)
        category_map[cat.slug] = cat

    db.session.commit()
    print(f"[OK] Created {len(categories_data)} categories.")

    # 2. Create Users (Demo accounts + organizers)
    demo_admin = User(name='Platform Administrator', email='admin@eventeasy.com', role='admin', phone='+91 98765 43210')
    demo_admin.set_password('Admin@123')

    demo_organizer = User(name='Nexus Event Organizers', email='organizer@eventeasy.com', role='organizer', phone='+91 98234 56789')
    demo_organizer.set_password('Organizer@123')

    demo_organizer_2 = User(name='Campus Pulse Community', email='campus@eventeasy.com', role='organizer', phone='+91 97123 45678')
    demo_organizer_2.set_password('Campus@123')

    demo_attendee = User(name='Rahul Sharma', email='attendee@eventeasy.com', role='attendee', phone='+91 91234 56780')
    demo_attendee.set_password('Attendee@123')

    demo_attendee_2 = User(name='Priya Patel', email='priya@example.com', role='attendee', phone='+91 92345 67891')
    demo_attendee_2.set_password('Priya@123')

    db.session.add_all([demo_admin, demo_organizer, demo_organizer_2, demo_attendee, demo_attendee_2])
    db.session.commit()
    print("[OK] Created Demo Users (Admin, Organizers, Attendees).")

    # 3. Create 18+ Rich Realistic Events
    today = date.today()

    events_data = [
        {
            'organizer': demo_organizer,
            'category': category_map['hackathons'],
            'title': 'HackNova 2026: National 36-Hour AI Hackathon',
            'description': 'Join 500+ top developers, designers, and innovators across India for a 36-hour non-stop building sprint focused on Generative AI, Web3, and Climate Tech. Mentorship from top tech leads and ₹5,00,000 in total prizes.',
            'highlights': '• Free food & 24/7 energy drinks\n• Mentors from Google, Microsoft, and Uber\n• High-speed gigabit Wi-Fi & sleeping pods\n• Certificates and sponsor goodies',
            'image': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=5),
            'start_time': '09:00 AM',
            'end_time': '09:00 PM (Next Day)',
            'venue': 'Tech Innovation Hub, Cyber City',
            'address': 'Plot 42, Knowledge Park, Phase 3',
            'city': 'Bengaluru',
            'featured': True,
            'tickets': [
                {'name': 'Student Hacker Pass', 'price': 0.0, 'capacity': 200, 'desc': 'Free entry with valid student ID verification.'},
                {'name': 'Team Pass (4 Members)', 'price': 999.0, 'capacity': 50, 'desc': 'All-access team registration with dedicated booth.'},
                {'name': 'VIP Observer & Mentor', 'price': 2499.0, 'capacity': 20, 'desc': 'Exclusive networking lounge and judge dinner.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['workshops'],
            'title': 'Advanced Python & FastAPI Masterclass',
            'description': 'Deep dive into asynchronous programming, design patterns, microservices architecture, and production deployment using Python 3.12+ and FastAPI. Interactive hands-on coding sessions with real-world case studies.',
            'highlights': '• Live coding repository access\n• Production Docker & Kubernetes templates\n• 1-on-1 Q&A and architecture review\n• Verified certification',
            'image': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=3),
            'start_time': '10:00 AM',
            'end_time': '04:30 PM',
            'venue': 'DevStudio Coworking',
            'address': '12th Floor, World Trade Center',
            'city': 'Pune',
            'featured': True,
            'tickets': [
                {'name': 'Early Bird Ticket', 'price': 499.0, 'capacity': 60, 'desc': 'Discounted entry for early registrants.'},
                {'name': 'General Admission', 'price': 799.0, 'capacity': 80, 'desc': 'Full day workshop pass + lunch.'},
                {'name': 'Pro Dev Pass (with 1-on-1)', 'price': 1499.0, 'capacity': 15, 'desc': 'Includes code review and 45min mentorship.'}
            ]
        },
        {
            'organizer': demo_organizer_2,
            'category': category_map['college-events'],
            'title': 'Tarang 2026: Annual Inter-College Cultural Extravaganza',
            'description': 'The biggest college festival of the year! Featuring battle of the bands, fashion parades, dance face-offs, drama competitions, food trucks, and a star-studded celebrity musical night.',
            'highlights': '• 25+ Inter-collegiate competitions\n• Celebrity DJ performance in the evening\n• 40+ Food and merchandise stalls\n• Grand trophy awards ceremony',
            'image': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=8),
            'start_time': '09:00 AM',
            'end_time': '10:30 PM',
            'venue': 'Grand University Amphitheatre',
            'address': 'Main Campus Road, University Circle',
            'city': 'Ahmedabad',
            'featured': True,
            'tickets': [
                {'name': 'Student Entry Pass', 'price': 199.0, 'capacity': 500, 'desc': 'Access to all day competitions and food carnival.'},
                {'name': 'All-Access Musical Night Pass', 'price': 499.0, 'capacity': 300, 'desc': 'Guaranteed entry to the headline DJ & band concert.'},
                {'name': 'VIP Front-Row Pass', 'price': 1199.0, 'capacity': 50, 'desc': 'Front stage zone access and refreshments.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['concerts'],
            'title': 'Neon Horizon: Indie Fusion Live Concert',
            'description': 'An electrifying evening of indie rock, electronic beats, and acoustic melodies featuring top breakthrough artists and bands across India. Immersive light shows and state-of-the-art acoustic soundstage.',
            'highlights': '• 4 Band performances + headline act\n• Synchronized laser & light visual experience\n• Open-air festival vibe with craft beverage stalls',
            'image': 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=12),
            'start_time': '06:30 PM',
            'end_time': '11:00 PM',
            'venue': 'Jio World Garden',
            'address': 'Bandra Kurla Complex, Bandra East',
            'city': 'Mumbai',
            'featured': True,
            'tickets': [
                {'name': 'Silver Standing', 'price': 799.0, 'capacity': 350, 'desc': 'General arena standing area.'},
                {'name': 'Gold Fan Pit', 'price': 1499.0, 'capacity': 150, 'desc': 'Close-up pit area with express entrance.'},
                {'name': 'VIP Lounge Pass', 'price': 2999.0, 'capacity': 40, 'desc': 'Elevated deck, unlimited appetizers, meet & greet.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['conferences'],
            'title': 'India Cloud & DevOps Summit 2026',
            'description': 'The premier gathering of Cloud Architects, DevOps Engineers, SREs, and CTOs. Explore the future of Serverless, Platform Engineering, Kubernetes at scale, and AI-driven Infrastructure automation.',
            'highlights': '• 18 Technical sessions and keynotes\n• Hands-on lab kiosks by AWS & Azure architects\n• Enterprise networking lunch\n• Swag kit with certified developer perks',
            'image': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=15),
            'start_time': '08:30 AM',
            'end_time': '06:00 PM',
            'venue': 'Hyderabad International Convention Centre (HICC)',
            'address': 'Novotel & HICC Complex, HITEC City',
            'city': 'Hyderabad',
            'featured': True,
            'tickets': [
                {'name': 'Standard Delegate', 'price': 1499.0, 'capacity': 250, 'desc': 'Full day conference entry, lunch & high-tea.'},
                {'name': 'Corporate Team Pass (3 Pax)', 'price': 3899.0, 'capacity': 40, 'desc': '3 delegate passes with workshop access.'},
                {'name': 'Executive VIP Pass', 'price': 4999.0, 'capacity': 25, 'desc': 'Speaker lounge access, dinner & VIP seating.'}
            ]
        },
        {
            'organizer': demo_organizer_2,
            'category': category_map['sports'],
            'title': 'Inter-State Box Cricket & Football League 2026',
            'description': 'Action-packed corporate and open sports league under floodlights! 32 cricket teams and 16 football teams competing for the coveted Champion Shield and cash rewards.',
            'highlights': '• State-of-the-art turf ground with floodlights\n• Live score streaming on LED screens\n• Professional referees & tournament trophies',
            'image': 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=7),
            'start_time': '04:00 PM',
            'end_time': '10:00 PM',
            'venue': 'Decathlon Arena Sports Complex',
            'address': 'Survey 88, Sohna Road',
            'city': 'Delhi',
            'featured': False,
            'tickets': [
                {'name': 'Spectator Pass', 'price': 99.0, 'capacity': 200, 'desc': 'Grandstand spectator seat + complimentary drink.'},
                {'name': 'Team Entry (Cricket - 8 players)', 'price': 1999.0, 'capacity': 32, 'desc': 'Full team registration, official jerseys and balls.'},
                {'name': 'Team Entry (Football - 6 players)', 'price': 1599.0, 'capacity': 16, 'desc': 'Football team registration and match kit.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['seminars'],
            'title': 'GenAI in Production: LLMs, RAG & Agents Seminar',
            'description': 'Learn how modern enterprises are deploying Large Language Models with Retrieval-Augmented Generation (RAG), vector databases, evaluation pipelines, and autonomous agentic workflows.',
            'highlights': '• Live walkthrough of production LangChain & LlamaIndex systems\n• Vector DB optimization masterclass\n• Q&A with Senior AI Researchers',
            'image': 'https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=4),
            'start_time': '02:00 PM',
            'end_time': '06:00 PM',
            'venue': 'IndiQube Emerald Innovation Hub',
            'address': 'Outer Ring Road, Bellandur',
            'city': 'Bengaluru',
            'featured': False,
            'tickets': [
                {'name': 'Student Attendee', 'price': 299.0, 'capacity': 80, 'desc': 'Discounted pass for college students.'},
                {'name': 'Professional Pass', 'price': 699.0, 'capacity': 120, 'desc': 'Access to slide decks, recordings and notes.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['networking'],
            'title': 'Founders & Angels: Startup Pitch & Mixer',
            'description': 'An exclusive curated evening connecting 40 high-growth seed and Series-A startups with top Angel Investors, Venture Capitalists, and Incubator Directors.',
            'highlights': '• 10 Curated 3-minute lightning pitches\n• 1-on-1 Speed networking tables\n• Cocktail reception & investor directory access',
            'image': 'https://images.unsplash.com/photo-1515187029135-18ee286d815b?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=10),
            'start_time': '05:30 PM',
            'end_time': '09:30 PM',
            'venue': 'The Lalit Great Eastern',
            'address': '1, 2 & 3 Old Court House Street',
            'city': 'Kolkata',
            'featured': False,
            'tickets': [
                {'name': 'Founder Pass', 'price': 1299.0, 'capacity': 40, 'desc': 'Entry for 1 founder with pitching opportunity.'},
                {'name': 'General Ecosystem Pass', 'price': 899.0, 'capacity': 60, 'desc': 'Entry for operators, mentors and enthusiasts.'}
            ]
        },
        {
            'organizer': demo_organizer_2,
            'category': category_map['cultural'],
            'title': 'Laughter Therapy: All-Star Standup Comedy Night',
            'description': 'Get ready for an evening of non-stop laughter featuring 5 of the finest standup comedians in the country performing fresh, hilarious sets on college life, tech jobs, and Indian culture.',
            'highlights': '• 120 minutes of rib-tickling humor\n• Air-conditioned auditorium with cozy seating\n• Meet the comedians post-show',
            'image': 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=6),
            'start_time': '07:30 PM',
            'end_time': '09:45 PM',
            'venue': 'Bhaidas Auditorium',
            'address': 'Gulmohar Road, JVPD Scheme, Vile Parle',
            'city': 'Mumbai',
            'featured': False,
            'tickets': [
                {'name': 'Balcony Pass', 'price': 349.0, 'capacity': 120, 'desc': 'Upper tier seating with great acoustic view.'},
                {'name': 'Prime Stall', 'price': 599.0, 'capacity': 180, 'desc': 'Mid-hall prime view seats.'},
                {'name': 'Front Rows VIP', 'price': 899.0, 'capacity': 40, 'desc': 'First 3 rows with comedian crowd interaction zone.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['exhibitions'],
            'title': 'KalaDrishti: Contemporary Art & Photography Expo',
            'description': 'Showcasing over 200 breathtaking curated artworks, digital installations, and documentary photography collections from celebrated and upcoming visual artists.',
            'highlights': '• Guided gallery walks with curators\n• Interactive live painting stations\n• Art prints available for purchase',
            'image': 'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=14),
            'start_time': '11:00 AM',
            'end_time': '08:00 PM',
            'venue': 'India Habitat Centre, Visual Arts Gallery',
            'address': 'Lodhi Road',
            'city': 'Delhi',
            'featured': False,
            'tickets': [
                {'name': 'General Gallery Walk', 'price': 150.0, 'capacity': 300, 'desc': 'Single day entry to all visual art wings.'},
                {'name': 'Artist Workshop + Entry', 'price': 650.0, 'capacity': 40, 'desc': 'Includes 2hr water-color & portrait workshop.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['workshops'],
            'title': 'UI/UX Design Thinking & Figma Systems Bootcamp',
            'description': 'Master modern product design from wireframing to interactive prototypes, design tokens, auto-layout, and developer handoff using Figma. Build a complete mobile app case study.',
            'highlights': '• Free Figma UI Kit and component library\n• Portfolio critique from Senior Product Designers\n• Hands-on design sprint challenge',
            'image': 'https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=9),
            'start_time': '10:00 AM',
            'end_time': '05:00 PM',
            'venue': 'DesignHub Innovation Lab',
            'address': 'Koramangala 4th Block',
            'city': 'Bengaluru',
            'featured': False,
            'tickets': [
                {'name': 'Standard Pass', 'price': 599.0, 'capacity': 75, 'desc': 'Entry, design assets pack, and certificate.'},
                {'name': 'Portfolio Review Pass', 'price': 1099.0, 'capacity': 20, 'desc': 'Detailed 1-on-1 portfolio feedback session.'}
            ]
        },
        {
            'organizer': demo_organizer_2,
            'category': category_map['college-events'],
            'title': 'National Career Conclave & Campus Placement Fair',
            'description': 'Connect with 45+ leading MNCs, startups, and consulting firms hiring for software engineering, analytics, marketing, and finance roles. Resume reviews and mock interviews on spot.',
            'highlights': '• Direct interview rounds with hiring managers\n• Free ATS resume screening desk\n• Keynote on breaking into tech in 2026',
            'image': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=11),
            'start_time': '09:30 AM',
            'end_time': '05:30 PM',
            'venue': 'Anna University Convention Center',
            'address': 'Sardar Patel Road, Guindy',
            'city': 'Chennai',
            'featured': False,
            'tickets': [
                {'name': 'Job Seeker Pass', 'price': 0.0, 'capacity': 400, 'desc': 'Free registration for final-year students & fresh grads.'},
                {'name': 'Priority Fast-Track Pass', 'price': 299.0, 'capacity': 100, 'desc': 'Skip waiting lines for top 5 hiring stalls.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['sports'],
            'title': 'Urban Night Marathon 10K & 5K Run',
            'description': 'Experience the thrill of running under city lights with cheering zones, live DJ stations along the course, RFID timing bibs, and commemorative finisher medals.',
            'highlights': '• Official timing chip & dry-fit running jersey\n• Hydration and energy gel stations every 1.5 km\n• Post-run breakfast and celebration concert',
            'image': 'https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=16),
            'start_time': '08:00 PM',
            'end_time': '11:30 PM',
            'venue': 'Sabarmati Riverfront Promenade',
            'address': 'Near Event Ground, West Bank',
            'city': 'Ahmedabad',
            'featured': False,
            'tickets': [
                {'name': '5K Fun Run Pass', 'price': 399.0, 'capacity': 250, 'desc': 'Includes bib, finisher medal and refreshments.'},
                {'name': '10K Timed Challenge', 'price': 699.0, 'capacity': 200, 'desc': 'Official chip-timed run, tech T-shirt and certificate.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['workshops'],
            'title': 'Autonomous Robotics & IoT Hands-on Workshop',
            'description': 'Build your own self-balancing robot and smart IoT device using ESP32, sensors, and motor drivers. Complete hardware kit provided for every participant to take home.',
            'highlights': '• Complete IoT hardware development kit included\n• Firmware programming in C++ & MicroPython\n• Take home your working robot model',
            'image': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=18),
            'start_time': '09:30 AM',
            'end_time': '05:00 PM',
            'venue': 'IIT Madras Research Park',
            'address': 'Kanagam Road, Taramani',
            'city': 'Chennai',
            'featured': False,
            'tickets': [
                {'name': 'Solo Maker Pass (Includes Kit)', 'price': 1899.0, 'capacity': 45, 'desc': 'Full workshop pass with complete take-home robot kit.'},
                {'name': 'Duo Team Pass (1 Shared Kit)', 'price': 2499.0, 'capacity': 20, 'desc': 'Entry for 2 participants sharing 1 kit.'}
            ]
        },
        {
            'organizer': demo_organizer_2,
            'category': category_map['cultural'],
            'title': 'Flavors of India: Street Food & Culture Carnival',
            'description': 'A 2-day celebration of India’s incredible culinary heritage. 60+ authentic regional food stalls from 18 states, live folk performances, spice bazaars, and chef masterclasses.',
            'highlights': '• 60+ curated food stalls from Kashmir to Kerala\n• Live folk music & dance performances\n• Celebrity chef live cook-off challenge',
            'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=20),
            'start_time': '12:00 PM',
            'end_time': '10:00 PM',
            'venue': 'Major Dhyan Chand National Stadium',
            'address': 'India Gate Circle',
            'city': 'Delhi',
            'featured': False,
            'tickets': [
                {'name': 'Day Entry Pass', 'price': 149.0, 'capacity': 500, 'desc': 'Entry to food carnival and cultural arena.'},
                {'name': 'Foodie Tasting Passport', 'price': 699.0, 'capacity': 150, 'desc': 'Entry + 6 complimentary tasting coupons for premium stalls.'}
            ]
        },
        {
            'organizer': demo_organizer,
            'category': category_map['conferences'],
            'title': 'NextGen Fintech & Blockchain Symposium',
            'description': 'Navigating the next decade of digital payments, Open Banking APIs, Central Bank Digital Currencies (CBDC), algorithmic risk, and decentralized finance regulations.',
            'highlights': '• Keynote from RBI & Fintech policy leaders\n• Case studies on UPI international expansion\n• Networking cocktails at the rooftop terrace',
            'image': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200&auto=format&fit=crop&q=80',
            'date': today + timedelta(days=22),
            'start_time': '09:00 AM',
            'end_time': '05:30 PM',
            'venue': 'The St. Regis Mumbai',
            'address': '462, Senapati Bapat Marg, Lower Parel',
            'city': 'Mumbai',
            'featured': False,
            'tickets': [
                {'name': 'Conference Pass', 'price': 1899.0, 'capacity': 120, 'desc': 'Access to all keynote stages and luncheon.'},
                {'name': 'VIP Executive Pass', 'price': 3499.0, 'capacity': 30, 'desc': 'Private dining table and investor roundtables.'}
            ]
        }
    ]

    created_events = []
    for ed in events_data:
        tickets_list = ed.pop('tickets')
        event = Event(**ed)
        db.session.add(event)
        db.session.flush()

        for t_info in tickets_list:
            tt = TicketType(
                event_id=event.id,
                name=t_info['name'],
                price=t_info['price'],
                capacity=t_info['capacity'],
                available_quantity=t_info['capacity'] - (5 if t_info['capacity'] > 20 else 0), # slight simulated usage
                description=t_info.get('desc', '')
            )
            db.session.add(tt)

        created_events.append(event)

    db.session.commit()
    print(f"[OK] Created {len(created_events)} events with multiple ticket tiers.")

    # 4. Create Sample Bookings for Demo Attendee so My Bookings & Dashboard are rich
    first_event = created_events[0]
    first_ticket = first_event.ticket_types[0]

    second_event = created_events[1]
    second_ticket = second_event.ticket_types[0]

    # Booking 1 - Confirmed Upcoming
    b1 = Booking(
        user_id=demo_attendee.id,
        event_id=first_event.id,
        total_amount=first_ticket.price * 2,
        status='confirmed',
        attendee_name=demo_attendee.name,
        attendee_email=demo_attendee.email,
        attendee_phone=demo_attendee.phone,
        booked_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(b1)
    db.session.flush()

    bi1 = BookingItem(
        booking_id=b1.id,
        ticket_type_id=first_ticket.id,
        ticket_name=first_ticket.name,
        quantity=2,
        unit_price=first_ticket.price,
        subtotal=first_ticket.price * 2
    )
    db.session.add(bi1)

    p1 = Payment(
        booking_id=b1.id,
        amount=b1.total_amount,
        payment_method='UPI',
        status='completed',
        paid_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(p1)

    # Booking 2 - For Priya Patel
    b2 = Booking(
        user_id=demo_attendee_2.id,
        event_id=second_event.id,
        total_amount=second_ticket.price * 1 + 25.0,
        status='confirmed',
        attendee_name=demo_attendee_2.name,
        attendee_email=demo_attendee_2.email,
        attendee_phone=demo_attendee_2.phone,
        booked_at=datetime.utcnow() - timedelta(hours=5)
    )
    db.session.add(b2)
    db.session.flush()

    bi2 = BookingItem(
        booking_id=b2.id,
        ticket_type_id=second_ticket.id,
        ticket_name=second_ticket.name,
        quantity=1,
        unit_price=second_ticket.price,
        subtotal=second_ticket.price
    )
    db.session.add(bi2)

    p2 = Payment(
        booking_id=b2.id,
        amount=b2.total_amount,
        payment_method='Credit/Debit Card',
        status='completed',
        paid_at=datetime.utcnow() - timedelta(hours=5)
    )
    db.session.add(p2)

    # Booking 3 - Completed/Cancelled sample
    third_event = created_events[2]
    third_ticket = third_event.ticket_types[0]

    b3 = Booking(
        user_id=demo_attendee.id,
        event_id=third_event.id,
        total_amount=third_ticket.price * 1,
        status='cancelled',
        attendee_name=demo_attendee.name,
        attendee_email=demo_attendee.email,
        attendee_phone=demo_attendee.phone,
        booked_at=datetime.utcnow() - timedelta(days=3)
    )
    db.session.add(b3)
    db.session.flush()

    bi3 = BookingItem(
        booking_id=b3.id,
        ticket_type_id=third_ticket.id,
        ticket_name=third_ticket.name,
        quantity=1,
        unit_price=third_ticket.price,
        subtotal=third_ticket.price
    )
    db.session.add(bi3)

    p3 = Payment(
        booking_id=b3.id,
        amount=b3.total_amount,
        payment_method='UPI',
        status='refunded',
        paid_at=datetime.utcnow() - timedelta(days=3)
    )
    db.session.add(p3)

    c3 = Cancellation(
        booking_id=b3.id,
        reason='Schedule clash with college examination',
        refund_amount=b3.total_amount,
        status='refunded',
        requested_at=datetime.utcnow() - timedelta(days=2),
        processed_at=datetime.utcnow() - timedelta(days=2)
    )
    db.session.add(c3)

    db.session.commit()
    print("[OK] Created Sample Bookings, Payments, and Cancellations.")
    print("==================================================")
    print("DEMO CREDENTIALS (DEVELOPMENT ONLY):")
    print("1. Attendee:  attendee@eventeasy.com  |  Attendee@123")
    print("2. Organizer: organizer@eventeasy.com |  Organizer@123")
    print("3. Admin:     admin@eventeasy.com     |  Admin@123")
    print("==================================================")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_database()
