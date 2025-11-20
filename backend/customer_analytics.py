"""
Customer Lifetime Value (LTV) Analytics Module

This module analyzes customer behavior and calculates lifetime value metrics
to help identify VIP customers, at-risk customers, and growth opportunities.
"""

from collections import defaultdict
from datetime import datetime

from backend.models import Appointment, Customer, app


def calculate_customer_ltv():
    """
    Calculate comprehensive lifetime value metrics for all customers.

    Returns:
        list of dicts: Each customer with their LTV metrics and segment
    """
    with app.app_context():
        customers = Customer.query.all()
        customer_metrics = []

        for customer in customers:
            appointments = (
                Appointment.query.filter_by(customer_id=customer.id)
                .order_by(Appointment.date_time.asc())
                .all()
            )

            if not appointments:
                continue  # Skip customers with no appointments

            # Basic Metrics
            total_visits = len(appointments)
            total_revenue = sum(a.price_charged for a in appointments)
            total_tips = sum(a.tip_amount for a in appointments)
            total_spend = total_revenue + total_tips

            # Date Metrics
            first_visit = appointments[0].date_time
            last_visit = appointments[-1].date_time
            days_as_customer = (datetime.now() - first_visit).days
            days_since_last_visit = (datetime.now() - last_visit).days

            # Calculate average days between visits
            if total_visits > 1:
                visit_dates = [a.date_time for a in appointments]
                gaps = [
                    (visit_dates[i + 1] - visit_dates[i]).days for i in range(len(visit_dates) - 1)
                ]
                avg_days_between_visits = sum(gaps) / len(gaps)
            else:
                avg_days_between_visits = days_as_customer

            # Revenue Metrics
            avg_transaction_value = total_spend / total_visits
            avg_tip_percentage = (total_tips / total_revenue * 100) if total_revenue > 0 else 0

            # Predict Future Value
            # Simple prediction: If they continue at current frequency for next 12 months
            if avg_days_between_visits > 0:
                predicted_visits_next_year = 365 / avg_days_between_visits
                predicted_ltv_12mo = predicted_visits_next_year * avg_transaction_value
            else:
                predicted_ltv_12mo = 0

            # Calculate visit frequency trend (are they coming more or less often?)
            visit_trend = "Stable"
            if total_visits >= 3:
                # Compare first half vs second half of visit gaps
                mid_point = len(gaps) // 2
                if mid_point > 0:
                    first_half_avg = sum(gaps[:mid_point]) / mid_point
                    second_half_avg = sum(gaps[mid_point:]) / len(gaps[mid_point:])

                    if second_half_avg < first_half_avg * 0.8:  # Coming more frequently
                        visit_trend = "Increasing"
                    elif second_half_avg > first_half_avg * 1.2:  # Coming less frequently
                        visit_trend = "Decreasing"

            # Customer Segmentation
            segment = classify_customer(
                total_visits=total_visits,
                days_since_last_visit=days_since_last_visit,
                total_spend=total_spend,
                avg_days_between_visits=avg_days_between_visits,
            )

            # Compile all metrics
            customer_metrics.append(
                {
                    "customer_id": customer.id,
                    "name": customer.first_name,
                    "phone": customer.phone,
                    "segment": segment,
                    # Visit Metrics
                    "total_visits": total_visits,
                    "first_visit": first_visit,
                    "last_visit": last_visit,
                    "days_as_customer": days_as_customer,
                    "days_since_last_visit": days_since_last_visit,
                    "avg_days_between_visits": round(avg_days_between_visits, 1),
                    "visit_trend": visit_trend,
                    # Financial Metrics
                    "total_spend": round(total_spend, 2),
                    "total_revenue": round(total_revenue, 2),
                    "total_tips": round(total_tips, 2),
                    "avg_transaction_value": round(avg_transaction_value, 2),
                    "avg_tip_percentage": round(avg_tip_percentage, 1),
                    # Predictions
                    "predicted_ltv_12mo": round(predicted_ltv_12mo, 2),
                    # Service Preferences
                    "favorite_services": get_favorite_services(appointments),
                    "favorite_technician": get_favorite_technician(appointments),
                }
            )

        # Sort by total spend (highest LTV first)
        customer_metrics.sort(key=lambda x: x["total_spend"], reverse=True)

        return customer_metrics


