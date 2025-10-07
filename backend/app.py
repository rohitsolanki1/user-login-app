import os, jwt, datetime, psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "appdb")
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "apppass")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "4"))

app = Flask(__name__)
CORS(app)

def get_conn():
    return psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)

@app.route('/api/health')
def health():
    return jsonify({"status":"ok"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message":"username and password required"}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (username,password) VALUES (%s,%s) ON CONFLICT DO NOTHING", (username,password))
            conn.commit()
    return jsonify({"message":"registered"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message":"username and password required"}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT password FROM users WHERE username=%s", (username,))
            row = cur.fetchone()
            if not row or row[0] != password:
                return jsonify({"message":"invalid credentials"}), 401

    payload = {"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXP_HOURS)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return jsonify({"access_token": token})

@app.route('/api/me')
def me():
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        return jsonify({"message":"missing token"}), 401
    token = auth.split(" ",1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"message":"invalid token", "error": str(e)}), 401
    return jsonify({"user": payload["sub"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
