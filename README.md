# 💅 Salon Pulse

A comprehensive business intelligence and management system for nail salons, built with Flask, SQLAlchemy, and modern analytics.

![CI/CD Pipeline](https://img.shields.io/github/actions/workflow/status/RoddyCodes/salon_pulse/ci-cd.yml?branch=main&label=CI%2FCD&logo=github)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue?logo=python)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

### Dashboard & Analytics

- **Staff Performance Tracking**: Revenue, tips, and job counts per technician
- **Customer Retention Alerts**: Identify at-risk customers (30+ days inactive)
- **Revenue Visualization**: Interactive charts with daily/monthly trends
- **Service Analysis**: Track which services drive revenue

### Customer Lifetime Value (LTV) Analytics

- **Smart Segmentation**: Automatically categorizes customers into:

  - 💎 **VIP**: High-value customers with recent activity
  - 🏆 **Champion**: Frequent, loyal customers
  - 🤝 **Loyal**: Consistent repeat customers
  - ⭐ **Promising**: New customers showing potential
  - ⚠️ **At-Risk**: Good customers who need attention
  - 🔔 **Needs Attention**: Infrequent visitors
  - 😔 **Lost**: Haven't visited in 60+ days

- **Comprehensive Metrics**:
  - Total lifetime spend
  - Visit frequency & trends
  - Average transaction value
  - Predicted 12-month LTV
  - Favorite services & technicians
  - Tip percentages

### Data Management

- Simple appointment entry form
- Auto-customer creation by phone number
- Realistic test data generator (90 days of history)

## 🚀 Quick Start

### Initial Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd salon_pulse

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m backend.models

# Generate practice data (90 days of realistic appointments)
python scripts/seed_data.py
```

### Run the Application

```bash
# Start Flask development server
python run.py

# Or use Make
make run

# Access at http://127.0.0.1:5000
```

## 🧪 Development & Testing

### Quick Commands with Make

```bash
# Install all dependencies
make install-dev

# Format code
make format

# Run linters
make lint

# Run tests
make test

# Run full CI pipeline locally
make ci

# See all commands
make help
```

## 📊 Usage

### Web Interface

Navigate through these pages:

1. **Dashboard** (`/`) - Staff performance and retention alerts
2. **📊 Analytics** (`/appointments`) - Revenue charts with filters
3. **💎 Customers** (`/customers`) - LTV analysis and segmentation
4. **New Appointment** (`/add`) - Quick data entry form

### CLI Tools

**Customer Analytics Report:**

```bash
python scripts/customer_report.py
```

Shows segment breakdown and top customers by LTV.

**Business Intelligence Report:**

```bash
python scripts/analyze.py
```

Terminal-based dashboard with staff performance.

**Reset Database:**

```bash
python scripts/seed_data.py
```

Drops all data and generates fresh practice dataset.

## 📁 Project Structure

```
salon_pulse/
├── run.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── backend/              # Flask application code
│   ├── __init__.py       # Package initialization
│   ├── models.py         # Database schema (SQLAlchemy)
│   ├── routes.py         # Flask routes and business logic
│   └── customer_analytics.py  # LTV calculation & segmentation
│
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navbar
│   ├── dashboard.html    # Main dashboard
│   ├── appointments.html # Analytics & charts
│   ├── customers.html    # Customer LTV page
│   └── add.html          # Appointment entry form
│
├── static/               # Static assets (CSS, JS, images)
│   ├── css/             # Custom stylesheets
│   └── js/              # Custom JavaScript
│
├── scripts/              # Utility scripts
│   ├── seed_data.py     # Test data generator
│   ├── analyze.py       # CLI reporting tool
│   └── customer_report.py  # Customer analytics CLI
│
├── docs/                 # Documentation
│   ├── AGENT_INSTRUCTIONS.md     # Project context for AI agents
│   └── copilot-instructions.md   # GitHub Copilot instructions
│
├── instance/             # Instance-specific files (auto-generated)
│   └── salon_data.db    # SQLite database
│
└── venv/                 # Python virtual environment (not in git)
```

## 🛠️ Technology Stack

- **Backend**: Flask, Flask-SQLAlchemy
- **Database**: SQLite (easily upgradable to PostgreSQL)
- **Frontend**: Jinja2, Bootstrap 5.3, Chart.js
- **Analytics**: Python (NumPy/Pandas-free for simplicity)
- **Testing**: Pytest, Coverage
- **Code Quality**: Black, isort, Flake8, Pylint
- **Security**: Bandit, Safety
- **CI/CD**: GitHub Actions

## 🔄 CI/CD Pipeline

This project includes a professional CI/CD pipeline with:

- ✅ **Code Quality**: Black, isort, Flake8, Pylint
- ✅ **Security Scanning**: Bandit, Safety
- ✅ **Testing**: Pytest across Python 3.11, 3.12, 3.13
- ✅ **Coverage Reports**: Automated code coverage tracking
- ✅ **Build Validation**: Application startup and CLI tool testing
- ✅ **Deployment**: Automated deployment to production (configurable)

See [CI/CD Documentation](docs/CI_CD_PIPELINE.md) for details.

### Running CI Locally

```bash
# Run full CI pipeline
make ci

# Or individual steps
make format  # Format code
make lint    # Run linters
make test    # Run tests
```

## 📈 Customer Segmentation Logic

### Segment Thresholds

- **High Spend**: $300+ lifetime value
- **Frequent Visits**: 5+ appointments
- **Regular Frequency**: Every 28 days or less
- **At-Risk Threshold**: 45 days since last visit
- **Lost Threshold**: 60+ days since last visit

### Segment Definitions

| Segment         | Criteria                         |
| --------------- | -------------------------------- |
| VIP             | High spend + recent activity     |
| Champion        | Frequent visits + loyal + recent |
| Loyal           | Consistent visits over time      |
| Promising       | New (1-3 visits) but engaged     |
| At-Risk         | Was good but overdue             |
| Needs Attention | Infrequent or low engagement     |
| Lost            | No visits in 60+ days            |

## 🔮 Future Enhancements

- [ ] Churn prediction ML model
- [ ] Revenue forecasting (time series)
- [ ] Automated SMS/email retention campaigns
- [ ] Service recommendation engine
- [ ] Staff scheduling optimization
- [ ] Mobile app for technicians
- [ ] Customer self-booking portal

## 🤝 Contributing

This is a personal project for a family-owned salon, but suggestions and improvements are welcome!

## 📝 License

MIT License - See LICENSE file for details

## 📞 Contact

Built with ❤️ for real-world salon operations
