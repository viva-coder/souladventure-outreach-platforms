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
    """Wipes the old table, recreates it with logo_path, and scans folders."""
    print("--- Starting Database Sync ---")
    conn = get_db()
    cur = conn.cursor()
    
    # 1. FORCE RESET: This fixes the 'logo_path' missing error
    print("Resetting 'nodes' table to fix schema...")
    cur.execute("DROP TABLE IF EXISTS nodes CASCADE;") 
    
    # 2. CREATE NEW TABLE: With the correct columns
    cur.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            category TEXT,
            logo_path TEXT
        );
    """)

    # 3. FOLDER MAPPING: Matches your GitHub structure exactly
    mapping = {
        '01_FB_Groups/NSW': 'NSW',
        '01_FB_Groups/QLD': 'QLD',
        '01_FB_Groups/VIC': 'VIC',
        '01_FB_Groups/General_and_Niche': 'General',
        '01_FB_Groups/Other_States': 'Other',
        '02_Platforms': 'Platform',
        '02_platforms': 'Platform'
    }

    # 4. SCAN FOLDERS
    for folder_rel, cat_label in mapping.items():
        if os.path.exists(folder_rel):
            print(f"Found folder: {folder_rel}")
            for filename in os.listdir(folder_rel):
                if filename.endswith(".md"):
                    node_name = filename.replace(".md", "")
                    
                    # Logic: Looks for "Name.jpg" or "Namelogo.jpg"
                    logo_file = f"{node_name}.jpg"
                    
                    cur.execute("""
                        INSERT INTO nodes (name, category, logo_path)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (name) 
                        DO UPDATE SET category = EXCLUDED.category, logo_path = EXCLUDED.logo_path;
                    """, (node_name, cat_label, logo_file))
                    print(f"  Synced: {node_name}")
    
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
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run sync on local or server startup
    sync_vault() 
    app.run(host='0.0.0.0', port=10000)
