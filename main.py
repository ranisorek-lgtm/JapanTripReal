from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import os
import json

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trip_data.json")

# מבנה ברירת המחדל המלא של הנתונים
DEFAULT_TRIP_DATA = {
    "flights": [
        {"id": "f1", "name": "טיסות בינלאומיות (תל אביב - אוסקה הלוך ושוב)", "price_ils": 17300.0}
    ],
    "hotels": [
        {"id": "h1", "name": "Keio Plaza Hotel Sapporo (11.9–14.9)", "price_ils": 2290.0, "address": "2 Chome-2-1 Kita 5 Jonishi, Chuo Ward, Sapporo, Hokkaido 060-0005, Japan"},
        {"id": "h2", "name": "Yutorelo Toyako (14.9–15.9)", "price_ils": 542.0, "address": "68-1 Maruyama, Abuta-gun, Toyako-cho, Hokkaido 049-5721, Japan"},
        {"id": "h3", "name": "Daiwa Roynet Hotel Aomori (15.9–18.9)", "price_ils": 1015.0, "address": "1 Chome-1-23 Shinmachi, Aomori, 030-0801, Japan"},
        {"id": "h4", "name": "Tokyu Stay Aoyama Premier (18.9–23.9)", "price_ils": 3168.0, "address": "2 Chome-7-18 Minamiaoyama, Minato City, Tokyo 107-0062, Japan"},
        {"id": "h8", "name": "Takayama Ouan - פמילי רום עם ארוחת בוקר (23.9–24.9) [הוזמן ב-32,071 מיילים]", "price_ils": 0.0, "address": "4 Chome-327 Hanakokuracho, Takayama, Gifu 506-0007, Japan"},
        {"id": "h5", "name": "Hotel and spa gift Takayama (24.9–26.9)", "price_ils": 813.0, "address": "6 Chome-888-1 Nishinoisshicho, Takayama, Gifu 506-0031, Japan"},
        {"id": "h6", "name": "Hotel Gracery Kyoto Sanjo (26.9–1.10)", "price_ils": 2015.0, "address": "420 Nakajimacho, Nakagyo Ward, Kyoto, 604-8032, Japan"},
        {"id": "h7", "name": "Oyado Nono Namba Natural Hot Spring (1.10–4.10)", "price_ils": 2603.0, "address": "1 Chome-4-17 Nipponbashi, Chuo Ward, Osaka, 542-0073, Japan"},
    ],
    "trains": [
        {"id": "t1", "name": "סאפורו <== אגם טויה (14.9)", "price_ils": 270.19},
        {"id": "t2", "name": "אגם טויה ==> אאומורי (15.9 - מקטע 1)", "price_ils": 219.68},
        {"id": "t3", "name": "אגם טויה ==> אאומורי (15.9 - מקטע 2)", "price_ils": 317.04},
        {"id": "t4", "name": "אאומורי ==> טוקיו (18.9)", "price_ils": 376.34},
        {"id": "t5", "name": "טוקיו ==> טאקאיאמה (23.9)", "price_ils": 346.15},
        {"id": "t6", "name": "טאקאיאמה ==> קיוטו (26.9)", "price_ils": 230.74},
        {"id": "t7", "name": "קיוטו ==> אוסקה (1.10)", "price_ils": 31.04},
    ],
    "checklists": {},
    "attractions": {
        "סאפורו": [
            {"id": "a1", "name": "פארק אודורי (Odori Park)", "price_ils": 0, "desc": "שדרה ירוקה וארוכה החוצה את מרכז העיר.", "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"},
            {"id": "a2", "name": "הר מואיווה (Mount Moiwa)", "price_ils": 52, "desc": "תצפית מרהיבה על העיר בלילה.", "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"}
        ],
        "אגם טויה": [
            {"id": "a7", "name": "רכבל הר אוסו (Usuzan Ropeway)", "price_ils": 47, "desc": "נקודת תצפית מרהיבה על האגם.", "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"}
        ],
        "אאומורי": [
            {"id": "a11", "name": "מרכז Nokkedon", "price_ils": 50, "desc": "חוויה קולינרית ייחודית של קערת דגים בהרכבה אישית.", "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"}
        ],
        "טוקיו": [
            {"id": "a16", "name": "מקדש Meiji Shrine", "price_ils": 0, "desc": "הליכה מרגיעה בתוך יער עבות בלב העיר.", "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"}
        ],
        "טאקאיאמה": [
            {"id": "a24", "name": "קאמיקוצ'י (Kamikochi)", "price_ils": 60, "desc": "עמק אלפיני עצום המוקף בפסגות מחודדות.", "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"}
        ],
        "קיוטו": [
            {"id": "a29", "name": "Arashiyama Bamboo Grove", "price_ils": 0, "desc": "שבילי הליכה מוקפים עצי במבוק עצומים.", "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"}
        ],
        "אוסקה": [
            {"id": "a33", "name": "Dotonbori", "price_ils": 0, "desc": "שדרה צבעונית ורועשת עם אוכל רחוב מעולה.", "img": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=500"}
        ]
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # וידוא שכל המפתחות הראשיים קיימים
                for key in DEFAULT_TRIP_DATA:
                    if key not in data:
                        data[key] = DEFAULT_TRIP_DATA[key]
                return data
        except Exception as e:
            print(f"Error loading data: {e}. Using defaults.")
            return DEFAULT_TRIP_DATA
    else:
        save_data(DEFAULT_TRIP_DATA)
        return DEFAULT_TRIP_DATA

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data successfully saved to {DATA_FILE}")
    except Exception as e:
        print(f"Error saving data: {e}")

app = Flask(__name__)

LAYOUT = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תכנון טיול ליפן 🇯🇵</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#6366f1">
    <style>
        :root {
            --bg-color: #0b0c10; --card-bg: #14151b; --border-color: #272935;
            --text-color: #f4f4f5; --text-muted: #94a3b8; --accent-color: #6366f1;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --success-color: #10b981; --danger-color: #ef4444;
        }
        body { font-family: sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: var(--card-bg); padding: 20px; border-radius: 16px; border: 1px solid var(--border-color); }
        nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-bottom: 20px; background: #0f1015; padding: 8px; border-radius: 10px; }
        nav a { color: var(--text-muted); text-decoration: none; padding: 8px 12px; border-radius: 8px; font-weight: 600; font-size: 14px; }
        nav a:hover { color: #fff; background: rgba(99, 102, 241, 0.15); }
        table { width: 100%; border-collapse: collapse; background: #111218; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; border-bottom: 1px solid var(--border-color); text-align: right; }
        th { background: #181922; color: #fff; }
        input[type="number"], input[type="text"] { padding: 8px; background: #0b0c10; border: 1px solid var(--border-color); color: #fff; border-radius: 6px; }
        button { background: var(--accent-gradient); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .total-box { background: #111218; border: 1px solid var(--border-color); padding: 20px; border-radius: 12px; text-align: center; font-size: 24px; font-weight: bold; color: var(--success-color); margin-top: 20px; }
    </style>
</head>
<body>
<div class="container">
    <nav>
        <a href="/">דף הבית</a>
        <a href="/stays">טיסות ומלונות</a>
        <a href="/trains">רכבות</a>
        <a href="/attractions">אטרקציות</a>
        <a href="/checklists">צ'ק-ליסט</a>
    </nav>
    {{ content | safe }}
</div>
</body>
</html>
"""

@app.route('/')
def index():
    trip_data = load_data()
    total = (
        sum(item['price_ils'] for item in trip_data.get('trains', [])) +
        sum(item['price_ils'] for item in trip_data.get('hotels', [])) +
        sum(item['price_ils'] for item in trip_data.get('flights', [])) +
        sum(item['price_ils'] for city_attrs in trip_data.get('attractions', {}).values() for item in city_attrs)
    )
    content = f"""
    <h1>טיול ליפן 2026 🇯🇵</h1>
    <p style="text-align: center; color: var(--text-muted);">מערכת לניהול תקציב ומסלול הטיול.</p>
    <div class="total-box">סך הכל כללי משוער: ₪{total:,.2f}</div>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/stays')
def stays():
    trip_data = load_data()
    content = "<h2>טיסות ומלונות</h2>"
    content += "<h3>טיסות</h3><ul>"
    for f in trip_data.get('flights', []):
        content += f"<li>{f['name']} - ₪{f['price_ils']}</li>"
    content += "</ul><h3>מלונות</h3><ul>"
    for h in trip_data.get('hotels', []):
        content += f"<li>{h['name']} - ₪{h['price_ils']}</li>"
    content += "</ul>"
    return render_template_string(LAYOUT, content=content)

@app.route('/trains', methods=['GET', 'POST'])
def trains():
    trip_data = load_data()
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('train_'):
                tid = key.replace('train_', '')
                try:
                    val_float = float(value)
                    for t in trip_data['trains']:
                        if t['id'] == tid:
                            t['price_ils'] = val_float
                except ValueError:
                    continue
        save_data(trip_data)
        return redirect(url_for('trains'))

    rows = "".join([f"<tr><td>{t['name']}</td><td><input type='number' step='0.01' name='train_{t['id']}' value='{t['price_ils']}'></td></tr>" for t in trip_data.get('trains', [])])
    content = f"""
    <h2>ניהול רכבות</h2>
    <form method="POST">
        <table>
            <tr><th>קו רכבת</th><th>מחיר ב-₪</th></tr>
            {rows}
        </table>
        <button type="submit">שמור שינויים</button>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/attractions', methods=['GET', 'POST'])
def attractions():
    trip_data = load_data()
    if request.method == 'POST':
        for key, value in request.form.items():
            if key.startswith('attr_'):
                aid = key.replace('attr_', '')
                try:
                    val_float = float(value)
                    for city_attrs in trip_data['attractions'].values():
                        for a in city_attrs:
                            if a['id'] == aid:
                                a['price_ils'] = val_float
                except ValueError:
                    continue
        save_data(trip_data)
        return redirect(url_for('attractions'))

    attrs_html = ""
    for city, attrs in trip_data.get('attractions', {}).items():
        attrs_html += f"<h3>📍 {city}</h3><table><tr><th>אטרקציה</th><th>מחיר ב-₪</th></tr>"
        for a in attrs:
            attrs_html += f"<tr><td>{a['name']}</td><td><input type='number' step='0.01' name='attr_{a['id']}' value='{a['price_ils']}'></td></tr>"
        attrs_html += "</table>"

    content = f"""
    <h2>אטרקציות</h2>
    <form method="POST">
        {attrs_html}
        <button type="submit">שמור שינויים</button>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/checklists', methods=['GET', 'POST'])
def checklists():
    trip_data = load_data()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_list':
            title = request.form.get('list_title', '').strip()
            if title:
                new_id = 'c_' + os.urandom(3).hex()
                trip_data['checklists'][new_id] = {"title": title, "items": []}
                save_data(trip_data)
        elif action == 'add_item':
            cid = request.form.get('list_id')
            text = request.form.get('item_text', '').strip()
            if cid in trip_data['checklists'] and text:
                new_item_id = 'i_' + os.urandom(3).hex()
                trip_data['checklists'][cid]['items'].append({"id": new_item_id, "text": text, "done": False})
                save_data(trip_data)
        return redirect(url_for('checklists'))

    lists_html = ""
    for cid, cdata in trip_data.get('checklists', {}).items():
        items_html = "".join([f"<li>{item['text']}</li>" for item in cdata['items']])
        lists_html += f"""
        <div style="background:#111218; padding:15px; margin-bottom:15px; border-radius:8px;">
            <h3>📋 {cdata['title']}</h3>
            <ul>{items_html if items_html else 'אין פריטים עדיין'}</ul>
            <form method="POST" style="display:flex; gap:10px; margin-top:10px;">
                <input type="hidden" name="action" value="add_item">
                <input type="hidden" name="list_id" value="{cid}">
                <input type="text" name="item_text" placeholder="הוסף פריט..." required style="flex-grow:1;">
                <button type="submit">הוסף</button>
            </form>
        </div>
        """

    content = f"""
    <h2>רשימות צ'ק-ליסט</h2>
    <div style="background:#111218; padding:15px; margin-bottom:20px; border-radius:8px;">
        <h3>הוסף רשימה חדשה</h3>
        <form method="POST" style="display:flex; gap:10px;">
            <input type="hidden" name="action" value="add_list">
            <input type="text" name="list_title" placeholder="שם הרשימה..." required style="flex-grow:1;">
            <button type="submit">צור רשימה</button>
        </form>
    </div>
    {lists_html}
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "תכנון טיול ליפן 2026",
        "short_name": "טיול ליפן",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b0c10",
        "theme_color": "#6366f1",
        "icons": [{"src": "https://img.icons8.com/color/512/japan.png", "sizes": "512x512", "type": "image/png"}]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)