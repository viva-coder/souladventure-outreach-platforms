import os
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_basicauth import BasicAuth
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

# 1. Page Password Configuration
# On Render, add WEB_USER and WEB_PASS to your Environment Variables
app.config['BASIC_AUTH_USERNAME'] = os.environ.get('WEB_USER', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('WEB_PASS', 'soul-secure-123')
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

# 2. Database Connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    # If the URL starts with 'postgres://', we fix it for SQLAlchemy/Psycopg2 compatibility
    url = DATABASE_URL
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Create the table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            region TEXT,
            url TEXT,
            members TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """)
    
    # Check if we need to seed
    cur.execute("SELECT COUNT(*) as c FROM nodes;")
    count = cur.fetchone()["c"]
    
    if count == 0:
        seed_data = [
            ("BookRetreats", "platform", None, "https://bookretreats.com", None, "Top retreat booking platform"),
            ("Retreat Guru", "platform", None, "https://retreat.guru", None, "Holistic retreat listings"),
            ("Tripaneer", "platform", None, "https://tripaneer.com", None, "Yoga & wellness travel"),
            ("Conscious City Guide", "platform", None, "https://consciouscityguide.com", None, "Conscious living directory"),
            ("Destination Deluxe", "platform", None, "https://destinationdeluxe.com", None, "Luxury wellness travel"),
            ("Mindtrip", "platform", None, "https://mindtrip.com", None, "Mindful travel experiences"),
            ("The Good Index", "platform", None, "https://thegoodindex.com", None, "Ethical & sustainable travel"),
            ("Tribu", "platform", None, "https://tribu.com", None, "Wellness community platform"),
            ("Conscious Retreats Worldwide", "fb_general", "General", "https://facebook.com/groups/consciousretreatsworldwide", None, None),
            # ... all your other 62 nodes stay here ...
            ("Yoga Teachers Perth WA", "fb_other", "Other", None, None, None)
        ]
        cur.executemany(
            "INSERT INTO nodes (name, category, region, url, members, notes) VALUES (%s,%s,%s,%s,%s,%s)",
            seed_data
        )
    
    conn.commit()
    cur.close()
    conn.close()

# 3. Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/nodes", methods=["GET"])
def get_nodes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM nodes ORDER BY category, name;")
    nodes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(n) for n in nodes])

@app.route("/api/nodes", methods=["POST"])
def create_node():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nodes (name, category, region, url, members, notes) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *;",
        (data["name"], data["category"], data.get("region"), data.get("url"), data.get("members"), data.get("notes"))
    )
    node = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(node), 201

@app.route("/api/nodes/<int:node_id>", methods=["PUT"])
def update_node(node_id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """UPDATE nodes SET name=%s, category=%s, region=%s, url=%s, members=%s, notes=%s, updated_at=NOW()
           WHERE id=%s RETURNING *;""",
        (data["name"], data["category"], data.get("region"), data.get("url"), data.get("members"), data.get("notes"), node_id)
    )
    node = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(dict(node))

@app.route("/api/nodes/<int:node_id>", methods=["DELETE"])
def delete_node(node_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE id=%s;", (node_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"deleted": node_id})

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)