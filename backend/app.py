from flask import Flask
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def home():
    return "Trekking App Backend Running!"


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