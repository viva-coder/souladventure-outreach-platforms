import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    url = DATABASE_URL
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def sync_vault():
    """Scans GitHub folders and populates the Database."""
    print("--- Starting Universe Sync ---")
    conn = get_db()
    cur = conn.cursor()
    
    # Create table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            url TEXT,
            members TEXT,
            notes TEXT
        );
    """)

    # Mapping local folders to your HTML categories
    paths = {
        '01_fb_groups/nsw': 'fb_nsw',
        '01_fb_groups/qld': 'fb_qld',
        '01_fb_groups/vic': 'fb_vic',
        '01_fb_groups/general': 'fb_general',
        '01_fb_groups/other': 'fb_other',
        '02_platforms': 'platform'
    }

    for path, cat_label in paths.items():
        if os.path.exists(path):
            print(f"Syncing: {path}")
            for filename in os.listdir(path):
                if filename.endswith(".md"):
                    node_name = filename.replace(".md", "")
                    # Insert only if it doesn't exist so we don't overwrite manual edits
                    cur.execute("""
                        INSERT INTO nodes (name, category)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING;
                    """, (node_name, cat_label))
    
    conn.commit()
    cur.close()
    conn.close()
    print("--- Sync Complete ---")

@app.route('/')
def index():
    return render_template("index.html")

# --- API ROUTES ---

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM nodes ORDER BY name ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route('/api/nodes', methods=['POST'])
def add_node():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO nodes (name, category, url, members, notes)
        VALUES (%s, %s, %s, %s, %s) RETURNING *
    """, (data['name'], data['category'], data.get('url'), data.get('members'), data.get('notes')))
    new_node = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(new_node)

@app.route('/api/nodes/<int:id>', methods=['PUT'])
def update_node(id):
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE nodes SET name=%s, category=%s, url=%s, members=%s, notes=%s
        WHERE id=%s RETURNING *
    """, (data['name'], data['category'], data.get('url'), data.get('members'), data.get('notes'), id))
    updated_node = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(updated_node)

@app.route('/api/nodes/<int:id>', methods=['DELETE'])
def delete_node(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM nodes WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    sync_vault() # Run sync on startup
    app.run(host='0.0.0.0', port=10000)
