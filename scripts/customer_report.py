import sys

sys.path.insert(0, "..")

from backend.customer_analytics import calculate_customer_ltv, get_segment_summary

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
            print(
                f"  {segment:18} {stats['count']:3} customers  |  ${stats['total_revenue']:8,.2f} total  |  ${stats['avg_spend']:6,.2f} avg"
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
            print(
                f"{customer['name']:<15} {customer['phone']:<15} {customer['days_since_last_visit']:<18} ${customer['total_spend']:,.2f}"
            )

    print("\n" + "=" * 60)
