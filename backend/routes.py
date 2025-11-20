from datetime import datetime, timedelta

from flask import flash, redirect, render_template, request
from sqlalchemy import func

from backend.customer_analytics import calculate_customer_ltv, get_segment_summary

# Import from backend package
from backend.models import Appointment, Customer, Service, Technician, app, db


# --- ROUTE 1: THE DASHBOARD ---
@app.route("/")
def dashboard():
    # 1. Get Performance Data
    performance = (
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

    # 2. Get Retention Alerts
    thirty_days_ago = datetime.now() - timedelta(days=30)
    at_risk_customers = []

    all_customers = Customer.query.all()
    for customer in all_customers:
        last_appt = (
            Appointment.query.filter_by(customer_id=customer.id)
            .order_by(Appointment.date_time.desc())
            .first()
        )
        if last_appt and last_appt.date_time < thirty_days_ago:
            days_missed = (datetime.now() - last_appt.date_time).days
            at_risk_customers.append(
                {"name": customer.first_name, "phone": customer.phone, "days_missed": days_missed}
            )

    return render_template("dashboard.html", performance=performance, at_risk=at_risk_customers)


# --- ROUTE 2: HISTORY & CHARTS (WITH FILTERS) ---
@app.route("/appointments")
def appointment_history():
    # Get filter parameters from URL
    selected_period = request.args.get("period", "day")  # 'day' or 'month'
    selected_tech = request.args.get("tech_id", "all")  # 'all' or specific tech id

    # Get all technicians for the filter dropdown
    all_techs = Technician.query.all()

    # 1. Build base query for appointments
    query = Appointment.query

    # Apply technician filter if not "all"
    if selected_tech != "all":
        query = query.filter_by(technician_id=int(selected_tech))

    # Get filtered appointments (newest first)
    history = query.order_by(Appointment.date_time.desc()).all()

    # 2. Prepare TREND CHART Data (Revenue over time)
    trend_data = {}
    for appt in history:
        # Format date based on selected period
        if selected_period == "month":
            date_str = appt.date_time.strftime("%Y-%m")  # Group by month
        else:
            date_str = appt.date_time.strftime("%Y-%m-%d")  # Group by day

        total_money = appt.price_charged + appt.tip_amount
        trend_data[date_str] = trend_data.get(date_str, 0) + total_money

    # Sort dates chronologically
    trend_labels = sorted(trend_data.keys())
    trend_values = [trend_data[d] for d in trend_labels]

    # 3. Prepare TECHNICIAN BREAKDOWN (Bar Chart)
    tech_data = {}
    for appt in history:
        tech_name = appt.technician.name
        total_money = appt.price_charged + appt.tip_amount
        tech_data[tech_name] = tech_data.get(tech_name, 0) + total_money

    tech_labels = list(tech_data.keys())
    tech_values = list(tech_data.values())

    # 4. Prepare SERVICE BREAKDOWN (Doughnut Chart)
    service_data = {}
    for appt in history:
        service_name = appt.service.name
        total_money = appt.price_charged + appt.tip_amount
        service_data[service_name] = service_data.get(service_name, 0) + total_money

    service_labels = list(service_data.keys())
    service_values = list(service_data.values())

    return render_template(
        "appointments.html",
        history=history,
        trend_labels=trend_labels,
        trend_values=trend_values,
        tech_labels=tech_labels,
        tech_values=tech_values,
        service_labels=service_labels,
        service_values=service_values,
        selected_period=selected_period,
        selected_tech=selected_tech,
        all_techs=all_techs,
    )


# --- ROUTE 3: CUSTOMER ANALYTICS ---
@app.route("/customers")
def customer_analytics():
    # Get comprehensive customer LTV data
    customers = calculate_customer_ltv()
    segment_summary = get_segment_summary()

    # Prepare data for segment chart (Pie chart showing customer distribution)
    segment_labels = list(segment_summary.keys())
    segment_counts = [segment_summary[s]["count"] for s in segment_labels]
    segment_revenue = [segment_summary[s]["total_revenue"] for s in segment_labels]

    # Calculate summary stats
    total_customers = len(customers)
    total_ltv = sum(c["total_spend"] for c in customers)
    avg_ltv = total_ltv / total_customers if total_customers > 0 else 0

    # Get at-risk and VIP counts
    at_risk_count = sum(1 for c in customers if c["segment"] == "At-Risk")
    vip_count = sum(1 for c in customers if c["segment"] == "VIP")

    return render_template(
        "customers.html",
        customers=customers,
        segment_summary=segment_summary,
        segment_labels=segment_labels,
        segment_counts=segment_counts,
        segment_revenue=segment_revenue,
        total_customers=total_customers,
        total_ltv=total_ltv,
        avg_ltv=avg_ltv,
        at_risk_count=at_risk_count,
        vip_count=vip_count,
    )


# --- ROUTE 4: ADD APPOINTMENT ---
@app.route("/add", methods=["GET", "POST"])
def add_appointment():
    if request.method == "POST":
        tech_id = request.form["technician_id"]
        service_id = request.form["service_id"]
        c_name = request.form["customer_name"]
        c_phone = request.form["customer_phone"]
        price = float(request.form["price"])
        tip = float(request.form["tip"])

        customer = Customer.query.filter_by(phone=c_phone).first()
        if not customer:
            customer = Customer(first_name=c_name, phone=c_phone)
            db.session.add(customer)
            db.session.commit()

        new_appt = Appointment(
            date_time=datetime.now(),
            customer_id=customer.id,
            technician_id=tech_id,
            service_id=service_id,
            price_charged=price,
            tip_amount=tip,
            payment_method="Cash",
        )
        db.session.add(new_appt)
        db.session.commit()

        flash("✅ Appointment Saved Successfully!")
        return redirect("/appointments")

    technicians = Technician.query.all()
    services = Service.query.all()
    return render_template("add.html", technicians=technicians, services=services)
