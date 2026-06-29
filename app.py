from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import mysql.connector
import uuid
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "medicine_app"
}

EMAIL_CONFIG = {
    "sender": "bhosalekiran2205@gmail.com",       # apna Gmail yahan
    "password": "ndts mjox spes zrba",          # Gmail App Password
    "family_email": "awscourse2205@gmail.com"   # family ka email
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def send_family_alert(patient_name, medicine_name, medicine_time):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⚠️ Medicine Missed - {patient_name}"
        msg["From"] = EMAIL_CONFIG["sender"]
        msg["To"] = EMAIL_CONFIG["family_email"]

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
          <div style="max-width: 500px; margin: auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h2 style="color: #e53e3e;">⚠️ Medicine Not Taken</h2>
            <p style="color: #555;">Hi,</p>
            <p style="color: #555;"><strong>{patient_name}</strong> has not taken their medicine on time.</p>
            <div style="background: #fff5f5; border-left: 4px solid #e53e3e; padding: 12px 16px; border-radius: 6px; margin: 20px 0;">
              <p style="margin: 0; color: #333;"><strong>Medicine:</strong> {medicine_name}</p>
              <p style="margin: 4px 0 0; color: #333;"><strong>Scheduled Time:</strong> {medicine_time}</p>
            </div>
            <p style="color: #555;">Please check on them and remind them to take their medicine.</p>
            <p style="color: #888; font-size: 12px; margin-top: 30px;">— MediCare+ Alert System</p>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
            server.sendmail(EMAIL_CONFIG["sender"], EMAIL_CONFIG["family_email"], msg.as_string())

        print(f"✅ Alert sent for {medicine_name}")
    except Exception as e:
        print(f"❌ Email error: {e}")


def check_missed_doses():
    # Wait 10 seconds after app start (TESTING - 60 wapas kar dena baad mein)
    threading.Event().wait(10)
    while True:
        try:
            db = get_db()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT m.*, u.name as patient_name
                FROM medicines m
                JOIN users u ON m.user_email = u.email
            """)
            medicines = cur.fetchall()
            cur.close()
            db.close()

            today = datetime.now().date()
            now = datetime.now()

            for med in medicines:
                time_str = str(med["time"])
                if isinstance(med["time"], timedelta):
                    total_seconds = int(med["time"].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                else:
                    parts = time_str.split(":")
                    hours = int(parts[0])
                    minutes = int(parts[1])

                scheduled = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                missed_window = scheduled + timedelta(minutes=1)   # 👈 30 ki jagah 1 minute (testing)

                last_taken = med["last_taken"]
                already_taken_today = (last_taken == today)

                if now >= missed_window and not already_taken_today:
                    send_family_alert(
                        patient_name=med["patient_name"],
                        medicine_name=med["name"],
                        medicine_time=f"{hours:02d}:{minutes:02d}"
                    )

        except Exception as e:
            print(f"Checker error: {e}")

        threading.Event().wait(15)   # 👈 1800 ki jagah 15 second (testing)

# Background thread
checker_thread = threading.Thread(target=check_missed_doses, daemon=True)
checker_thread.start()


def get_badges(qty, expiry_date):
    badges = []
    if qty <= 5:
        badges.append("low_stock")
    if (expiry_date - datetime.now().date()) <= timedelta(days=5):
        badges.append("expiring_soon")
    return badges


def get_period(time_str):
    if isinstance(time_str, timedelta):
        total_seconds = int(time_str.total_seconds())
        hour = total_seconds // 3600
    else:
        hour = int(str(time_str).split(":")[0])
    if hour < 12:
        return "Morning"
    elif hour < 17:
        return "Afternoon"
    else:
        return "Night"


def enrich(rows, today):
    enriched = []
    for r in rows:
        expiry = r["expiry_date"]
        days_left = (expiry - today).days
        last_taken = r["last_taken"]

        if isinstance(r["time"], timedelta):
            total_seconds = int(r["time"].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            time_str = f"{hours:02d}:{minutes:02d}:00"
        else:
            time_str = str(r["time"])

        enriched.append({
            "id": r["id"],
            "name": r["name"],
            "dosage": r["dosage"],
            "time": time_str,
            "qty": r["quantity"],
            "expiry": expiry.strftime("%Y-%m-%d"),
            "days_left": days_left,
            "taken_today": (last_taken == today),
            "badges": get_badges(r["quantity"], expiry),
            "period": get_period(r["time"]),
        })
    return enriched


def get_weekly_adherence(user_email, total_meds):
    db = get_db()
    cur = db.cursor(dictionary=True)
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    heatmap = []
    for d in days:
        cur.execute(
            "SELECT COUNT(DISTINCT medicine_id) as cnt FROM dose_logs WHERE user_email=%s AND date_taken=%s",
            (user_email, d)
        )
        row = cur.fetchone()
        taken = row["cnt"] if row else 0
        pct = round((taken / total_meds) * 100) if total_meds > 0 else 0
        heatmap.append({"label": d.strftime("%a")[0], "date": d.strftime("%d %b"), "pct": pct})
    cur.close()
    db.close()
    avg = round(sum(h["pct"] for h in heatmap) / len(heatmap)) if heatmap else 0
    return heatmap, avg


def get_streak(user_email, total_meds):
    if total_meds == 0:
        return 0
    db = get_db()
    cur = db.cursor(dictionary=True)
    streak = 0
    day = datetime.now().date()
    while streak < 60:
        cur.execute(
            "SELECT COUNT(DISTINCT medicine_id) as cnt FROM dose_logs WHERE user_email=%s AND date_taken=%s",
            (user_email, day)
        )
        row = cur.fetchone()
        taken = row["cnt"] if row else 0
        if taken >= total_meds:
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    cur.close()
    db.close()
    return streak


def get_monthly_trend(user_email, total_meds):
    db = get_db()
    cur = db.cursor(dictionary=True)
    today = datetime.now().date()
    days = [today - timedelta(days=i) for i in range(29, -1, -1)]
    trend = []
    for d in days:
        cur.execute(
            "SELECT COUNT(DISTINCT medicine_id) as cnt FROM dose_logs WHERE user_email=%s AND date_taken=%s",
            (user_email, d)
        )
        row = cur.fetchone()
        taken = row["cnt"] if row else 0
        pct = round((taken / total_meds) * 100) if total_meds > 0 else 0
        trend.append({"date": d.strftime("%d %b"), "pct": pct})
    cur.close()
    db.close()
    return trend


def get_medicine_usage(user_email):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT m.name, COUNT(*) as taken_count
        FROM dose_logs dl
        JOIN medicines m ON dl.medicine_id = m.id
        WHERE dl.user_email=%s
        GROUP BY m.name
        ORDER BY taken_count DESC
    """, (user_email,))
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows


