# SYNTHETIC FIXTURE - intentionally unsafe, do not deploy.
import pickle
import subprocess
from flask import Flask, request

app = Flask(__name__)
DATABASE_URL = "postgres://appuser:hunter2hunter2@db.internal:5432/app"
JWT_SECRET = "supersecret"
ADMIN = {"password": "admin"}

@app.route("/user")
def user():
    uid = request.args["id"]
    cur = db.execute(f"SELECT * FROM users WHERE id = {uid}")
    return str(cur.fetchall())

@app.route("/run")
def run():
    return subprocess.check_output(request.args["cmd"], shell=True)

@app.route("/load", methods=["POST"])
def load():
    return str(pickle.loads(request.data))

if __name__ == "__main__":
    app.run(debug=True)
