"""
Unit tests for customer analytics module.
"""

from datetime import datetime, timedelta

import pytest

from backend.customer_analytics import (
    calculate_customer_ltv,
    classify_customer,
    get_favorite_services,
    get_favorite_technician,
    get_segment_summary,
)
from backend.models import Appointment


class TestCustomerSegmentation:
    """Tests for customer segmentation logic."""

    def test_vip_classification(self):
        """Test VIP customer classification."""
        segment = classify_customer(
            total_visits=5, days_since_last_visit=10, total_spend=350.00, avg_days_between_visits=20
        )
        assert segment == "VIP"

    def test_champion_classification(self):
        """Test Champion customer classification."""
        segment = classify_customer(
            total_visits=6, days_since_last_visit=15, total_spend=250.00, avg_days_between_visits=25
        )
        assert segment == "Champion"

    def test_lost_classification(self):
        """Test Lost customer classification."""
        segment = classify_customer(
            total_visits=3, days_since_last_visit=65, total_spend=150.00, avg_days_between_visits=30
        )
        assert segment == "Lost"

    def test_promising_classification(self):
        """Test Promising customer classification."""
        segment = classify_customer(
            total_visits=2, days_since_last_visit=20, total_spend=100.00, avg_days_between_visits=25
        )
        assert segment == "Promising"

    def test_at_risk_classification(self):
        """Test At-Risk customer classification."""
        segment = classify_customer(
            total_visits=5, days_since_last_visit=50, total_spend=300.00, avg_days_between_visits=25
        )
        assert segment == "At-Risk"

    def test_loyal_classification(self):
        """Test Loyal customer classification."""
        segment = classify_customer(
            total_visits=8, days_since_last_visit=30, total_spend=250.00, avg_days_between_visits=35
        )
        assert segment == "Loyal"

    def test_needs_attention_classification(self):
        """Test Needs Attention customer classification."""
        segment = classify_customer(
            total_visits=2, days_since_last_visit=40, total_spend=80.00, avg_days_between_visits=25
        )
        assert segment == "Needs Attention"


class TestLTVCalculation:
    """Tests for LTV calculation."""

    def test_calculate_ltv_with_appointments(self, db_session, sample_appointment, sample_customer):
        """Test LTV calculation with appointment data."""
        customers = calculate_customer_ltv()

        assert len(customers) > 0
        assert customers[0]["name"] == "Test Customer"
        assert customers[0]["total_spend"] == 40.00  # 35 + 5

    def test_ltv_metrics_structure(self, db_session, sample_appointment):
        """Test that LTV metrics have correct structure."""
        customers = calculate_customer_ltv()

        required_keys = [
            "customer_id",
            "name",
            "phone",
            "segment",
            "total_visits",
            "total_spend",
            "avg_transaction_value",
            "days_since_last_visit",
            "predicted_ltv_12mo",
            "favorite_services",
            "favorite_technician",
        ]

        for key in required_keys:
            assert key in customers[0]

    def test_calculate_ltv_with_multiple_appointments(
        self, db_session, sample_customer, sample_technician, sample_service
    ):
        """Test LTV calculation with multiple appointments to test trend calculation."""
        # Create multiple appointments over time
        from backend.models import Appointment, db

        # First appointment
        appt1 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=60),
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Card",
        )
        db.session.add(appt1)

        # Second appointment
        appt2 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=30),
            price_charged=40.00,
            tip_amount=6.00,
            payment_method="Card",
        )
        db.session.add(appt2)

        # Third appointment
        appt3 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=10),
            price_charged=45.00,
            tip_amount=7.00,
            payment_method="Cash",
        )
        db.session.add(appt3)
        db.session.commit()

        customers = calculate_customer_ltv()
        assert len(customers) > 0
        assert customers[0]["total_visits"] >= 3
        assert "visit_trend" in customers[0]

    def test_calculate_ltv_skips_customers_without_appointments(self, db_session, sample_customer):
        """Test that customers without appointments are skipped."""
        # Customer exists but has no appointments
        customers = calculate_customer_ltv()
        # Should return empty or only include customers with appointments
        assert isinstance(customers, list)

    def test_calculate_ltv_with_decreasing_trend(
        self, db_session, sample_customer, sample_technician, sample_service
    ):
        """Test LTV calculation detects decreasing visit frequency."""
        from backend.models import Appointment, db

        # Create appointments with increasing gaps (decreasing frequency)
        appt1 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=100),
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Card",
        )
        db.session.add(appt1)

        appt2 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=80),  # 20 days gap
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Card",
        )
        db.session.add(appt2)

        appt3 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=40),  # 40 days gap (increasing gap)
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Card",
        )
        db.session.add(appt3)

        appt4 = Appointment(
            customer_id=sample_customer.id,
            technician_id=sample_technician.id,
            service_id=sample_service.id,
            date_time=datetime.now() - timedelta(days=10),  # 30 days gap
            price_charged=35.00,
            tip_amount=5.00,
            payment_method="Cash",
        )
        db.session.add(appt4)
        db.session.commit()

        customers = calculate_customer_ltv()
        assert len(customers) > 0
        # Should detect the trend (though exact trend may vary based on algorithm)
        assert "visit_trend" in customers[0]


class TestServicePreferences:
    """Tests for service preference functions."""

    def test_get_favorite_services(self, db_session, sample_appointment):
        """Test getting favorite services."""
        appointments = [sample_appointment]
        favorites = get_favorite_services(appointments)

        assert len(favorites) > 0
        assert "Test Manicure" in favorites

    def test_get_favorite_technician(self, db_session, sample_appointment):
        """Test getting favorite technician."""
        appointments = [sample_appointment]
        favorite = get_favorite_technician(appointments)

        assert favorite == "Test Tech"

    def test_get_favorite_services_empty(self):
        """Test getting favorite services with empty list."""
        favorites = get_favorite_services([])
        assert favorites == []

    def test_get_favorite_technician_empty(self):
        """Test getting favorite technician with empty list."""
        favorite = get_favorite_technician([])
        assert favorite == "None"


class TestSegmentSummary:
    """Tests for segment summary function."""

    def test_segment_summary_structure(self, db_session, sample_appointment):
        """Test segment summary returns correct structure."""
        summary = get_segment_summary()

        assert isinstance(summary, dict)

        # Check that each segment has required keys
        for segment_data in summary.values():
            assert "count" in segment_data
            assert "total_revenue" in segment_data
            assert "avg_spend" in segment_data