@app.route("/")
def landing():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT email FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            flash("Email already registered, please login.", "error")
            cur.close(); db.close()
            return redirect(url_for("register"))

        cur.execute("INSERT INTO users (email, name, password) VALUES (%s, %s, %s)",
                     (email, name, password))
        db.commit()
        cur.close(); db.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close(); db.close()

        if user:
            session["user"] = email
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    today = datetime.now().date()
    query = request.args.get("q", "").strip().lower()

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE user_email=%s", (session["user"],))
    rows = cur.fetchall()
    cur.close(); db.close()

    all_enriched = enrich(rows, today)
    total = len(all_enriched)
    low_stock_count = sum(1 for m in all_enriched if "low_stock" in m["badges"])
    expiring_count = sum(1 for m in all_enriched if "expiring_soon" in m["badges"])

    heatmap, weekly_avg = get_weekly_adherence(session["user"], total)
    streak = get_streak(session["user"], total)

    notifications = []
    for m in all_enriched:
        if "low_stock" in m["badges"]:
            notifications.append({"type": "low_stock", "title": f"{m['name']} is running low",
                                   "detail": f"Only {m['qty']} left — restock soon"})
        if "expiring_soon" in m["badges"]:
            label = "Expires today" if m["days_left"] == 0 else f"Expires in {m['days_left']} day(s)"
            notifications.append({"type": "expiring", "title": f"{m['name']} expiring soon", "detail": label})
    notifications.sort(key=lambda n: 0 if n["type"] == "low_stock" else 1)

    schedule_today = sorted(all_enriched, key=lambda m: m["time"])

    filtered = all_enriched
    if query:
        filtered = [m for m in filtered if query in m["name"].lower()]

    grouped = {"Morning": [], "Afternoon": [], "Night": []}
    for m in filtered:
        grouped[m["period"]].append(m)

    return render_template(
        "dashboard.html", grouped=grouped, name=session.get("name"), email=session.get("user"),
        total=total, low_stock_count=low_stock_count, expiring_count=expiring_count,
        query=query, notifications=notifications, schedule_today=schedule_today,
        heatmap=heatmap, weekly_avg=weekly_avg, streak=streak,
    )


