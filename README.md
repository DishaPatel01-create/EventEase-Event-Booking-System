# 🎟️ EventEasy - Full-Stack Event Booking & Discovery Platform

> A modern, commercial-grade, full-stack Event Booking and Ticketing System built with Python, Flask, SQLAlchemy, PostgreSQL, and Bootstrap 5.

---

## 📖 1. Project Overview
**EventEasy** is a full-featured event discovery, registration, and ticketing platform. It empowers attendees to discover, search, filter, and book passes for **College Events, Technical Workshops, Hackathons, Industry Conferences, Concerts, Sports Leagues, Cultural Fests, Seminars, and Exhibitions** across major Indian cities. 

It provides organizers with end-to-end event management, dynamic multi-tier ticketing (General, Early Bird, VIP, Student), real-time sales dashboards, and anti-overbooking inventory protection.

---

## 🎯 2. Problem Statement
Traditional event ticketing platforms often suffer from:
* Cluttered, movie-centric interfaces unsuited for general academic/industry events.
* Concurrency race conditions resulting in ticket overbooking.
* Rigid ticketing tiers with lack of role-based permissions for student organizers vs. attendees.
* Lack of instant digital ticketing and automated simulated refund processing on cancellation.

**EventEasy** solves these challenges by providing a dedicated, commercial-grade event platform with row-level transaction safety, instant pass generation, role-verified authentication, and analytics dashboards.

---

## 🚀 3. Key Features

### For Attendees
* **Explore & Discovery:** Multi-criteria filtering (Category, City, Date Presets, Custom Date, Price Tiers, Availability status) with instant debounced AJAX search.
* **Event Details & Live Pricing:** Detailed schedules, highlights, venue maps, and real-time subtotal calculators.
* **Anti-Overbooking Ticketing:** Atomic inventory decrement within database transactions to prevent overselling.
* **Simulated Checkout & Payment:** Interactive gateway supporting UPI (Google Pay, PhonePe, BHIM), Credit/Debit Cards, and Net Banking.
* **Instant Digital Ticket:** Digital entry pass featuring booking reference numbers, attendee details, ticket tier breakdown, and scalable QR matrix visuals ready for print/download.
* **My Bookings Dashboard:** Organized tabs for *Upcoming*, *Completed*, and *Cancelled* bookings with self-service 100% refund processing.

### For Organizers
* **Organizer Portal:** Overview of Total Events, Upcoming Events, Tickets Sold, and Gross Revenue (₹).
* **Interactive Analytics:** Category distribution charts and booking volume trends powered by Chart.js.
* **Event Creation & Dynamic Tiers:** Create rich events with custom ticket categories (e.g. VIP, Student Pass, Early Bird) with custom prices and capacities.
* **Attendee Roster:** View full attendee rosters and ticket breakdowns per event with instant print/export capability.
* **Publishing Control:** Toggle event status between *Published*, *Draft*, and *Cancelled*.

### For Platform Administrators
* **Super Admin Console:** Platform metrics, gross volume oversight, user role administration, and content moderation.

---

## 🛠️ 4. Technology Stack

* **Backend:** Python 3.12+ / 3.14, Flask
* **Database & ORM:** PostgreSQL / SQLite (automatic fallback), SQLAlchemy, Flask-SQLAlchemy
* **Authentication:** Flask-Login, Werkzeug Password Hashing (`scrypt` / `pbkdf2`), Role-Verified Login
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Jinja2 Templates
* **Icons & UI:** Font Awesome 6, SVG vector graphics
* **Charts & Analytics:** Chart.js
* **Environment:** python-dotenv

---

## 📁 5. Folder Structure

