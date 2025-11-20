Project Context: SalonPulse

1. Project Mission

We are building "SalonPulse," a business intelligence and management tool for a family-owned nail salon.
Goal: Move the business from pen-and-paper/Excel to a data-driven Python application.
Key Objectives:

Track revenue by technician and service type.

Identify "At-Risk" customers (retention tracking).

Visualize business trends (Daily/Monthly revenue).

Simple, mobile-friendly interface for the owner to enter data.

2. Tech Stack & Environment

Language: Python 3.13

Backend Framework: Flask

Database: SQLite (via Flask-SQLAlchemy ORM)

Frontend: HTML5, Jinja2 Templates, Bootstrap 5.3 (CSS), Chart.js (Visualization)

Version Control: Git/GitHub

3. File Architecture

models.py: Contains the SQLAlchemy DB models (Technician, Service, Customer, Appointment).

app.py: The main Flask application. Handles routing, data aggregation, and logic.

customer_analytics.py: Customer Lifetime Value (LTV) analysis module with segmentation logic.

seed_data.py: A utility script to drop the database and repopulate it with dummy test data.

analyze.py: A CLI script for quick reporting (legacy, mostly replaced by the web dashboard).

templates/:

base.html: Global layout (Navbar, Bootstrap CDN, Flash messages).

dashboard.html: Main view showing Staff Performance table and Retention Alerts.

add.html: Form to manually input new appointments.

appointments.html: Analytics view with Chart.js visualizations and filtering options.

customers.html: Customer Lifetime Value dashboard with segmentation and rankings.

4. Database Schema (Mental Model)

The database is a Star-like schema centered on Appointment:

Technician: id, name, commission_rate

Service: id, name, base_price, category (e.g., Hands/Feet)

Customer: id, first_name, phone, notes

Appointment:

Links to Technician, Service, Customer.

Stores financial facts: price_charged, tip_amount, date_time, payment_method.

5. Current State & Features

Dashboard: Displays a leaderboard of technician revenue and a list of customers who haven't visited in 30+ days.

Data Entry: A /add route allows creating new appointments. It checks if a customer exists by phone number; if not, it creates a new customer record automatically.

Analytics Page (/appointments): - Contains 3 charts: Revenue Trend (Line), Revenue by Tech (Bar), Revenue by Service (Doughnut).

Contains a detailed data table of history.

Filtering: Users can filter by Time Period (Day/Month) and specific Technician via query parameters (e.g., ?period=month&tech_id=1).

Customer Analytics Page (/customers): - Calculates Customer Lifetime Value (LTV) metrics for all customers.

Segments customers into: VIP, Champion, Loyal, Promising, At-Risk, Needs Attention, Lost.

Displays comprehensive metrics: total spend, visit frequency, predicted 12-month LTV, favorite services.

Shows segment distribution and revenue breakdown via Chart.js visualizations.

6. Customer Segmentation Logic

The customer_analytics.py module classifies customers based on behavior:

VIP: High spend ($300+) + recent activity (within 28 days)

Champion: Frequent visits (5+) + loyal (every 28 days) + recent

Loyal: Consistent visits (5+ visits, reasonable frequency)

Promising: New customers (1-3 visits) showing good engagement

At-Risk: Good customers who haven't visited in 45-60 days

Needs Attention: Infrequent visitors or low engagement

Lost: No visits in 60+ days

LTV Calculations Include:

Total lifetime spend (revenue + tips)

Visit frequency (average days between visits)

Visit trend (increasing, stable, or decreasing frequency)

Predicted 12-month value (based on current visit frequency and avg transaction)

Favorite services and preferred technician

7. Coding Conventions & "Gotchas"

Chart.js Integration: When passing data to Chart.js in templates/appointments.html, we calculate the lists (labels/values) in app.py first. We MUST use | tojson | safe in the Jinja template to prevent JavaScript syntax errors.

Date Handling: We use Python's datetime object. For charts, we format dates as strings (YYYY-MM-DD) in the backend before passing them to the frontend.

Styling: Use Bootstrap 5 utility classes (e.g., card, shadow, row, col-md-6) for all layout. Keep it responsive.

8. Immediate Roadmap

Customer analytics enhancement: Add date range filters, export customer lists, automated retention campaigns.

Next steps may include: Date range pickers for all pages, editing existing appointments, or authentication (login).
