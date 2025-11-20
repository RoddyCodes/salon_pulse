# Salon Pulse - AI Coding Agent Instructions

## Project Overview

Salon Pulse is a Flask-based salon management system tracking appointments, revenue, technician performance, and customer retention. Uses SQLite with SQLAlchemy ORM.

## Architecture & Data Flow

### Core Structure (3-Layer Pattern)

- **`models.py`**: Database schema definitions (Technician, Service, Customer, Appointment)
- **`app.py`**: Flask routes and business logic (dashboard, appointments, add)
- **`templates/`**: Jinja2 templates with Bootstrap 5 + Chart.js

### Data Model Relationships

```
Appointment (central ledger)
  ├─→ customer_id → Customer (phone is unique identifier)
  ├─→ technician_id → Technician (has commission_rate)
  └─→ service_id → Service (has base_price)
```

**Critical**: Appointments store actual `price_charged` (not Service.base_price) + `tip_amount` to track real transaction values.

### Key Business Logic Patterns

**Customer Auto-Creation**: In `/add` route, customers are fetched by phone or created on-the-fly:

```python
customer = Customer.query.filter_by(phone=c_phone).first()
if not customer:
    customer = Customer(first_name=c_name, phone=c_phone)
    db.session.add(customer)
    db.session.commit()
```

**Retention Alerts**: Dashboard identifies at-risk customers by finding those whose last appointment is >30 days old (in-memory iteration pattern, not SQL-filtered).

**Chart Data Aggregation**: The `/appointments` route aggregates revenue by date using dictionary accumulation:

```python
for appt in history:
    date_str = appt.date_time.strftime('%Y-%m-%d')
    total_money = appt.price_charged + appt.tip_amount
    daily_data[date_str] = daily_data.get(date_str, 0) + total_money
```

## Development Workflows

### Initial Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database with schema
python models.py

# Populate test data
python seed_data.py
```

### Running the Application

```bash
# Start Flask dev server (debug mode enabled in app.py)
python app.py
# Access at http://127.0.0.1:5000
```

### Database Management

- **SQLite file**: `instance/salon_data.db` (auto-created)
- **Reset data**: Run `seed_data.py` (drops all tables via `db.drop_all()`)
- **CLI reports**: Run `analyze.py` for terminal-based performance dashboard

## Project Conventions

### Naming & Structure

- **Routes return templates**: Always use `render_template()`, never JSON APIs
- **Flash messages**: Use Flask's `flash()` for user feedback (e.g., "✅ Appointment Saved Successfully!")
- **Redirect pattern**: POST requests redirect to GET routes (e.g., `/add` POST → `/appointments`)
- **Template inheritance**: All templates extend `base.html` which includes Bootstrap navbar

### Date/Time Handling

- Use `datetime.now()` for new appointments (not `datetime.utcnow()` despite model default)
- Display format: `strftime('%Y-%m-%d %H:%M')` for appointment tables
- Retention window: 30 days calculated via `datetime.now() - timedelta(days=30)`

### Financial Calculations

- Always sum `price_charged + tip_amount` for total revenue
- Commission rates stored per technician (default 0.60 = 60%)
- Payment method stored but not used in calculations yet

## Template Data Expectations

### Dashboard (`dashboard.html`)

- `performance`: List of tuples `(name, total_jobs, total_revenue, total_tips)`
- `at_risk`: List of dicts with keys `name`, `phone`, `days_missed`

### Appointments (`appointments.html`)

**Current implementation (app.py line 39-62)**:

- `history`: All Appointment objects sorted newest first
- `labels`: Sorted list of date strings (YYYY-MM-DD)
- `values`: Revenue totals matching labels

**Template expects but not yet implemented**:

- `selected_period`, `selected_tech`, `all_techs` (for filter controls)
- `trend_labels`, `trend_values`, `tech_labels`, `tech_values`, `service_labels`, `service_values` (for Chart.js)

### Add Form (`add.html`)

- `technicians`: All Technician objects
- `services`: All Service objects

## Common Pitfalls & Gotchas

1. **Missing Flask secret key**: `app.config['SECRET_KEY']` must be set in `app.py` for flash messages to work
2. **Database not initialized**: Run `python models.py` before first app start
3. **Template/route mismatch**: `appointments.html` references variables not provided by current `/appointments` route (needs update for filters/charts)
4. **Customer uniqueness**: Phone numbers are unique constraint—duplicate phone entries will fail
5. **Relationship access**: Use backref names: `appt.customer.first_name`, `appt.technician.name`, `appt.service.name`

## File Purpose Reference

- **`models.py`**: Schema only, no routes (imports Flask, SQLAlchemy, datetime)
- **`app.py`**: Application entry point with routes (imports from models.py)
- **`seed_data.py`**: Test data generator (clears DB each run)
- **`analyze.py`**: CLI reporting tool (mirrors dashboard logic for terminal use)
- **`requirements.txt`**: Minimal dependencies (Flask, Flask-SQLAlchemy)
