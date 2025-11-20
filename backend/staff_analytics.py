"""Staff performance analytics and reporting."""

from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy import func

from backend.models import Appointment, Service, Technician, db


def get_technician_performance(
    start_date: datetime = None, end_date: datetime = None
) -> List[Dict]:
    """
    Calculate comprehensive performance metrics for each technician.

    Args:
        start_date: Start of date range (default: 30 days ago)
        end_date: End of date range (default: now)

    Returns:
        List of dicts with technician performance data
    """
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Query appointments with aggregations per technician
    results = (
        db.session.query(
            Technician.id,
            Technician.name,
            Technician.commission_rate,
            func.count(Appointment.id).label("appointment_count"),
            func.sum(Appointment.price_charged).label("total_revenue"),
            func.sum(Appointment.tip_amount).label("total_tips"),
            func.avg(Appointment.price_charged).label("avg_service_price"),
            func.count(func.distinct(Appointment.customer_id)).label("unique_customers"),
        )
        .join(Appointment, Technician.id == Appointment.technician_id)
        .filter(Appointment.date_time >= start_date, Appointment.date_time <= end_date)
        .group_by(Technician.id)
        .all()
    )

    performance_data = []
    for row in results:
        total_revenue = float(row.total_revenue or 0)
        total_tips = float(row.total_tips or 0)
        commission_earned = total_revenue * row.commission_rate

        performance_data.append(
            {
                "id": row.id,
                "name": row.name,
                "appointment_count": row.appointment_count,
                "total_revenue": round(total_revenue, 2),
                "total_tips": round(total_tips, 2),
                "commission_earned": round(commission_earned, 2),
                "avg_service_price": round(float(row.avg_service_price or 0), 2),
                "unique_customers": row.unique_customers,
                "commission_rate": row.commission_rate,
            }
        )

    # Sort by total revenue descending
    performance_data.sort(key=lambda x: x["total_revenue"], reverse=True)

    # Add rank
    for idx, tech in enumerate(performance_data, start=1):
        tech["rank"] = idx

    return performance_data


def get_technician_revenue_trend(technician_id: int, days: int = 30) -> Dict[str, List]:
    """
    Get daily revenue trend for a specific technician.

    Args:
        technician_id: ID of the technician
        days: Number of days to look back

    Returns:
        Dict with dates and revenue arrays
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Query daily revenue
    results = (
        db.session.query(
            func.date(Appointment.date_time).label("date"),
            func.sum(Appointment.price_charged).label("daily_revenue"),
        )
        .filter(
            Appointment.technician_id == technician_id,
            Appointment.date_time >= start_date,
            Appointment.date_time <= end_date,
        )
        .group_by(func.date(Appointment.date_time))
        .order_by("date")
        .all()
    )

    dates = []
    revenues = []
    for row in results:
        dates.append(str(row.date))
        revenues.append(float(row.daily_revenue or 0))

    return {"dates": dates, "revenues": revenues}


def get_customer_retention_by_technician(
    start_date: datetime = None, end_date: datetime = None
) -> List[Dict]:
    """
    Calculate customer retention rate for each technician.

    Retention = customers with 2+ visits / total unique customers

    Args:
        start_date: Start of date range (default: 90 days ago)
        end_date: End of date range (default: now)

    Returns:
        List of dicts with retention metrics per technician
    """
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=90)

    # Get all technicians
    technicians = Technician.query.all()

    retention_data = []
    for tech in technicians:
        # Count appointments per customer for this technician
        customer_visits = (
            db.session.query(
                Appointment.customer_id, func.count(Appointment.id).label("visit_count")
            )
            .filter(
                Appointment.technician_id == tech.id,
                Appointment.date_time >= start_date,
                Appointment.date_time <= end_date,
            )
            .group_by(Appointment.customer_id)
            .all()
        )

        total_customers = len(customer_visits)
        if total_customers == 0:
            retention_rate = 0.0
        else:
            returning_customers = sum(1 for cv in customer_visits if cv.visit_count >= 2)
            retention_rate = (returning_customers / total_customers) * 100

        retention_data.append(
            {
                "technician_id": tech.id,
                "technician_name": tech.name,
                "total_customers": total_customers,
                "returning_customers": sum(1 for cv in customer_visits if cv.visit_count >= 2),
                "retention_rate": round(retention_rate, 1),
            }
        )

    return retention_data


def get_top_services_by_technician(technician_id: int, limit: int = 5) -> List[Dict]:
    """
    Get the most popular services performed by a technician.

    Args:
        technician_id: ID of the technician
        limit: Number of top services to return

    Returns:
        List of service performance data
    """
    results = (
        db.session.query(
            Appointment.service_id,
            func.count(Appointment.id).label("service_count"),
            func.sum(Appointment.price_charged).label("service_revenue"),
        )
        .filter(Appointment.technician_id == technician_id)
        .group_by(Appointment.service_id)
        .order_by(func.count(Appointment.id).desc())
        .limit(limit)
        .all()
    )

    top_services = []
    for row in results:
        service = db.session.get(Service, row.service_id)
        top_services.append(
            {
                "service_name": service.name if service else "Unknown",
                "count": row.service_count,
                "revenue": round(float(row.service_revenue or 0), 2),
            }
        )

    return top_services


def get_staff_summary_stats(start_date: datetime = None, end_date: datetime = None) -> Dict:
    """
    Get overall staff performance summary statistics.

    Args:
        start_date: Start of date range (default: 30 days ago)
        end_date: End of date range (default: now)

    Returns:
        Dict with summary statistics
    """
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    total_techs = Technician.query.count()

    # Total appointments and revenue in period
    result = (
        db.session.query(
            func.count(Appointment.id).label("total_appointments"),
            func.sum(Appointment.price_charged).label("total_revenue"),
            func.sum(Appointment.tip_amount).label("total_tips"),
        )
        .filter(Appointment.date_time >= start_date, Appointment.date_time <= end_date)
        .first()
    )

    total_appointments = result.total_appointments or 0
    total_revenue = float(result.total_revenue or 0)
    total_tips = float(result.total_tips or 0)

    avg_per_tech = total_revenue / total_techs if total_techs > 0 else 0

    return {
        "total_technicians": total_techs,
        "total_appointments": total_appointments,
        "total_revenue": round(total_revenue, 2),
        "total_tips": round(total_tips, 2),
        "avg_revenue_per_tech": round(avg_per_tech, 2),
        "date_range_days": (end_date - start_date).days,
    }
