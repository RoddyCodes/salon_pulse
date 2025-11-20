"""
Unit tests for database models.
"""

from datetime import datetime

import pytest

from backend.models import Appointment, Customer, Service, Technician


class TestTechnicianModel:
    """Tests for Technician model."""

    def test_create_technician(self, db_session):
        """Test creating a technician."""
        tech = Technician(name="Lisa", commission_rate=0.65)
        db_session.session.add(tech)
        db_session.session.commit()

        assert tech.id is not None
        assert tech.name == "Lisa"
        assert tech.commission_rate == 0.65

    def test_technician_default_commission(self, db_session):
        """Test default commission rate."""
        tech = Technician(name="Tom")
        db_session.session.add(tech)
        db_session.session.commit()

        assert tech.commission_rate == 0.60


class TestServiceModel:
    """Tests for Service model."""

    def test_create_service(self, db_session):
        """Test creating a service."""
        service = Service(name="Gel Manicure", base_price=35.00, category="Hands")
        db_session.session.add(service)
        db_session.session.commit()

        assert service.id is not None
        assert service.name == "Gel Manicure"
        assert service.base_price == 35.00
        assert service.category == "Hands"


class TestCustomerModel:
    """Tests for Customer model."""

    def test_create_customer(self, db_session):
        """Test creating a customer."""
        customer = Customer(first_name="Sarah", phone="555-1234", notes="VIP customer")
        db_session.session.add(customer)
        db_session.session.commit()

        assert customer.id is not None
        assert customer.first_name == "Sarah"
        assert customer.phone == "555-1234"
        assert customer.notes == "VIP customer"

    def test_customer_phone_unique(self, db_session):
        """Test that phone numbers are unique."""
        customer1 = Customer(first_name="Sarah", phone="555-1234")
        db_session.session.add(customer1)
        db_session.session.commit()

        customer2 = Customer(first_name="Jenny", phone="555-1234")
        db_session.session.add(customer2)

        with pytest.raises(Exception):  # SQLAlchemy IntegrityError
            db_session.session.commit()


class TestAppointmentModel:
    """Tests for Appointment model."""

    def test_create_appointment(self, sample_appointment):
        """Test creating an appointment."""
        assert sample_appointment.id is not None
        assert sample_appointment.price_charged == 35.00
        assert sample_appointment.tip_amount == 5.00
        assert sample_appointment.payment_method == "Card"

    def test_appointment_relationships(
        self, sample_appointment, sample_customer, sample_technician, sample_service
    ):
        """Test appointment relationships."""
        assert sample_appointment.customer.id == sample_customer.id
        assert sample_appointment.technician.id == sample_technician.id
        assert sample_appointment.service.id == sample_service.id

    def test_appointment_total_value(self, sample_appointment):
        """Test calculating total value."""
        total = sample_appointment.price_charged + sample_appointment.tip_amount
        assert total == 40.00
