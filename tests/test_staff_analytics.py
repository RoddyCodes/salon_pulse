"""Tests for staff performance analytics module."""

from datetime import datetime, timedelta

import pytest

from backend.models import Appointment, Customer, Service, Technician, app, db
from backend.staff_analytics import (
    get_customer_retention_by_technician,
    get_staff_summary_stats,
    get_technician_performance,
    get_top_services_by_technician,
)


@pytest.fixture
def test_app():
    """Create test app with in-memory database."""
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_data(test_app):
    """Create sample test data for staff analytics."""
    with test_app.app_context():
        # Create technicians
        tech1 = Technician(name="Alice", commission_rate=0.60)
        tech2 = Technician(name="Bob", commission_rate=0.55)
        tech3 = Technician(name="Carol", commission_rate=0.65)
        db.session.add_all([tech1, tech2, tech3])

        # Create services
        service1 = Service(name="Manicure", base_price=30.0, category="Basic")
        service2 = Service(name="Pedicure", base_price=45.0, category="Basic")
        service3 = Service(name="Gel Nails", base_price=55.0, category="Premium")
        db.session.add_all([service1, service2, service3])

        # Create customers
        customer1 = Customer(first_name="Customer1", phone="555-0001")
        customer2 = Customer(first_name="Customer2", phone="555-0002")
        customer3 = Customer(first_name="Customer3", phone="555-0003")
        db.session.add_all([customer1, customer2, customer3])

        db.session.commit()

        # Create appointments - Alice (highest performer)
        now = datetime.now()
        appointments = [
            # Alice - 5 appointments, 3 customers, high revenue
            Appointment(
                date_time=now - timedelta(days=5),
                customer_id=customer1.id,
                technician_id=tech1.id,
                service_id=service3.id,
                price_charged=55.0,
                tip_amount=10.0,
            ),
            Appointment(
                date_time=now - timedelta(days=10),
                customer_id=customer1.id,
                technician_id=tech1.id,
                service_id=service3.id,
                price_charged=55.0,
                tip_amount=12.0,
            ),
            Appointment(
                date_time=now - timedelta(days=15),
                customer_id=customer2.id,
                technician_id=tech1.id,
                service_id=service2.id,
                price_charged=45.0,
                tip_amount=8.0,
            ),
            Appointment(
                date_time=now - timedelta(days=20),
                customer_id=customer2.id,
                technician_id=tech1.id,
                service_id=service3.id,
                price_charged=55.0,
                tip_amount=11.0,
            ),
            Appointment(
                date_time=now - timedelta(days=25),
                customer_id=customer3.id,
                technician_id=tech1.id,
                service_id=service1.id,
                price_charged=30.0,
                tip_amount=5.0,
            ),
            # Bob - 3 appointments, 2 customers, medium revenue
            Appointment(
                date_time=now - timedelta(days=8),
                customer_id=customer1.id,
                technician_id=tech2.id,
                service_id=service2.id,
                price_charged=45.0,
                tip_amount=7.0,
            ),
            Appointment(
                date_time=now - timedelta(days=12),
                customer_id=customer2.id,
                technician_id=tech2.id,
                service_id=service1.id,
                price_charged=30.0,
                tip_amount=5.0,
            ),
            Appointment(
                date_time=now - timedelta(days=18),
                customer_id=customer2.id,
                technician_id=tech2.id,
                service_id=service1.id,
                price_charged=30.0,
                tip_amount=6.0,
            ),
            # Carol - 2 appointments, 1 customer, lower revenue
            Appointment(
                date_time=now - timedelta(days=6),
                customer_id=customer3.id,
                technician_id=tech3.id,
                service_id=service1.id,
                price_charged=30.0,
                tip_amount=4.0,
            ),
            Appointment(
                date_time=now - timedelta(days=14),
                customer_id=customer3.id,
                technician_id=tech3.id,
                service_id=service1.id,
                price_charged=30.0,
                tip_amount=5.0,
            ),
        ]
        db.session.add_all(appointments)
        db.session.commit()

        return {
            "technicians": [tech1, tech2, tech3],
            "services": [service1, service2, service3],
            "customers": [customer1, customer2, customer3],
        }


