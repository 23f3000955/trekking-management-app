from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from flask_caching import Cache
from config import Config
from models import db, User, Trek, Booking
from celery_app import make_celery
import io, csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "trek_management_secret_key"

CORS(app, supports_credentials=True)
app.config.from_object(Config)

db.init_app(app)
cache = Cache(app)
celery = make_celery(app)



@app.route("/")
def home():
    return "Trekking App Backend Running!"


# ---------------- ADMIN ----------------

@app.route("/add_trek", methods=["POST"])
def add_trek():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403

    data = request.get_json()

    if not data:
        return jsonify({"message": "Invalid request"}), 400

    if (
        not data.get("trek_name") or
        not data.get("location") or
        not data.get("difficulty") or
        not data.get("duration") or
        not data.get("available_slots")
    ):
        return jsonify({"message": "All fields are required"}), 400

    trek = Trek(
        trek_name=data["trek_name"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration=data["duration"],
        available_slots=data["available_slots"]
    )

    db.session.add(trek)
    db.session.commit()

    cache.delete("all_treks")

    return jsonify({"message": "Trek added successfully"})

@app.route("/treks")
@cache.cached(timeout=300, key_prefix="all_treks")
def get_treks():

    treks = Trek.query.all()
    trek_list = []

    for trek in treks:

        trek_list.append({
            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "slots": trek.available_slots,
            "status": trek.status,
            "staff_id": trek.staff_id
        })

    return jsonify(trek_list)

@app.route("/staff/assigned_treks")
def staff_assigned_treks():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "staff":
        return jsonify({"message": "Access denied"}), 403

    treks = Trek.query.filter_by(staff_id=session["user_id"]).all()

    result = []

    for trek in treks:

        participant_count = Booking.query.filter_by(
            trek_id=trek.id
        ).count()

        result.append({

            "id": trek.id,

            "name": trek.trek_name,

            "location": trek.location,

            "difficulty": trek.difficulty,

            "duration": trek.duration,

            "slots": trek.available_slots,

            "status": trek.status,

            "participants": participant_count

        })

    return jsonify(result)

@app.route("/staff/update_trek/<int:trek_id>", methods=["PUT"])
def update_staff_trek(trek_id):

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "staff":
        return jsonify({"message": "Access denied"}), 403

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.staff_id != session["user_id"]:
        return jsonify({"message": "You are not assigned to this trek"}), 403

    data = request.get_json()

    trek.available_slots = data["slots"]
    trek.status = data["status"]

    db.session.commit()

    return jsonify({

        "message": "Trek updated successfully"

    })

@app.route("/staff/profile")
def staff_profile():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "staff":
        return jsonify({"message": "Access denied"}), 403

    staff = User.query.get(session["user_id"])

    treks = Trek.query.filter_by(staff_id=staff.id).all()

    assigned = []

    for trek in treks:
        assigned.append(trek.trek_name)

    return jsonify({

        "id": staff.id,

        "name": staff.name,

        "email": staff.email,

        "contact": staff.contact,

        "address": staff.address,

        "experience": staff.experience,

        "active": staff.active,

        "treks": assigned

    })




@app.route("/bookings")
def get_bookings():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403

    bookings = Booking.query.all()

    booking_list = []

    for booking in bookings:

        user = User.query.get(booking.user_id)
        trek = Trek.query.get(booking.trek_id)

        booking_list.append({

            "id": booking.id,

            "user_name": user.name if user else "Unknown",

            "trek_name": trek.trek_name if trek else "Unknown",

            "status": booking.booking_status

        })

    return jsonify(booking_list)

# ---------------- USER ----------------

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if (
        not data.get("name") or
        not data.get("email") or
        not data.get("password")
    ):
        return jsonify({"message": "All fields are required"}), 400

    existing_user = User.query.filter_by(email=data["email"]).first()

    if existing_user:
        return jsonify({"message": "User already exists"}), 409

    user = User(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"})


@app.route("/add_staff", methods=["POST"])
def add_staff():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():

        return jsonify({

            "message": "Email already exists"

        }), 400

    staff = User(

        name=data["name"],
        email=data["email"],
        password=data["password"],
        role="staff",
        active=True,

        contact=data.get("contact", ""),
        address=data.get("address", ""),
        experience=data.get("experience", ""),
        emergency_contact=data.get("emergency_contact", "")

    )

    db.session.add(staff)
    db.session.commit()

    return jsonify({

        "message": "Staff added successfully"

    })



@app.route("/staffs")
def get_staffs():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    staffs = User.query.filter_by(role="staff").all()

    result = []

    for staff in staffs:

        assigned = Trek.query.filter_by(staff_id=staff.id).first()

        result.append({

            "id": staff.id,

            "name": staff.name,

            "email": staff.email,

            "contact": staff.contact,

            "address": staff.address,

            "experience": staff.experience,

            "emergency_contact": staff.emergency_contact,

            "assigned_trek": assigned.trek_name if assigned else "Not Assigned",

            "trek_id": assigned.id if assigned else None,

            "active": staff.active

        })

    return jsonify(result)

@app.route("/update_staff/<int:id>", methods=["PUT"])
def update_staff(id):

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    staff = User.query.get(id)

    if not staff or staff.role != "staff":
        return jsonify({"message": "Staff not found"}), 404

    data = request.get_json()

    staff.name = data.get("name", staff.name)
    staff.email = data.get("email", staff.email)

    if data.get("password"):
        staff.password = data["password"]

    staff.contact = data.get("contact", staff.contact)
    staff.address = data.get("address", staff.address)
    staff.experience = data.get("experience", staff.experience)
    staff.emergency_contact = data.get(
        "emergency_contact",
        staff.emergency_contact
    )

    db.session.commit()

    return jsonify({

        "message": "Staff updated successfully"

    })


@app.route("/delete_staff/<int:id>",methods=["DELETE"])
def delete_staff(id):

    if "user_id" not in session:
        return jsonify({"message":"Please login first"}),401

    staff=User.query.get(id)

    if not staff:

        return jsonify({"message":"Staff not found"}),404

    db.session.delete(staff)

    db.session.commit()

    return jsonify({

        "message":"Staff deleted successfully"

    })

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if (
        not data.get("email") or
        not data.get("password")
    ):
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.password != data["password"]:
        return jsonify({"message": "Wrong password"}), 401

    # Check if account is active
    if not user.active:
        return jsonify({
            "message": "Your account has been deactivated by the administrator."
        }), 403

    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({

        "message": "Login successful",
        "user_id": user.id,
        "role": user.role

    })


@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({"message": "Logged out successfully"})


@app.route("/book_trek", methods=["POST"])
def book_trek():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Only trekkers can book treks"}), 403

    data = request.get_json()

    trek = Trek.query.get(data["trek_id"])

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status.lower() != "open":
        return jsonify({"message": "This trek is not open for booking"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available"}), 400

    existing = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing:
        return jsonify({"message": "You have already booked this trek"}), 400

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_status="Booked",
        booked_on=datetime.now().strftime("%Y-%m-%d")
    )

    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()

    return jsonify({
        "message": "Trek booked successfully"
    })


@app.route("/check_login")
def check_login():

    if "user_id" not in session:
        return jsonify({"logged_in": False})

    return jsonify({
        "logged_in": True,
        "user_id": session["user_id"],
        "role": session["role"]
    })


# ---------------- TEMP DEBUG ----------------

@app.route("/test_trek")
def test_trek():

    trek = Trek(
        trek_name="Triund Trek",
        location="Himachal",
        difficulty="Easy",
        duration=3,
        available_slots=25
    )

    db.session.add(trek)
    db.session.commit()

    return "Sample trek added!"


@app.route("/test_register")
def test_register():

    existing_user = User.query.filter_by(email="snigdha@test.com").first()

    if existing_user:
        return "User already exists"

    user = User(
        name="Snigdha",
        email="snigdha@test.com",
        password="1234",
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return "Test user registered!"


@app.route("/all_users")
def all_users():

    users = User.query.all()
    result = []

    for user in users:
        result.append({
            "id": user.id,
            "email": user.email,
            "role": user.role
        })

    return jsonify(result)

# ================= DASHBOARD USERS =================

@app.route("/users")
def get_users():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    users = User.query.all()

    result = []

    for user in users:

        result.append({

            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "active": user.active

        })

    return jsonify(result)



@app.route("/toggle_user_status/<int:user_id>", methods=["PUT"])
def toggle_user_status(user_id):

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Do not allow disabling the admin account
    if user.role == "admin":
        return jsonify({"message": "Admin cannot be deactivated"}), 400

    user.active = not user.active

    db.session.commit()

    return jsonify({

        "message": "Status updated successfully"

    })


@app.route("/user/search")
def user_search():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403

    q = request.args.get("q", "").lower().strip()
    location = request.args.get("location", "").lower().strip()
    difficulty = request.args.get("difficulty", "").lower().strip()
    duration = request.args.get("duration", "").strip()

    treks = Trek.query.all()

    results = []

    for trek in treks:

        if q and q not in trek.trek_name.lower() and q not in trek.location.lower():
            continue

        if location and location != trek.location.lower():
            continue

        if difficulty and difficulty != trek.difficulty.lower():
            continue

        if duration and str(trek.duration) != duration:
            continue

        staff = User.query.get(trek.staff_id) if trek.staff_id else None

        results.append({

            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "slots": trek.available_slots,
            "status": trek.status,
            "staff": staff.name if staff else "Not Assigned"

        })

    return jsonify(results)



@app.route("/user/treks")
def user_treks():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403

    treks = Trek.query.all()

    result = []

    for trek in treks:

        staff = User.query.get(trek.staff_id) if trek.staff_id else None

        result.append({

            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "duration": trek.duration,
            "slots": trek.available_slots,
            "status": trek.status,
            "staff": staff.name if staff else "Not Assigned"

        })

    print("========== USER TREKS ==========")
    print(result)
    print("================================")

    return jsonify(result)
# ---------------- DEFAULT USERS ----------------

@app.route("/delete_trek/<int:trek_id>", methods=["DELETE"])
def delete_trek(trek_id):

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    db.session.delete(trek)
    db.session.commit()

    cache.delete("all_treks")

    return jsonify({"message": "Trek deleted successfully"})

@app.route("/update_trek/<int:trek_id>", methods=["PUT"])
def update_trek(trek_id):

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    data = request.get_json()

    trek.trek_name = data["trek_name"]
    trek.location = data["location"]
    trek.difficulty = data["difficulty"]
    trek.duration = data["duration"]
    trek.available_slots = data["available_slots"]

    db.session.commit()

    cache.delete("all_treks")

    return jsonify({"message": "Trek updated successfully"})


def create_admin():

    admin = User.query.filter_by(email="admin@trek.com").first()

    if not admin:
        admin = User(
            name="Admin",
            email="admin@trek.com",
            password="admin123",
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created!")


def create_staff():

    staff = User.query.filter_by(email="staff1@trek.com").first()

    if not staff:
        staff = User(
            name="Staff One",
            email="staff1@trek.com",
            password="staff123",
            role="staff"
        )

        db.session.add(staff)
        db.session.commit()

        print("Staff created!")



@app.route("/search")
def search():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    keyword = request.args.get("q", "").lower()

    results = []

    users = User.query.all()

    for user in users:

        if (

            keyword in user.name.lower() or
            keyword in user.email.lower()

        ):

            results.append({

                "type": user.role.capitalize(),
                "name": user.name,
                "details": user.email

            })

    treks = Trek.query.all()

    for trek in treks:

        if (

            keyword in trek.trek_name.lower() or
            keyword in trek.location.lower()

        ):

            results.append({

                "type": "Trek",
                "name": trek.trek_name,
                "details": trek.location

            })

    return jsonify(results)


@app.route("/assign_staff", methods=["POST"])
def assign_staff():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()

    trek = Trek.query.get(data.get("trek_id"))

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    trek.staff_id = data.get("staff_id")

    db.session.commit()

    return jsonify({"message": "Staff assigned successfully"})



@app.route("/unassign_staff", methods=["POST"])
def unassign_staff():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()

    trek = Trek.query.get(data.get("trek_id"))

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    trek.staff_id = None

    db.session.commit()

    return jsonify({"message": "Staff unassigned successfully"})

@app.route("/staff/participants")
def staff_participants():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "staff":
        return jsonify({"message": "Access denied"}), 403

    treks = Trek.query.filter_by(staff_id=session["user_id"]).all()

    result = []

    for trek in treks:

        bookings = Booking.query.filter_by(
            trek_id=trek.id
        ).all()

        for booking in bookings:

            user = User.query.get(booking.user_id)

            result.append({

                "booking_id": booking.id,

                "trek_name": trek.trek_name,

                "name": user.name,

                "email": user.email,

                "status": booking.booking_status

            })

    return jsonify(result)

@app.route("/user/bookings")
def user_bookings():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    print("========== USER BOOKINGS ==========")
    print("User ID:", session["user_id"])
    print("Bookings Found:", len(bookings))

    result = []

    for booking in bookings:

        trek = Trek.query.get(booking.trek_id)

        if trek:

            staff = User.query.get(trek.staff_id) if trek.staff_id else None

            result.append({

                "booking_id": booking.id,

                "trek_name": trek.trek_name,

                "location": trek.location,

                "difficulty": trek.difficulty,

                "duration": trek.duration,

                "status": trek.status,

                "booking_status": booking.booking_status,

                "staff": staff.name if staff else "Not Assigned"

            })

    print(result)
    print("===================================")

    return jsonify(result)
@app.route("/user/dashboard")
def user_dashboard():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    total_bookings = len(bookings)

    active_treks = 0
    completed_treks = 0

    for booking in bookings:

        trek = Trek.query.get(booking.trek_id)

        if trek:

            if trek.status.lower() in ["open", "started"]:

                active_treks += 1

            elif trek.status.lower() == "completed":

                completed_treks += 1

    return jsonify({

        "total_bookings": total_bookings,

        "active_treks": active_treks,

        "completed_treks": completed_treks

    })


@app.route("/user/profile", methods=["GET", "PUT"])
def user_profile():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403

    user = User.query.get(session["user_id"])

    if request.method == "PUT":

        data = request.get_json()

        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        user.contact = data.get("contact", user.contact)
        user.address = data.get("address", user.address)

        db.session.commit()

        return jsonify({
            "message": "Profile updated successfully"
        })

    return jsonify({

        "id": user.id,
        "name": user.name,
        "email": user.email,
        "contact": user.contact,
        "address": user.address,
        "active": user.active

    })
@app.route("/user/export_bookings")
def export_bookings_download():
    """Instant CSV download for the logged-in user."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401
    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403
    user     = User.query.get(session["user_id"])
    bookings = Booking.query.filter_by(user_id=user.id).all()
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
            user.id, user.name, trek.trek_name, trek.location,
            trek.difficulty, trek.duration, trek.status,
            b.booking_status, b.booked_on or "N/A"
        ])
    mem = io.BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"bookings_{user.id}.csv"
    )
@app.route("/user/export_bookings_async", methods=["POST"])
def export_bookings_async():
    """Queue a Celery CSV export task; email sent on completion."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401
    if session["role"] != "user":
        return jsonify({"message": "Access denied"}), 403
    from tasks import export_booking_csv
    task = export_booking_csv.delay(session["user_id"])
    return jsonify({
        "message": "Export queued! You will receive an email when it is ready.",
        "task_id": task.id
    })


@app.route("/user/export_status/<task_id>")
def export_task_status(task_id):
    """Poll Celery task state."""
    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401
    from celery.result import AsyncResult
    result = AsyncResult(task_id, app=celery)
    return jsonify({
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    })



def _schedule_or_send(task, job_label):
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")

    scheduled_time = (request.get_json(silent=True) or {}).get("scheduled_time")

    if scheduled_time:
        try:
            run_at = datetime.fromisoformat(scheduled_time).replace(tzinfo=IST)
        except ValueError:
            return jsonify({"message": "Invalid scheduled time"}), 400

        countdown = (run_at - datetime.now(IST)).total_seconds()

        if countdown <= 0:
            return jsonify({"message": "Scheduled time must be in the future"}), 400

        result = task.apply_async(countdown=countdown)

        return jsonify({
            "message": f"{job_label} scheduled for {scheduled_time}",
            "task_id": result.id
        })

    result = task.delay()

    return jsonify({
        "message": f"{job_label} sent instantly",
        "task_id": result.id
    })


@app.route("/admin/trigger_reminders", methods=["POST"])
def trigger_reminders():
    if "user_id" not in session or session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403
    from tasks import send_daily_reminders
    return _schedule_or_send(send_daily_reminders, "Daily reminders")


@app.route("/admin/trigger_monthly_report", methods=["POST"])
def trigger_monthly_report():
    if "user_id" not in session or session["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403
    from tasks import send_monthly_report
    return _schedule_or_send(send_monthly_report, "Monthly report")


def migrate_db():
    import sqlite3, os
    db_path = os.path.join(os.path.dirname(__file__), "instance", "trekking.db")
    try:
        conn = sqlite3.connect(db_path)
        cur  = conn.cursor()
        cur.execute("PRAGMA table_info(booking)")
        cols = [row[1] for row in cur.fetchall()]
        if "booked_on" not in cols:
            cur.execute("ALTER TABLE booking ADD COLUMN booked_on TEXT DEFAULT ''")
            conn.commit()
            print("Migration: added booked_on column")
        conn.close()
    except Exception as e:
        print(f"Migration skipped: {e}")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        migrate_db()
        create_admin()
        create_staff()
    app.run(debug=True)
