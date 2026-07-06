from flask import Flask, request, jsonify, session
from flask_cors import CORS
from config import Config
from models import db, User, Trek, Booking

app = Flask(__name__)
app.secret_key = "trek_management_secret_key"

CORS(app, supports_credentials=True)
app.config.from_object(Config)

db.init_app(app)


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

    return jsonify({"message": "Trek added successfully"})


@app.route("/treks")
def get_treks():

    treks = Trek.query.all()
    trek_list = []

    for trek in treks:
        trek_list.append({
            "id": trek.id,
            "name": trek.trek_name,
            "location": trek.location,
            "difficulty": trek.difficulty,
            "slots": trek.available_slots,
            "status": trek.status
        })

    return jsonify(trek_list)


@app.route("/bookings")
def get_bookings():

    if "user_id" not in session:
        return jsonify({"message": "Please login first"}), 401

    if session["role"] != "admin":
        return jsonify({"message": "Access denied. Admin only."}), 403

    bookings = Booking.query.all()
    booking_list = []

    for booking in bookings:
        booking_list.append({
            "booking_id": booking.id,
            "user_id": booking.user_id,
            "trek_id": booking.trek_id,
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

    if not data:
        return jsonify({"message": "Invalid request"}), 400

    if not data.get("trek_id"):
        return jsonify({"message": "Trek ID is required"}), 400

    booking = Booking(
        user_id=session["user_id"],
        trek_id=data["trek_id"]
    )

    db.session.add(booking)
    db.session.commit()

    return jsonify({"message": "Trek booked successfully"})

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

    return jsonify({"message": "Trek deleted successfully"})




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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
        create_staff()

    app.run(debug=True)