def classify_customer(total_visits, days_since_last_visit, total_spend, avg_days_between_visits):
    """
    Segment customers based on their behavior patterns.

    Segments:
    - VIP: High spend, frequent visits, recent activity
    - Champion: Very frequent visits, good spend, loyal
    - Loyal: Consistent visits over time
    - Promising: New but showing good signs
    - At-Risk: Was good but hasn't visited recently
    - Needs Attention: Infrequent or low spend
    - Lost: Hasn't visited in 60+ days
    """

    # Thresholds (adjust based on your business)
    HIGH_SPEND = 300  # Total lifetime spend
    FREQUENT_VISITS = 5  # Number of visits
    REGULAR_FREQUENCY = 28  # Days between visits
    AT_RISK_DAYS = 45  # Days since last visit
    LOST_DAYS = 60

    # Lost customers (hasn't visited in 60+ days)
    if days_since_last_visit > LOST_DAYS:
        return "Lost"

    # VIP: High spend + recent activity
    if total_spend >= HIGH_SPEND and days_since_last_visit <= REGULAR_FREQUENCY:
        return "VIP"

    # Champion: Very frequent visits + loyal + recent
    if (
        total_visits >= FREQUENT_VISITS
        and avg_days_between_visits <= REGULAR_FREQUENCY
        and days_since_last_visit <= REGULAR_FREQUENCY
    ):
        return "Champion"

    # At-Risk: Was good but overdue for visit
    if (
        total_visits >= FREQUENT_VISITS or total_spend >= HIGH_SPEND
    ) and days_since_last_visit > AT_RISK_DAYS:
        return "At-Risk"

    # Loyal: Consistent visits
    if total_visits >= FREQUENT_VISITS and avg_days_between_visits <= REGULAR_FREQUENCY * 1.5:
        return "Loyal"

    # Promising: New customer (1-3 visits) but recent
    if total_visits <= 3 and days_since_last_visit <= REGULAR_FREQUENCY:
        return "Promising"

    # Default: Needs Attention
    return "Needs Attention"


def get_favorite_services(appointments):
    """Get the top 2 most frequent services for a customer."""
    service_counts = defaultdict(int)
    for appt in appointments:
        service_counts[appt.service.name] += 1

    # Sort by frequency
    sorted_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)

    # Return top 2 services
    return [s[0] for s in sorted_services[:2]]


def get_favorite_technician(appointments):
    """Get the technician the customer visits most often."""
    tech_counts = defaultdict(int)
    for appt in appointments:
        tech_counts[appt.technician.name] += 1

    if not tech_counts:
        return "None"

    # Return most frequent technician
    return max(tech_counts.items(), key=lambda x: x[1])[0]


def get_segment_summary():
    """
    Get summary statistics for each customer segment.

    Returns:
        dict: Segment names with counts and total revenue
    """
    customers = calculate_customer_ltv()

    segment_stats = defaultdict(lambda: {"count": 0, "total_revenue": 0, "avg_spend": 0})

    for customer in customers:
        segment = customer["segment"]
        segment_stats[segment]["count"] += 1
        segment_stats[segment]["total_revenue"] += customer["total_spend"]

    # Calculate averages
    for segment in segment_stats:
        count = segment_stats[segment]["count"]
        if count > 0:
            segment_stats[segment]["avg_spend"] = segment_stats[segment]["total_revenue"] / count

    return dict(segment_stats)


# CLI Tool for quick analysis
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("💎 CUSTOMER LIFETIME VALUE ANALYSIS")
    print("=" * 60)

    customers = calculate_customer_ltv()

    # Print segment summary
    print("\n📊 CUSTOMER SEGMENTS")
    print("-" * 60)
    segment_summary = get_segment_summary()

    segment_order = ["VIP", "Champion", "Loyal", "Promising", "At-Risk", "Needs Attention", "Lost"]
    for segment in segment_order:
        if segment in segment_summary:
            stats = segment_summary[segment]
            revenue = stats["total_revenue"]
            avg = stats["avg_spend"]
            print(
                f"  {segment:18} {stats['count']:3} customers  |  "
                f"${revenue:8,.2f} total  |  ${avg:6,.2f} avg"
            )

    # Print top 10 customers by LTV
    print("\n💰 TOP 10 CUSTOMERS BY LIFETIME VALUE")
    print("-" * 60)
    print(f"{'Name':<15} {'Segment':<15} {'Visits':<8} {'Total Spend':<12} {'Predicted 12mo'}")
    print("-" * 60)

    for customer in customers[:10]:
        print(
            f"{customer['name']:<15} {customer['segment']:<15} {customer['total_visits']:<8} "
            f"${customer['total_spend']:<11,.2f} ${customer['predicted_ltv_12mo']:,.2f}"
        )

    # Print at-risk customers
    at_risk = [c for c in customers if c["segment"] == "At-Risk"]
    if at_risk:
        print(f"\n⚠️  AT-RISK CUSTOMERS ({len(at_risk)} total)")
        print("-" * 60)
        print(f"{'Name':<15} {'Phone':<15} {'Days Since Visit':<18} {'Total Spend'}")
        print("-" * 60)

        for customer in at_risk[:10]:  # Show top 10 at-risk by spend
            days = customer["days_since_last_visit"]
            spend = customer["total_spend"]
            print(f"{customer['name']:<15} {customer['phone']:<15} " f"{days:<18} ${spend:,.2f}")

    print("\n" + "=" * 60)