class TestTechnicianPerformance:
    """Test technician performance analytics."""

    def test_get_technician_performance_basic(self, test_app, sample_data):
        """Test basic technician performance calculation."""
        with test_app.app_context():
            performance = get_technician_performance()

            assert len(performance) == 3
            # Alice should be ranked #1
            assert performance[0]["name"] == "Alice"
            assert performance[0]["rank"] == 1
            assert performance[0]["appointment_count"] == 5
            assert performance[0]["total_revenue"] == 240.0
            assert performance[0]["total_tips"] == 46.0

    def test_performance_ranking_order(self, test_app, sample_data):
        """Test that technicians are ranked by revenue."""
        with test_app.app_context():
            performance = get_technician_performance()

            # Should be ordered by revenue: Alice > Bob > Carol
            assert performance[0]["name"] == "Alice"
            assert performance[1]["name"] == "Bob"
            assert performance[2]["name"] == "Carol"

            assert performance[0]["rank"] == 1
            assert performance[1]["rank"] == 2
            assert performance[2]["rank"] == 3

    def test_performance_commission_calculation(self, test_app, sample_data):
        """Test commission calculation for technicians."""
        with test_app.app_context():
            performance = get_technician_performance()

            alice = next(p for p in performance if p["name"] == "Alice")
            expected_commission = 240.0 * 0.60  # 60% commission rate
            assert alice["commission_earned"] == expected_commission

    def test_performance_date_filtering(self, test_app, sample_data):
        """Test date range filtering for performance data."""
        with test_app.app_context():
            now = datetime.now()
            # Only last 7 days
            performance = get_technician_performance(
                start_date=now - timedelta(days=7), end_date=now
            )

            alice = next((p for p in performance if p["name"] == "Alice"), None)
            # Should only have 1 appointment from 5 days ago
            if alice:
                assert alice["appointment_count"] == 1

    def test_unique_customers_count(self, test_app, sample_data):
        """Test unique customer counting."""
        with test_app.app_context():
            performance = get_technician_performance()

            alice = next(p for p in performance if p["name"] == "Alice")
            assert alice["unique_customers"] == 3  # Served 3 different customers

            bob = next(p for p in performance if p["name"] == "Bob")
            assert bob["unique_customers"] == 2  # Served 2 different customers

    def test_avg_service_price(self, test_app, sample_data):
        """Test average service price calculation."""
        with test_app.app_context():
            performance = get_technician_performance()

            alice = next(p for p in performance if p["name"] == "Alice")
            expected_avg = (55.0 + 55.0 + 45.0 + 55.0 + 30.0) / 5
            assert alice["avg_service_price"] == round(expected_avg, 2)

    def test_no_appointments(self, test_app):
        """Test performance with no appointments."""
        with test_app.app_context():
            # Create tech but no appointments
            tech = Technician(name="NewTech", commission_rate=0.60)
            db.session.add(tech)
            db.session.commit()

            performance = get_technician_performance()
            assert len(performance) == 0  # No performance data for techs with 0 appointments


class TestCustomerRetention:
    """Test customer retention analytics."""

    def test_retention_calculation(self, test_app, sample_data):
        """Test retention rate calculation."""
        with test_app.app_context():
            retention = get_customer_retention_by_technician()

            alice = next(r for r in retention if r["technician_name"] == "Alice")
            # Alice: 3 customers, 2 are returning (customer1 and customer2 have 2+ visits)
            assert alice["total_customers"] == 3
            assert alice["returning_customers"] == 2
            assert alice["retention_rate"] == round((2 / 3) * 100, 1)

    def test_retention_all_new_customers(self, test_app):
        """Test retention when all customers are new."""
        with test_app.app_context():
            tech = Technician(name="TestTech", commission_rate=0.60)
            service = Service(name="Service", base_price=30.0)
            db.session.add_all([tech, service])
            db.session.commit()

            # Create 3 customers, each with only 1 visit
            for i in range(3):
                customer = Customer(first_name=f"Customer{i}", phone=f"555-{i:04d}")
                db.session.add(customer)
                db.session.commit()

                appt = Appointment(
                    date_time=datetime.now() - timedelta(days=i),
                    customer_id=customer.id,
                    technician_id=tech.id,
                    service_id=service.id,
                    price_charged=30.0,
                    tip_amount=5.0,
                )
                db.session.add(appt)

            db.session.commit()

            retention = get_customer_retention_by_technician()
            tech_retention = next(r for r in retention if r["technician_name"] == "TestTech")

            assert tech_retention["total_customers"] == 3
            assert tech_retention["returning_customers"] == 0
            assert tech_retention["retention_rate"] == 0.0

    def test_retention_no_customers(self, test_app):
        """Test retention with technician who has no customers."""
        with test_app.app_context():
            tech = Technician(name="Lonely", commission_rate=0.60)
            db.session.add(tech)
            db.session.commit()

            retention = get_customer_retention_by_technician()
            tech_retention = next(r for r in retention if r["technician_name"] == "Lonely")

            assert tech_retention["total_customers"] == 0
            assert tech_retention["retention_rate"] == 0.0


