from flask import Flask, jsonify
from flask_cors import CORS
from config.config import init_db, db   # chú ý import db

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Khởi tạo DB
init_db(app)


@app.route('/favicon.ico')
def favicon():
    return '', 204   # trả về rỗng, không lỗi 404


# Health check
@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.get("/")
def home():
    return "Welcome to my project"

# Đăng ký blueprint
from routes.user_routes import users_bp
from routes.booking_routes import booking_bp 
from routes.device_routes import devices_bp
from routes.venue_routes import venues_bp
from routes.promotion_routes import promotions_bp
from routes.transaction_routes import transactions_bp
from routes.cart_routes import cart_bp
from routes.ticket_routes import tickets_bp
from routes.momo_routes import momo_bp
from routes.transactions_venue_routes import transactions_venue_bp
from routes.history_routes import history_bp

app.register_blueprint(transactions_venue_bp, url_prefix="/")
app.register_blueprint(momo_bp, url_prefix="/momo")
app.register_blueprint(users_bp, url_prefix="/users") 
app.register_blueprint(booking_bp, url_prefix="/booking")
app.register_blueprint(devices_bp, url_prefix="/devices")
app.register_blueprint(venues_bp, url_prefix="/venues")
app.register_blueprint(promotions_bp, url_prefix="/promotions")
app.register_blueprint(transactions_bp, url_prefix="/transactions")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(tickets_bp, url_prefix="/tickets")
app.register_blueprint(history_bp)


print("\n=== URL MAP ===")
print(app.url_map)
print("===============\n")


if __name__ == "__main__":
    app.run(debug=True)

