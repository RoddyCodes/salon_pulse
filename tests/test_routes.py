"""
Integration tests for Flask routes.
"""

from datetime import datetime, timedelta

import pytest

from backend.models import Appointment, Customer, Service, Technician


class TestDashboardRoute:
    """Tests for dashboard route."""

    def test_dashboard_loads(self, client, db_session):
        """Test that dashboard page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Salon Pulse" in response.data

    def test_dashboard_with_data(self, client, sample_appointment):
        """Test dashboard with appointment data."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Test Tech" in response.data

    def test_dashboard_at_risk_customers(
        self, client, db_session, sample_customer, sample_technician, sample_service
    ):
        """Test dashboard shows at-risk customers."""
        from datetime import datetime, timedelta

        from backend.models import Appointment, db

        # Create an old appointment (45 days ago)
        old_appt = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=45),
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Card",
        )
        db.session.add(old_appt)
        db.session.commit()

        response = client.get("/")
        assert response.status_code == 200
        assert b"Retention Alerts" in response.data


class TestAppointmentsRoute:
    """Tests for appointments/analytics route."""

    def test_appointments_page_loads(self, client, db_session):
        """Test that appointments page loads."""
        response = client.get("/appointments")
        assert response.status_code == 200

    def test_appointments_filter_by_period(self, client, sample_appointment):
        """Test filtering by time period."""
        # Test daily view
        response = client.get("/appointments?period=day")
        assert response.status_code == 200

        # Test monthly view
        response = client.get("/appointments?period=month")
        assert response.status_code == 200

    def test_appointments_filter_by_technician(self, client, sample_appointment, sample_technician):
        """Test filtering by technician."""
        response = client.get(f"/appointments?tech_id={sample_technician.id}")
        assert response.status_code == 200


class TestCustomersRoute:
    """Tests for customer analytics route."""

    def test_customers_page_loads(self, client, db_session):
        """Test that customers page loads."""
        response = client.get("/customers")
        assert response.status_code == 200

    def test_customers_with_data(self, client, sample_appointment):
        """Test customers page with data."""
        response = client.get("/customers")
        assert response.status_code == 200
        assert b"Test Customer" in response.data


class TestAddAppointmentRoute:
    """Tests for add appointment route."""

    def test_add_form_loads(self, client, db_session, sample_technician, sample_service):
        """Test that add form loads."""
        response = client.get("/add")
        assert response.status_code == 200
        assert b"New Appointment" in response.data

    def test_add_new_appointment(self, client, db_session, sample_technician, sample_service):
        """Test creating a new appointment."""
        data = {
            "technician_id": sample_technician.id,
            "service_id": sample_service.id,
            "customer_name": "New Customer",
            "customer_phone": "555-9999",
            "price": "35.00",
            "tip": "5.00",
        }

        response = client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Verify customer was created
        customer = Customer.query.filter_by(phone="555-9999").first()
        assert customer is not None
        assert customer.first_name == "New Customer"

    def test_add_appointment_existing_customer(
        self, client, db_session, sample_technician, sample_service, sample_customer
    ):
        """Test creating appointment for existing customer."""
        data = {
            "technician_id": sample_technician.id,
            "service_id": sample_service.id,
            "customer_name": "Test Customer",
            "customer_phone": sample_customer.phone,
            "price": "45.00",
            "tip": "7.00",
        }

        response = client.post("/add", data=data, follow_redirects=True)
        assert response.status_code == 200

        # Verify no duplicate customer was created
        customers = Customer.query.filter_by(phone=sample_customer.phone).all()
        assert len(customers) == 1