class TestTopServices:
    """Test top services by technician."""

    def test_top_services_ranking(self, test_app, sample_data):
        """Test that services are ranked by count."""
        with test_app.app_context():
            # Query Alice fresh from the database
            tech = Technician.query.filter_by(name="Alice").first()
            top_services = get_top_services_by_technician(tech.id, limit=3)

            # Alice performed: Gel Nails 3x, Pedicure 1x, Manicure 1x
            assert len(top_services) <= 3
            assert top_services[0]["service_name"] == "Gel Nails"
            assert top_services[0]["count"] == 3

    def test_top_services_revenue(self, test_app, sample_data):
        """Test revenue calculation for top services."""
        with test_app.app_context():
            # Query Alice fresh from the database
            tech = Technician.query.filter_by(name="Alice").first()
            top_services = get_top_services_by_technician(tech.id)

            gel_nails = next(s for s in top_services if s["service_name"] == "Gel Nails")
            assert gel_nails["revenue"] == 165.0  # 3 × $55

    def test_top_services_limit(self, test_app, sample_data):
        """Test limit parameter for top services."""
        with test_app.app_context():
            # Query Alice fresh from the database
            tech = Technician.query.filter_by(name="Alice").first()
            top_services = get_top_services_by_technician(tech.id, limit=2)

            assert len(top_services) <= 2


class TestStaffSummaryStats:
    """Test overall staff summary statistics."""

    def test_summary_stats_calculation(self, test_app, sample_data):
        """Test summary statistics calculation."""
        with test_app.app_context():
            stats = get_staff_summary_stats()

            assert stats["total_technicians"] == 3
            assert stats["total_appointments"] == 10
            # Alice: 240, Bob: 105, Carol: 60 = 405 total
            assert stats["total_revenue"] == 405.0
            # Alice: 46, Bob: 18, Carol: 9 = 73 total
            assert stats["total_tips"] == 73.0

    def test_avg_revenue_per_tech(self, test_app, sample_data):
        """Test average revenue per technician."""
        with test_app.app_context():
            stats = get_staff_summary_stats()

            expected_avg = 405.0 / 3  # Total revenue / 3 techs
            assert stats["avg_revenue_per_tech"] == round(expected_avg, 2)

    def test_date_range_days(self, test_app, sample_data):
        """Test date range calculation."""
        with test_app.app_context():
            now = datetime.now()
            stats = get_staff_summary_stats(start_date=now - timedelta(days=30), end_date=now)

            assert stats["date_range_days"] == 30

    def test_empty_database(self, test_app):
        """Test summary stats with no data."""
        with test_app.app_context():
            stats = get_staff_summary_stats()

            assert stats["total_technicians"] == 0
            assert stats["total_appointments"] == 0
            assert stats["total_revenue"] == 0.0
            assert stats["avg_revenue_per_tech"] == 0.0


class TestStaffPerformanceRoute:
    """Test the staff performance route."""

    def test_staff_performance_route_exists(self, test_app, sample_data):
        """Test that the staff performance route returns successfully."""
        with test_app.test_client() as client:
            response = client.get("/staff-performance")
            assert response.status_code == 200

    def test_staff_performance_with_days_param(self, test_app, sample_data):
        """Test route with days query parameter."""
        with test_app.test_client() as client:
            response = client.get("/staff-performance?days=7")
            assert response.status_code == 200

    def test_staff_performance_template_data(self, test_app, sample_data):
        """Test that route passes correct data to template."""
        with test_app.test_client() as client:
            response = client.get("/staff-performance")
            assert b"Staff Performance Dashboard" in response.data
            assert b"Alice" in response.data  # Should show technician name
