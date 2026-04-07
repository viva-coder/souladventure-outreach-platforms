import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify
from flask_basicauth import BasicAuth
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Security & DB Config
app.config['BASIC_AUTH_USERNAME'] = os.environ.get('WEB_USER', 'admin')
app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('WEB_PASS', 'password')
basic_auth = BasicAuth(app)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    url = DATABASE_URL
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def sync_vault():
    """Simple sync for renamed lowercase folders."""
    print("--- Starting Clean Folder Sync ---")
    conn = get_db()
    cur = conn.cursor()
    
    # 1. Reset the table to make sure everything is fresh
    cur.execute("DROP TABLE IF EXISTS nodes CASCADE;") 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            logo_path TEXT
        );
    """)

    # 2. These paths now match your renamed GitHub folders exactly
    paths = {
        '01_fb_groups/nsw': 'NSW',
        '01_fb_groups/qld': 'QLD',
        '01_fb_groups/vic': 'VIC',
        '01_fb_groups/general': 'General',
        '01_fb_groups/other': 'Other',
        '02_platforms': 'Platform'
    }

    for path, cat_label in paths.items():
        if os.path.exists(path):
            print(f"✅ Syncing Folder: {path}")
            for filename in os.listdir(path):
                if filename.endswith(".md"):
                    node_name = filename.replace(".md", "")
                    logo_file = f"{node_name}.jpg"
                    
                    cur.execute("""
                        INSERT INTO nodes (name, category, logo_path)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (name) DO NOTHING;
                    """, (node_name, cat_label, logo_file))
                    print(f"   + Added: {node_name}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("--- Sync Complete ---")

@app.route('/')
@basic_auth.required
def index():
    return render_template("index.html")

@app.route('/api/data')
def get_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, category, logo_path FROM nodes")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    nodes = [{"id": "SoulAdventure", "group": "Center"}]
    links = []
    for r in rows:
        nodes.append({"id": r['name'], "group": r['category'], "logo": r['logo_path']})
        links.append({"source": "SoulAdventure", "target": r['name']})
    return jsonify({"nodes": nodes, "links": links})

if __name__ == '__main__':
    sync_vault() 
    app.run(host='0.0.0.0', port=10000)
