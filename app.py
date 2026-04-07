import os, json
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
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
    # Seed initial data if empty
    cur.execute("SELECT COUNT(*) as c FROM nodes;")
    count = cur.fetchone()["c"]
    if count == 0:
        seed_data = [
            # Platforms
            ("BookRetreats", "platform", None, "https://bookretreats.com", None, "Top retreat booking platform"),
            ("Retreat Guru", "platform", None, "https://retreat.guru", None, "Holistic retreat listings"),
            ("Tripaneer", "platform", None, "https://tripaneer.com", None, "Yoga & wellness travel"),
            ("Conscious City Guide", "platform", None, "https://consciouscityguide.com", None, "Conscious living directory"),
            ("Destination Deluxe", "platform", None, "https://destinationdeluxe.com", None, "Luxury wellness travel"),
            ("Mindtrip", "platform", None, "https://mindtrip.com", None, "Mindful travel experiences"),
            ("The Good Index", "platform", None, "https://thegoodindex.com", None, "Ethical & sustainable travel"),
            ("Tribu", "platform", None, "https://tribu.com", None, "Wellness community platform"),
            # General & Niche FB Groups
            ("Conscious Retreats Worldwide", "fb_general", "General", "https://facebook.com/groups/consciousretreatsworldwide", None, None),
            ("Japanese Yoga Australia", "fb_general", "General", None, None, None),
            ("Online Yoga and Wellness Classes", "fb_general", "General", None, None, None),
            ("Reciprocity Group", "fb_general", "General", None, None, None),
            ("RetreatHub Professionals", "fb_general", "General", None, None, None),
            ("The Yoga of Birth", "fb_general", "General", None, None, None),
            ("Yin Yoga Australia", "fb_general", "General", None, None, None),
            ("Yoga and Meditation Retreats in Australia", "fb_general", "General", None, None, None),
            ("Yoga Education Resources Australia", "fb_general", "General", None, None, None),
            ("Yoga Meditation & Wellbeing", "fb_general", "General", None, None, None),
            ("Yoga Retreat Leaders", "fb_general", "General", None, None, None),
            ("Yoga Retreats Worldwide", "fb_general", "General", None, None, None),
            ("Yoga Teachers", "fb_general", "General", None, None, None),
            # NSW
            ("Acro Yoga Central Coast", "fb_nsw", "NSW", None, None, None),
            ("Acro Yoga Newcastle", "fb_nsw", "NSW", None, None, None),
            ("Acro Yoga Sydney", "fb_nsw", "NSW", None, None, None),
            ("Blue Mountains Yoga Teachers", "fb_nsw", "NSW", None, None, None),
            ("Central Coast Yoga Community", "fb_nsw", "NSW", None, None, None),
            ("Coffs Coast Yoga Teachers", "fb_nsw", "NSW", None, None, None),
            ("Milton Ulladulla Yoga and Natural Movement", "fb_nsw", "NSW", None, None, None),
            ("South Coast Yoga Teachers", "fb_nsw", "NSW", None, None, None),
            ("Spiritual Living Sydney - CC - Newcastle", "fb_nsw", "NSW", None, None, None),
            ("Sydney Wellness Coaching", "fb_nsw", "NSW", None, None, None),
            ("Sydney Yoga Instructors", "fb_nsw", "NSW", None, None, None),
            ("Sydney Yoga Teachers", "fb_nsw", "NSW", None, None, None),
            ("Thriving Illawarra Community", "fb_nsw", "NSW", None, None, None),
            ("Vegan Yogis and Teachers of Newcastle", "fb_nsw", "NSW", None, None, None),
            ("Wollongong Wellness Guide", "fb_nsw", "NSW", None, None, None),
            ("Wollongong Yoga teachers", "fb_nsw", "NSW", None, None, None),
            ("YOGA COLLECTIVE Sydney to South Coast", "fb_nsw", "NSW", None, None, None),
            ("Yoga Sydney", "fb_nsw", "NSW", None, None, None),
            # QLD
            ("Acroyoga Byron Bay", "fb_qld", "QLD", None, None, None),
            ("Brisbane Yoga Community", "fb_qld", "QLD", None, None, None),
            ("Brisbane Yoga Teachers", "fb_qld", "QLD", None, None, None),
            ("Byron Bay & Queensland", "fb_qld", "QLD", None, None, None),
            ("Byron Bay Yoga Teachers", "fb_qld", "QLD", None, None, None),
            ("Byron Bay Yoga Tribe", "fb_qld", "QLD", None, None, None),
            ("Gold Coast Yoga Teachers and Trainees", "fb_qld", "QLD", None, None, None),
            ("Gold Coast Yoga Teachers", "fb_qld", "QLD", None, None, None),
            ("Kundalini yoga teachers network SE QLD", "fb_qld", "QLD", None, None, None),
            ("Noosa Yoga Community", "fb_qld", "QLD", None, None, None),
            ("Queensland Yoga Group", "fb_qld", "QLD", None, None, None),
            ("Toowoomba Yoga Collective", "fb_qld", "QLD", None, None, None),
            ("Townsville Yoga Teachers", "fb_qld", "QLD", None, None, None),
            # VIC
            ("AcroYoga Melbourne", "fb_vic", "VIC", None, None, None),
            ("Melbourne Yoga Teachers Unite", "fb_vic", "VIC", None, None, None),
            ("Melbourne Yoga Teachers", "fb_vic", "VIC", None, None, None),
            ("Mornington Peninsula Yoga Network", "fb_vic", "VIC", None, None, None),
            ("Mornington Peninsula Yoga Teachers", "fb_vic", "VIC", None, None, None),
            # Other States
            ("Adelaide Yoga Teacher Network", "fb_other", "Other", None, None, None),
            ("Adelaide Yoga Teachers", "fb_other", "Other", None, None, None),
            ("Awakening the Divine Fire Australia", "fb_other", "Other", None, None, None),
            ("Canberra Yoga Scene", "fb_other", "Other", None, None, None),
            ("Darwin Yoga Community", "fb_other", "Other", None, None, None),
            ("Darwin Yoga Teachers", "fb_other", "Other", None, None, None),
            ("Denmark Australia Yoga Community", "fb_other", "Other", None, None, None),
            ("Yoga in Mparntwe Alice Springs", "fb_other", "Other", None, None, None),
            ("Yoga Instructors of Canberra", "fb_other", "Other", None, None, None),
            ("Yoga Teachers in Darwin", "fb_other", "Other", None, None, None),
            ("Yoga Teachers Perth WA", "fb_other", "Other", None, None, None),
        ]
        cur.executemany(
            "INSERT INTO nodes (name, category, region, url, members, notes) VALUES (%s,%s,%s,%s,%s,%s)",
            seed_data
        )
    conn.commit()
    cur.close()
    conn.close()

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