```
EventBooking System/
├── app.py                     # Flask Application Factory & Server Entrypoint
├── config.py                  # Environment-specific configuration
├── requirements.txt           # Python library dependencies
├── test_app.py                # Automated Test Suite (Unit & End-to-End)
├── README.md                  # Comprehensive documentation
├── .env                       # Local environment variables
├── .env.example               # Template environment configuration
│
├── models/                    # SQLAlchemy Database Models
│   ├── __init__.py            # DB instance & model exports
│   ├── user.py                # User model with Flask-Login & role checks
│   ├── category.py            # Event categories & badge themes
│   ├── event.py               # Events with dates, venues, status & pricing
│   ├── ticket.py              # Multi-tier ticket types & inventory
│   ├── booking.py             # Bookings & individual BookingItems
│   ├── payment.py             # Simulated payment records & references
│   └── cancellation.py        # Refund requests & cancellation logs
│
├── routes/                    # Flask Blueprints & Role Decorators
│   ├── __init__.py            # @organizer_required, @admin_required decorators
│   ├── auth.py                # Role-verified Login, Register, Logout, Profile
│   ├── home.py                # Homepage, Hero, Featured & Upcoming feeds
│   ├── events.py              # Explore page, AJAX filters & Details
│   ├── booking.py             # Checkout, Anti-Overbooking transaction, Tickets & Refunds
│   ├── organizer.py           # Organizer dashboard, Event creation & Rosters
│   └── admin.py               # Super Admin control panel
│
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html              # Master layout with Navbar & Toasts
│   ├── index.html             # Homepage
│   ├── events.html            # Explore events with multi-condition filters
│   ├── event_details.html     # Event details & live ticket selector
│   ├── checkout.html          # Checkout & simulated payment methods
│   ├── booking_confirmation.html # Success celebration page
│   ├── ticket.html            # Digital Ticket with QR visual & Print styling
│   ├── bookings.html          # My Bookings user dashboard
│   ├── login.html             # Sign in with Account Type selector (Attendee / Organizer / Admin)
│   ├── register.html          # Registration with Attendee/Organizer role cards
│   ├── profile.html           # User profile settings
│   ├── organizer_dashboard.html # Organizer metrics & Chart.js visualizer
│   ├── create_event.html      # Create event with dynamic ticket tiers
│   ├── edit_event.html        # Edit event details & ticket capacities
│   ├── organizer_bookings.html# Event attendee roster
│   ├── admin_dashboard.html   # Platform-wide administration console
│   └── errors/
│       ├── 403.html           # Access Denied
│       ├── 404.html           # Page Not Found
│       └── 500.html           # Internal Server Error
│
├── static/                    # Static Assets
│   ├── css/
│   │   ├── style.css          # Main design system & custom variables
│   │   └── responsive.css     # Mobile responsive adjustments
│   ├── js/
│   │   ├── main.js            # Toast notifications & UI helpers
│   │   ├── filters.js         # Live AJAX filtering & debounced search
│   │   ├── booking.js         # Quantity selector & live pricing calculator
│   │   └── dashboard.js       # Stats counter & dynamic ticket repeater
│   └── images/
│       ├── logo.svg           # Scalable EventEasy brand logo
│       └── favicon.svg        # Brand browser icon
│
└── database/
    ├── __init__.py
    └── seed.py                # 16+ rich realistic events, categories & demo users
```

---

## 🔐 6. Demo Accounts & Credentials (Development & Viva)

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Attendee** | `attendee@eventeasy.com` | `Attendee@123` | Browse, Search, Book tickets, View digital tickets, Request refunds |
| **Organizer** | `organizer@eventeasy.com` | `Organizer@123` | Host events, Manage ticket tiers, View live rosters & revenue |
| **Admin** | `admin@eventeasy.com` | `Admin@123` | Manage users, Change roles, Delete events, Platform overview |

---

## ⚡ 7. Installation & Setup

### Prerequisites
* Python 3.10+ installed
* PostgreSQL (Optional — SQLite fallback works out of the box)

### 1. Clone & Enter Directory
```bash
git clone <repo-url>
cd "EventBooking System"
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

*(Optional) For PostgreSQL setup, edit `DATABASE_URL` in `.env`:*
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/eventeasy_db
```

### 4. Seed Sample Database (16+ Events & Demo Accounts)
```bash
python database/seed.py
```

### 5. Start the Server
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:5000`**.

---

## 🧪 8. Running Automated Tests
Run the comprehensive test suite:
```bash
python test_app.py
```
