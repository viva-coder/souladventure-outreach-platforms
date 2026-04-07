import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# This pulls the DATABASE_URL automatically from your render.yaml setup
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    url = DATABASE_URL
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, cursor_factory=RealDictCursor)

def sync_vault():
    """Finds your 62+ files and puts them in the database."""
    print("--- Starting Universe Sync ---")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS nodes CASCADE;")
        cur.execute("""
            CREATE TABLE nodes (
                id SERIAL PRIMARY KEY, 
                name TEXT UNIQUE, 
                category TEXT, 
                logo_path TEXT
            );
        """)

        # Scans the folders you have on GitHub
        paths = {
            '01_fb_groups/nsw': 'NSW',
            '01_fb_groups/qld': 'QLD',
            '01_fb_groups/vic': 'VIC',
            '01_fb_groups/general': 'General',
            '02_platforms': 'Platform'
        }

        for path, cat in paths.items():
            if os.path.exists(path):
                print(f"Reading: {path}")
                for f in os.listdir(path):
                    if f.endswith(".md"):
                        name = f.replace(".md", "")
                        cur.execute("INSERT INTO nodes (name, category, logo_path) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (name, cat, f"{name}.jpg"))
        
        conn.commit()
        cur.close()
        conn.close()
        print("--- Sync Complete ---")
    except Exception as e:
        print(f"Sync Error: {e}")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/data')
def get_data():
    """Sends the nodes to the D3 Graph."""
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
