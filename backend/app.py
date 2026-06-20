from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Trek, Booking

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return "Trekking App Backend Running!"


@app.route("/add_trek", methods=["POST"])
def add_trek():
    data = request.json

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


@app.route("/book_trek")
def book_trek():
    booking = Booking(
        user_id=1,
        trek_id=1
    )

    db.session.add(booking)
    db.session.commit()

    return "Trek booked successfully!"


@app.route("/bookings")
def get_bookings():
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


@app.route("/register", methods=["POST"])
def register():
    data = request.json

    existing_user = User.query.filter_by(email=data["email"]).first()

    if existing_user:
        return jsonify({"message": "User already exists"})

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
    data = request.json

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"message": "User not found"})

    if user.password != data["password"]:
        return jsonify({"message": "Wrong password"})

    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role
    })


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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()

    app.run(debug=True)