@app.route("/add-medicine", methods=["GET", "POST"])
def add_medicine():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        med_id = str(uuid.uuid4())[:8]
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO medicines (id, user_email, name, dosage, time, quantity, expiry_date) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (med_id, session["user"], request.form["name"], request.form["dosage"],
             request.form["time"], int(request.form["qty"]), request.form["expiry"])
        )
        db.commit()
        cur.close(); db.close()
        flash("Medicine added successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_medicine.html", med=None)


@app.route("/edit-medicine/<med_id>", methods=["GET", "POST"])
def edit_medicine(med_id):
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE id=%s AND user_email=%s", (med_id, session["user"]))
    item = cur.fetchone()

    if not item:
        cur.close(); db.close()
        flash("Medicine not found.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        cur.execute(
            "UPDATE medicines SET name=%s, dosage=%s, time=%s, quantity=%s, expiry_date=%s WHERE id=%s",
            (request.form["name"], request.form["dosage"], request.form["time"],
             int(request.form["qty"]), request.form["expiry"], med_id)
        )
        db.commit()
        cur.close(); db.close()
        flash("Medicine updated successfully!", "success")
        return redirect(url_for("dashboard"))

    cur.close(); db.close()
    med = {"id": item["id"], "name": item["name"], "dosage": item["dosage"],
           "time": item["time"], "qty": item["quantity"], "expiry": item["expiry_date"].strftime("%Y-%m-%d")}
    return render_template("add_medicine.html", med=med)


@app.route("/take-medicine/<med_id>")
def take_medicine(med_id):
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE id=%s AND user_email=%s", (med_id, session["user"]))
    item = cur.fetchone()

    if item and item["quantity"] > 0:
        new_qty = item["quantity"] - 1
        today = datetime.now().date()
        cur.execute("UPDATE medicines SET quantity=%s, last_taken=%s WHERE id=%s", (new_qty, today, med_id))
        cur.execute(
            "INSERT INTO dose_logs (user_email, medicine_id, date_taken) VALUES (%s,%s,%s)",
            (session["user"], med_id, today)
        )
        db.commit()
        flash(f"Marked {item['name']} as taken. {new_qty} left.", "success")

    cur.close(); db.close()
    return redirect(url_for("dashboard"))


@app.route("/delete-medicine/<med_id>")
def delete_medicine(med_id):
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM medicines WHERE id=%s AND user_email=%s", (med_id, session["user"]))
    db.commit()
    cur.close(); db.close()
    flash("Medicine removed.", "success")
    return redirect(url_for("dashboard"))


@app.route("/history")
def history():
    if "user" not in session:
        return redirect(url_for("login"))

    query = request.args.get("q", "").strip().lower()

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT dl.date_taken, m.name, m.dosage, m.time
        FROM dose_logs dl
        JOIN medicines m ON dl.medicine_id = m.id
        WHERE dl.user_email=%s
        ORDER BY dl.date_taken DESC
    """, (session["user"],))
    logs = cur.fetchall()
    cur.close(); db.close()

    if query:
        logs = [l for l in logs if query in l["name"].lower()]

    grouped_logs = {}
    for l in logs:
        d = l["date_taken"].strftime("%Y-%m-%d")
        grouped_logs.setdefault(d, []).append(l)

    return render_template("history.html", grouped_logs=grouped_logs, query=query, total_logs=len(logs))


@app.route("/reports")
def reports():
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE user_email=%s", (session["user"],))
    meds = cur.fetchall()
    cur.close(); db.close()

    total = len(meds)
    trend = get_monthly_trend(session["user"], total)
    usage = get_medicine_usage(session["user"])
    avg_adherence = round(sum(t["pct"] for t in trend) / len(trend)) if trend else 0

    return render_template("reports.html", trend=trend, usage=usage, avg_adherence=avg_adherence, total=total)


@app.route("/schedule")
def schedule():
    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM medicines WHERE user_email=%s", (session["user"],))
    rows = cur.fetchall()
    cur.close(); db.close()

    today = datetime.now().date()
    meds = enrich(rows, today)
    schedule_list = sorted(meds, key=lambda m: m["time"])

    return render_template("schedule.html", schedule=schedule_list)


if __name__ == "__main__":
    app.run(debug=True)
