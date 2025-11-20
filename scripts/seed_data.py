"""Generate realistic seed data for the salon application."""

import random
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "..")

from backend.models import Appointment, Customer, Service, Technician, app, db  # noqa: E402


def add_sample_data():
    """Populates the database with realistic practice data spanning 90 days."""
    with app.app_context():
        # Clear old data to avoid duplicates while testing
        db.drop_all()
        db.create_all()

        print("🔄 Generating practice dataset...")

        # 1. Create Staff (5 technicians with varying commission rates)
        techs = [
            Technician(name="Lisa", commission_rate=0.65),  # Senior tech, higher rate
            Technician(name="Tom", commission_rate=0.60),
            Technician(name="Maria", commission_rate=0.60),
            Technician(name="Kevin", commission_rate=0.55),  # Newer tech
            Technician(name="Jenny", commission_rate=0.60),
        ]
        db.session.add_all(techs)
        db.session.commit()
        print(f"✅ Created {len(techs)} technicians")

        # 2. Create Services (Realistic salon menu)
        services = [
            # Manicures
            Service(name="Basic Manicure", base_price=25.00, category="Hands"),
            Service(name="Gel Manicure", base_price=35.00, category="Hands"),
            Service(name="Acrylic Full Set", base_price=55.00, category="Hands"),
            Service(name="Gel X Extensions", base_price=65.00, category="Hands"),
            Service(name="Nail Repair", base_price=15.00, category="Hands"),
            # Pedicures
            Service(name="Basic Pedicure", base_price=35.00, category="Feet"),
            Service(name="Spa Pedicure", base_price=45.00, category="Feet"),
            Service(name="Deluxe Pedicure", base_price=55.00, category="Feet"),
            Service(name="Gel Pedicure", base_price=50.00, category="Feet"),
            # Add-ons
            Service(name="Nail Art (per nail)", base_price=5.00, category="Add-on"),
            Service(name="Chrome/Cat Eye", base_price=10.00, category="Add-on"),
            Service(name="Callus Treatment", base_price=15.00, category="Add-on"),
        ]
        db.session.add_all(services)
        db.session.commit()
        print(f"✅ Created {len(services)} services")

        # 3. Create Customers (Mix of regulars, occasionals, and at-risk)
        first_names = [
            "Sarah",
            "Jennifer",
            "Maria",
            "Emily",
            "Ashley",
            "Jessica",
            "Amanda",
            "Michelle",
            "Stephanie",
            "Nicole",
            "Elizabeth",
            "Rebecca",
            "Laura",
            "Angela",
            "Melissa",
            "Kimberly",
            "Lisa",
            "Amy",
            "Anna",
            "Rachel",
            "Samantha",
            "Diana",
            "Karen",
            "Nancy",
            "Betty",
            "Helen",
            "Sandra",
            "Donna",
            "Carol",
            "Ruth",
            "Sharon",
            "Patricia",
            "Deborah",
            "Linda",
        ]

        customers = []
        for i, name in enumerate(first_names, start=1):
            customer = Customer(
                first_name=name,
                phone=f"555-{1000+i:04d}",
                notes=random.choice(
                    [
                        "Prefers almond shape",
                        "Likes bright colors",
                        "Sensitive cuticles",
                        "Regular customer",
                        "Prefers natural look",
                        "",  # Some customers have no notes
                    ]
                ),
            )
            customers.append(customer)

        db.session.add_all(customers)
        db.session.commit()
        print(f"✅ Created {len(customers)} customers")

        # 4. Generate Appointments (90 days of history with realistic patterns)
        appointments = []
        start_date = datetime.now() - timedelta(days=90)

        # Define customer visit patterns
        # Regular customers (visit every 2-3 weeks)
        regular_customers = customers[:15]
        # Occasional customers (visit every 4-6 weeks)
        occasional_customers = customers[15:25]
        # At-risk customers (haven't visited in 30+ days)
        at_risk_customers = customers[25:]

        # Payment method distribution
        payment_methods = ["Cash", "Card", "Card", "Card"]  # 75% card, 25% cash

        # Generate appointments for regular customers
        for customer in regular_customers:
            days_between_visits = random.randint(14, 21)
            current_date = start_date + timedelta(days=random.randint(0, 14))

            while current_date <= datetime.now():
                # Skip some days to make it more realistic (closed days, customer cancellations)
                if random.random() < 0.85:  # 85% chance of appointment happening
                    # Regular customers tend to book same services
                    service = random.choice(services[:9])  # Prefer main services
                    tech = random.choice(techs)

                    # Price varies slightly from base price
                    price_variation = random.uniform(-2, 5)
                    price = max(service.base_price + price_variation, service.base_price)

                    # Tip amount (15-25% of service, some customers tip more)
                    tip_percentage = random.uniform(0.15, 0.25)
                    tip = round(price * tip_percentage, 2)

                    # Add some appointments at specific times
                    hour = random.choice([9, 10, 11, 12, 13, 14, 15, 16, 17])
                    minute = random.choice([0, 15, 30, 45])
                    appt_time = current_date.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )

                    appointment = Appointment(
                        date_time=appt_time,
                        customer_id=customer.id,
                        technician_id=tech.id,
                        service_id=service.id,
                        price_charged=round(price, 2),
                        tip_amount=tip,
                        payment_method=random.choice(payment_methods),
                    )
                    appointments.append(appointment)

                current_date += timedelta(days=days_between_visits)

        # Generate appointments for occasional customers
        for customer in occasional_customers:
            days_between_visits = random.randint(28, 45)
            current_date = start_date + timedelta(days=random.randint(0, 30))

            while current_date <= datetime.now():
                if random.random() < 0.80:  # 80% chance
                    service = random.choice(services[:9])
                    tech = random.choice(techs)

                    price_variation = random.uniform(-2, 5)
                    price = max(service.base_price + price_variation, service.base_price)
                    tip_percentage = random.uniform(0.10, 0.20)
                    tip = round(price * tip_percentage, 2)

                    hour = random.choice([9, 10, 11, 12, 13, 14, 15, 16, 17])
                    minute = random.choice([0, 15, 30, 45])
                    appt_time = current_date.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )

                    appointment = Appointment(
                        date_time=appt_time,
                        customer_id=customer.id,
                        technician_id=tech.id,
                        service_id=service.id,
                        price_charged=round(price, 2),
                        tip_amount=tip,
                        payment_method=random.choice(payment_methods),
                    )
                    appointments.append(appointment)

                current_date += timedelta(days=days_between_visits)

        # Generate old appointments for at-risk customers (31-60 days ago)
        for customer in at_risk_customers:
            # These customers haven't visited recently
            days_ago = random.randint(31, 60)
            appt_date = datetime.now() - timedelta(days=days_ago)

            service = random.choice(services[:9])
            tech = random.choice(techs)

            price_variation = random.uniform(-2, 5)
            price = max(service.base_price + price_variation, service.base_price)
            tip_percentage = random.uniform(0.10, 0.20)
            tip = round(price * tip_percentage, 2)

            hour = random.choice([9, 10, 11, 12, 13, 14, 15, 16, 17])
            minute = random.choice([0, 15, 30, 45])
            appt_time = appt_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            appointment = Appointment(
                date_time=appt_time,
                customer_id=customer.id,
                technician_id=tech.id,
                service_id=service.id,
                price_charged=round(price, 2),
                tip_amount=tip,
                payment_method=random.choice(payment_methods),
            )
            appointments.append(appointment)

        # Batch insert all appointments
        db.session.add_all(appointments)
        db.session.commit()
        print(f"✅ Created {len(appointments)} appointments")

        # Print summary statistics
        print("\n📊 Dataset Summary:")
        start_str = start_date.strftime("%Y-%m-%d")
        now_str = datetime.now().strftime("%Y-%m-%d")
        print(f"   • Date Range: {start_str} to {now_str}")
        total_revenue = sum(a.price_charged + a.tip_amount for a in appointments)
        print(f"   • Total Revenue: ${total_revenue:,.2f}")
        avg_transaction = total_revenue / len(appointments)
        print(f"   • Average Transaction: ${avg_transaction:.2f}")
        print(f"   • Regular Customers: {len(regular_customers)}")
        print(f"   • At-Risk Customers: {len(at_risk_customers)}")
        print("\n✅ Practice dataset generated successfully!")


if __name__ == "__main__":
    add_sample_data()
