# SoulAdventure Outreach Universe

Interactive knowledge graph of all 62 FB groups + retreat platforms.

## Features
- 🌐 Force-directed D3 graph — drag, zoom, pan
- 🔍 Search + filter by category/region  
- 🖱️ Click any node to open its side panel
- ✏️ Edit node details, URL, notes in-browser
- ➕ Add new nodes from the browser
- 🗑️ Delete nodes
- 💾 All data saved to PostgreSQL (persists forever)

## Deploy to Render (one-click)

1. Push all these files to your GitHub repo root
2. Go to [render.com](https://render.com) → New → **Blueprint**
3. Connect your GitHub repo → Render detects `render.yaml` automatically
4. Click **Apply** — it creates both the web service AND the database
5. Wait ~3 minutes → your URL is live ✨

## Manual Render setup (if Blueprint doesn't work)

### Step 1: Create PostgreSQL database
- Render dashboard → New → PostgreSQL
- Name: `souladventure-db`
- Plan: Free
- Copy the **Internal Database URL**

### Step 2: Create Web Service
Fill the form like this:

| Field | Value |
|-------|-------|
| **Name** | `souladventure-outreach` |
| **Language** | Python 3 |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Instance Type** | Free |

### Step 3: Add environment variable
- Key: `DATABASE_URL`
- Value: paste the Internal Database URL from Step 1

### Step 4: Deploy
Click **Create Web Service** — done!

## Local development

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:pass@localhost/souladventure"
python app.py
# → open http://localhost:5000
```
