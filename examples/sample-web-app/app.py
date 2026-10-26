# SYNTHETIC DEMO - intentionally vulnerable. Do not deploy.
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-123"
db = sqlite3.connect("shop.db", check_same_thread=False)

@app.route("/api/orders/<order_id>")
def get_order(order_id):
    # no authentication, no ownership check
    row = db.execute("SELECT * FROM orders WHERE id = " + order_id).fetchone()
    return jsonify(row)

@app.route("/api/profile", methods=["POST"])
def update_profile():
    data = request.get_json()
    db.execute("UPDATE users SET " + ", ".join(f"{k} = '{v}'" for k, v in data.items()) + " WHERE id = 1")
    return jsonify(ok=True)

@app.route("/admin")
def admin():
    return "admin panel"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
