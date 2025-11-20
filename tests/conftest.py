"""
Test configuration and fixtures for Salon Pulse tests.
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

# Import routes to register them with the app
from backend import routes  # noqa: F401
from backend.models import Appointment, Customer, Service, Technician, app, db


@pytest.fixture(scope="session")
def test_app():
    """Create application for testing."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture(scope="function")
def db_session(test_app):
    """Create a database session for tests."""
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_technician(db_session):
    """Create a sample technician."""
    tech = Technician(name="Test Tech", commission_rate=0.60)
    db_session.session.add(tech)
    db_session.session.commit()
    return tech


@pytest.fixture
def sample_service(db_session):
    """Create a sample service."""
    service = Service(name="Test Manicure", base_price=35.00, category="Hands")
    db_session.session.add(service)
    db_session.session.commit()
    return service


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer."""
    customer = Customer(first_name="Test Customer", phone="555-0000", notes="Test notes")
    db_session.session.add(customer)
    db_session.session.commit()
    return customer


@pytest.fixture
def sample_appointment(db_session, sample_technician, sample_service, sample_customer):
    """Create a sample appointment."""
    appointment = Appointment(
        date_time=datetime.now(),
        customer_id=sample_customer.id,
        technician_id=sample_technician.id,
        service_id=sample_service.id,
        price_charged=35.00,
        tip_amount=5.00,
        payment_method="Card",
    )
    db_session.session.add(appointment)
    db_session.session.commit()
    return appointment
