"""
Celery tasks:
  a) send_daily_reminders   – daily email to each user with their booked treks
  b) send_monthly_report    – monthly HTML email to admin
  c) export_booking_csv     – user-triggered async CSV export
"""

import csv
import io
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from app import app, celery
from models import db, User, Trek, Booking


# ─────────────────────────────────────────────
# Helper: send email via SMTP
# ─────────────────────────────────────────────

def _send_email(to_addr, subject, html_body, attachment=None, attachment_name="export.csv"):
    username = app.config.get("MAIL_USERNAME", "")
    password = app.config.get("MAIL_PASSWORD", "")

    if not username or not password:
        # No email credentials configured – just log
        print(f"[EMAIL SKIPPED] To: {to_addr} | Subject: {subject}")
        print("Set MAIL_USERNAME and MAIL_PASSWORD env vars to enable real emails.")
        return False

    msg = MIMEMultipart("mixed")
    msg["From"]    = username
    msg["To"]      = to_addr
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    if attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{attachment_name}"')
        msg.attach(part)

    try:
        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_addr, msg.as_string())
        print(f"[EMAIL SENT] To: {to_addr} | Subject: {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ─────────────────────────────────────────────
# a) Daily Reminders
# ─────────────────────────────────────────────

@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    with app.app_context():
        users = User.query.filter_by(role="user", active=True).all()
        sent = 0

        for user in users:
            bookings = Booking.query.filter_by(user_id=user.id).all()
            if not bookings:
                continue

            rows = ""
            for b in bookings:
                trek = Trek.query.get(b.trek_id)
                if not trek:
                    continue
                staff = User.query.get(trek.staff_id) if trek.staff_id else None
                rows += f"""
                <tr>
                  <td>{trek.trek_name}</td>
                  <td>{trek.location}</td>
                  <td>{trek.difficulty}</td>
                  <td>{trek.duration} days</td>
                  <td>{trek.status}</td>
                  <td>{staff.name if staff else 'Not Assigned'}</td>
                  <td>{b.booking_status}</td>
                </tr>"""

            html = f"""
            <html><body>
            <h2>Hello {user.name},</h2>
            <p>Here is your daily trek reminder from <b>Trekking Management App</b>.</p>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
              <thead style="background:#0d6efd;color:white;">
                <tr>
                  <th>Trek</th><th>Location</th><th>Difficulty</th>
                  <th>Duration</th><th>Trek Status</th><th>Staff</th><th>Booking</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
            <p>Please be prepared and follow all safety guidelines.</p>
            <p>— Trekking Management Team</p>
            </body></html>"""

            if _send_email(user.email, "Your Daily Trek Reminder", html):
                sent += 1

        print(f"[DAILY REMINDERS] Sent to {sent}/{len(users)} users at {datetime.now()}")
        return {"sent": sent, "total_users": len(users)}


# ─────────────────────────────────────────────
# b) Monthly Activity Report
# ─────────────────────────────────────────────

@celery.task(name="tasks.send_monthly_report")
def send_monthly_report():
    with app.app_context():
        now   = datetime.now()
        month = now.strftime("%B %Y")

        all_treks    = Trek.query.all()
        all_bookings = Booking.query.all()
        all_users    = User.query.filter_by(role="user").all()

        completed = [t for t in all_treks if t.status.lower() == "completed"]
        started   = [t for t in all_treks if t.status.lower() == "started"]

        # Participation per trek
        trek_counts = {}
        for b in all_bookings:
            trek_counts[b.trek_id] = trek_counts.get(b.trek_id, 0) + 1

        popular = sorted(trek_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        popular_rows = ""
        for trek_id, count in popular:
            trek = Trek.query.get(trek_id)
            if trek:
                popular_rows += f"<tr><td>{trek.trek_name}</td><td>{trek.location}</td><td>{count}</td></tr>"

        trek_rows = "".join(
            f"<tr><td>{t.trek_name}</td><td>{t.location}</td><td>{t.status}</td></tr>"
            for t in all_treks
        )

        html = f"""
        <html><body>
        <h1 style="color:#0d6efd;">Monthly Trekking Activity Report</h1>
        <h3>{month}</h3>
        <hr>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;margin-bottom:20px;">
          <tr><th>Metric</th><th>Count</th></tr>
          <tr><td>Total Treks</td><td>{len(all_treks)}</td></tr>
          <tr><td>Completed Treks</td><td>{len(completed)}</td></tr>
          <tr><td>Active/Started Treks</td><td>{len(started)}</td></tr>
          <tr><td>Registered Users</td><td>{len(all_users)}</td></tr>
          <tr><td>Total Bookings</td><td>{len(all_bookings)}</td></tr>
        </table>

        <h3>All Treks</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;margin-bottom:20px;">
          <thead style="background:#198754;color:white;">
            <tr><th>Trek Name</th><th>Location</th><th>Status</th></tr>
          </thead>
          <tbody>{trek_rows}</tbody>
        </table>

        <h3>Top 5 Popular Treks (by bookings)</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;">
          <thead style="background:#ffc107;">
            <tr><th>Trek Name</th><th>Location</th><th>Bookings</th></tr>
          </thead>
          <tbody>{popular_rows if popular_rows else '<tr><td colspan="3">No bookings yet</td></tr>'}</tbody>
        </table>

        <p style="margin-top:20px;">Generated on {now.strftime("%d %B %Y at %H:%M")} — Trekking Management System</p>
        </body></html>"""

        admin_email = app.config.get("ADMIN_EMAIL", "admin@trek.com")
        _send_email(admin_email, f"Monthly Trek Report — {month}", html)
        print(f"[MONTHLY REPORT] Generated for {month}")
        return {"month": month, "treks": len(all_treks), "bookings": len(all_bookings)}


# ─────────────────────────────────────────────
# c) Export Booking History as CSV (async)
# ─────────────────────────────────────────────

@celery.task(name="tasks.export_booking_csv", bind=True)
def export_booking_csv(self, user_id):
    with app.app_context():
        user     = User.query.get(user_id)
        bookings = Booking.query.filter_by(user_id=user_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["User ID", "User Name", "Trek Name", "Location",
                         "Difficulty", "Duration (Days)", "Trek Status",
                         "Booking Status", "Booked On"])

        for b in bookings:
            trek = Trek.query.get(b.trek_id)
            if not trek:
                continue
            writer.writerow([
                user.id,
                user.name,
                trek.trek_name,
                trek.location,
                trek.difficulty,
                trek.duration,
                trek.status,
                b.booking_status,
                b.booked_on or "N/A"
            ])

        csv_bytes = output.getvalue().encode("utf-8")

        html = f"""
        <html><body>
        <h2>Hello {user.name},</h2>
        <p>Your trekking booking history export is ready. Please find the CSV attached.</p>
        <p>Total bookings exported: <b>{len(bookings)}</b></p>
        <p>— Trekking Management Team</p>
        </body></html>"""

        sent = _send_email(
            user.email,
            "Your Booking History Export",
            html,
            attachment=csv_bytes,
            attachment_name=f"booking_history_{user_id}.csv"
        )

        print(f"[CSV EXPORT] User {user_id} | Bookings: {len(bookings)} | Email sent: {sent}")
        return {
            "user_id": user_id,
            "bookings": len(bookings),
            "email_sent": sent,
            "task_id": self.request.id
        }
