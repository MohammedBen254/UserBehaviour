import os
from flask import Flask, request, jsonify, render_template
import json
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
DB_FILE = "test.db"
# ...existing code...

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.executescript('''
        DROP TABLE IF EXISTS "User";
        DROP TABLE IF EXISTS "Session";
        DROP TABLE IF EXISTS EventType;
        DROP TABLE IF EXISTS Event;
        DROP TABLE IF EXISTS PageView;
        DROP TABLE IF EXISTS Click;
        DROP TABLE IF EXISTS UserNeed;
    ''')

    c.executescript("""
        CREATE TABLE "User" (
            user_id VARCHAR(100) PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE "Session" (
            session_id VARCHAR(100) PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            start_time TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES "User"(user_id) ON DELETE CASCADE
        );

        CREATE TABLE EventType (
            event_type_id VARCHAR(20) PRIMARY KEY
        );

        CREATE TABLE Event (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(100) NOT NULL,
            event_type_id VARCHAR(20) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            FOREIGN KEY (session_id) REFERENCES "Session"(session_id) ON DELETE CASCADE,
            FOREIGN KEY (event_type_id) REFERENCES EventType(event_type_id)
        );

        CREATE TABLE PageView (
            event_id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            referrer TEXT,
            viewport_width INTEGER,
            viewport_height INTEGER,
            FOREIGN KEY (event_id) REFERENCES Event(event_id) ON DELETE CASCADE
        );

        CREATE TABLE Click (
            event_id INTEGER PRIMARY KEY,
            tag VARCHAR(50),
            element_id VARCHAR(100),
            class_list TEXT,
            text TEXT,
            href TEXT,
            x INTEGER,
            y INTEGER,
            scroll_position INTEGER,
            time_on_page REAL,
            FOREIGN KEY (event_id) REFERENCES Event(event_id) ON DELETE CASCADE
        );

        CREATE TABLE UserNeed (
            event_id INTEGER PRIMARY KEY,
            message TEXT,
            FOREIGN KEY (event_id) REFERENCES Event(event_id) ON DELETE CASCADE
        );

        INSERT INTO EventType (event_type_id) VALUES ('page_view'), ('click'), ('user_need');
    """)

    conn.commit()
    conn.close()

# ...existing code...

@app.route("/track", methods=["POST"])
def track_event():
    if request.is_json:
        body = request.get_json()
    else:
        try:
            body = json.loads(request.data.decode("utf-8"))
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

    user_id = body.get("user_id")
    session_id = body.get("session_id")
    events = body.get("events", [])

    if not user_id or not session_id or not events:
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO \"User\" (user_id, created_at) VALUES (?, ?)",
              (user_id, datetime.utcnow().isoformat()))

    c.execute("""
        INSERT OR IGNORE INTO "Session" (session_id, user_id, start_time)
        VALUES (?, ?, ?)
    """, (session_id, user_id, datetime.utcnow().isoformat()))

    for event in events:
        event_type = event.get("type")
        timestamp = event.get("timestamp") or datetime.utcnow().isoformat()
        data = event.get("data", {})

        c.execute("""
            INSERT INTO Event (session_id, event_type_id, timestamp)
            VALUES (?, ?, ?)
        """, (session_id, event_type, timestamp))
        event_id = c.lastrowid

        if event_type == "page_view":
            url = data.get("url")
            title = data.get("title")
            referrer = data.get("referrer")
            width = data.get("viewport", {}).get("width")
            height = data.get("viewport", {}).get("height")

            c.execute("""
                INSERT INTO PageView (event_id, url, title, referrer, viewport_width, viewport_height)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_id, url, title, referrer, width, height))

        elif event_type == "click":
            tag = data.get("tag")
            element_id = data.get("id")
            class_list = ",".join(data.get("class", []))
            text = data.get("text")
            href = data.get("href")
            x = data.get("position", {}).get("x")
            y = data.get("position", {}).get("y")
            scroll_position = data.get("scroll_position")
            time_on_page = data.get("time_on_page")

            c.execute("""
                INSERT INTO Click (event_id, tag, element_id, class_list, text, href, x, y, scroll_position, time_on_page)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (event_id, tag, element_id, class_list, text, href, x, y, scroll_position, time_on_page))

        elif event_type == "user_need":
            message = data.get("message")
            c.execute("""
                INSERT INTO UserNeed (event_id, message)
                VALUES (?, ?)
            """, (event_id, message))

    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200

@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Total events
    c.execute("SELECT COUNT(*) FROM Event")
    total_events = c.fetchone()[0]

    # Unique users
    c.execute("SELECT COUNT(DISTINCT user_id) FROM Session")
    unique_users = c.fetchone()[0]

    # Event types
    c.execute("SELECT event_type_id, COUNT(*) FROM Event GROUP BY event_type_id")
    event_types = dict(c.fetchall())

    # Events by day
    c.execute("SELECT DATE(timestamp), COUNT(*) FROM Event GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC")
    events_by_day = c.fetchall()

    # All events for display (ID, user_id, event_type, data, timestamp)
    c.execute("""
        SELECT 
            e.event_id, 
            s.user_id, 
            e.event_type_id, 
            COALESCE(pv.url, cl.text, '') AS data, 
            e.timestamp
        FROM Event e
        LEFT JOIN Session s ON e.session_id = s.session_id
        LEFT JOIN PageView pv ON e.event_id = pv.event_id
        LEFT JOIN Click cl ON e.event_id = cl.event_id
        ORDER BY e.timestamp DESC
    """)
    events = c.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        total_events=total_events,
        unique_users=unique_users,
        event_types=event_types,
        events_by_day=events_by_day,
        events=events
    )

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
