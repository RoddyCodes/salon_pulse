"""Analyze salon business data and generate reports."""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import func  # noqa: E402

from backend.models import Appointment, Customer, Technician, app, db  # noqa: E402


def run_reports():
    with app.app_context():
        print("\n" + "=" * 50)
        print(" 💅 SALON PULSE: DASHBOARD")
        print("=" * 50)

        # --- REPORT 1: STAFF PERFORMANCE ---
        print("\n📊 TECHNICIAN PERFORMANCE")
        results = (
            db.session.query(
                Technician.name,
                func.count(Appointment.id).label("total_jobs"),
                func.sum(Appointment.price_charged).label("total_revenue"),
                func.sum(Appointment.tip_amount).label("total_tips"),
            )
            .join(Technician)
            .group_by(Technician.name)
            .all()
        )

        for row in results:
            name, jobs, revenue, tips = row
            total = revenue + tips
            print(f"  • {name}: ${total:,.2f} ({jobs} appts)")

        # --- REPORT 2: AT-RISK CUSTOMERS ---
        print("\n⚠️  RETENTION ALERTS (Haven't visited in 30 days)")

        # Calculate the date 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Find customers whose LATEST appointment is older than that date
        # This requires a subquery: Find Max Date per customer, then filter

        # Simplified Logic for now: Find anyone who hasn't visited since that date
        # 1. Get list of all customers
        all_customers = Customer.query.all()

        at_risk_count = 0
        for customer in all_customers:
            # Get their most recent appointment
            last_appt = (
                Appointment.query.filter_by(customer_id=customer.id)
                .order_by(Appointment.date_time.desc())
                .first()
            )

            if last_appt and last_appt.date_time < thirty_days_ago:
                days_missed = (datetime.now() - last_appt.date_time).days
                name = customer.first_name
                phone = customer.phone
                print(f"  • {name} {phone} " f"(Last seen: {days_missed} days ago)")
                at_risk_count += 1

        if at_risk_count == 0:
            print("  • Great news! All active customers have visited recently.")

        print("-" * 50)


if __name__ == "__main__":
    run_reports()
