import os
import boto3
import pymysql

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# ==========================
# Environment Variables
# ==========================

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

SES_SENDER = os.environ["SES_SENDER"]

ses = boto3.client(
    "ses",
    region_name="ap-south-1"
)


# ==========================
# Database Connection
# ==========================

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=10
    )


# ==========================
# Send Email
# ==========================

def send_email(receivers, subject, body):
    try:
        response = ses.send_email(
            Source=SES_SENDER,
            Destination={
                "ToAddresses": receivers
            },
            Message={
                "Subject": {
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Data": body
                    }
                }
            }
        )

        print("Email Sent:", response)

    except Exception as e:
        print("SES ERROR:", str(e))


# ==========================
# Current IST Time
# ==========================

def get_current_time():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now


# ==========================
# Medicine Reminder
# ==========================

def send_medicine_reminders(cursor, now):
    current_time = (now - timedelta(minutes=1)).strftime("%H:%M")
    print("Checking Reminder:", current_time)

    cursor.execute("""
        SELECT
            m.id,
            m.user_email,
            u.family_email,
            m.name,
            m.dosage,
            m.time
        FROM medicines m
        JOIN users u
            ON m.user_email = u.email
        WHERE
            DATE_FORMAT(m.time,'%%H:%%i') = %s
            AND m.status = 'Pending'
            AND m.reminder_sent = 0
    """, (current_time,))

    medicines = cursor.fetchall()

    print("Reminder Medicines:", medicines)

    for medicine in medicines:
        receivers = [medicine["user_email"]]

        if medicine["family_email"]:
            if medicine["family_email"] not in receivers:
                receivers.append(medicine["family_email"])

        subject = "💊 Medicine Reminder"

        body = f"""
Hello,

This is your medicine reminder.

Medicine : {medicine['name']}
Dosage : {medicine['dosage']}
Time : {medicine['time']}

Please take your medicine on time.

Thank you.

Smart Medicine Reminder
"""

        send_email(receivers, subject, body)

        cursor.execute("""
            UPDATE medicines
            SET reminder_sent = 1
            WHERE id = %s
        """, (medicine["id"],))


# ==========================
# Low Stock Alert
# ==========================

def send_low_stock_alert(cursor):
    cursor.execute("""
        SELECT
            m.id,
            m.user_email,
            u.family_email,
            m.name,
            m.quantity
        FROM medicines m
        JOIN users u
            ON m.user_email = u.email
        WHERE
            m.quantity <= 5
            AND m.low_stock_sent = 0
    """)

    medicines = cursor.fetchall()

    print("Low Stock:", medicines)

    for medicine in medicines:
        receivers = [medicine["user_email"]]

        if medicine["family_email"]:
            if medicine["family_email"] not in receivers:
                receivers.append(medicine["family_email"])

        subject = "⚠ Low Medicine Stock"

        body = f"""
Hello,

Your medicine stock is running low.

Medicine : {medicine['name']}
Remaining Quantity : {medicine['quantity']}

Please refill your medicine.

Smart Medicine Reminder
"""

        send_email(receivers, subject, body)

        cursor.execute("""
            UPDATE medicines
            SET low_stock_sent = 1
            WHERE id = %s
        """, (medicine["id"],))


# ==========================
# Expiry Reminder
# ==========================

def send_expiry_alert(cursor, now):
    expiry_limit = (now + timedelta(days=5)).date()

    cursor.execute("""
        SELECT
            m.id,
            m.user_email,
            u.family_email,
            m.name,
            m.expiry_date
        FROM medicines m
        JOIN users u
            ON m.user_email = u.email
        WHERE
            m.expiry_date <= %s
            AND m.expiry_sent = 0
    """, (expiry_limit,))

    medicines = cursor.fetchall()

    print("Expiry Medicines:", medicines)

    for medicine in medicines:

        receivers = [medicine["user_email"]]

        if medicine["family_email"] and medicine["family_email"] not in receivers:
            receivers.append(medicine["family_email"])

        subject = "⚠ Medicine Expiry Alert"

        body = f"""
Hello,

Your medicine will expire soon.

Medicine : {medicine['name']}
Expiry Date : {medicine['expiry_date']}

Please replace this medicine before expiry.

Smart Medicine Reminder
"""

        send_email(receivers, subject, body)

        cursor.execute("""
            UPDATE medicines
            SET expiry_sent = 1
            WHERE id = %s
        """, (medicine["id"],))


# ==========================
# Missed Dose Alert
# ==========================

def send_missed_dose_alert(cursor, now):
    today = now.date()
    current_time = (now - timedelta(minutes=1)).strftime("%H:%M")

    cursor.execute("""
        SELECT
            m.id,
            m.user_email,
            u.family_email,
            m.name,
            m.dosage,
            m.time,
            m.last_taken,
            m.status
        FROM medicines m
        JOIN users u
            ON m.user_email = u.email
        WHERE
           DATE_FORMAT(m.time,'%%H:%%i') < %s
            AND m.status = 'Pending'
            AND m.missed_sent = 0
            AND (
                m.last_taken IS NULL
                OR m.last_taken < %s
            )
    """, (current_time, today))

    medicines = cursor.fetchall()

    print("Missed Medicines:", medicines)

    for medicine in medicines:
        receivers = []

        if medicine["family_email"]:
            receivers.append(medicine["family_email"])

        receivers.append(medicine["user_email"])

        subject = "🚨 Missed Medicine Alert"

        body = f"""
Hello,

Medicine was not taken.

Medicine : {medicine['name']}
Dosage : {medicine['dosage']}
Scheduled Time : {medicine['time']}

Please take medicine immediately if appropriate.

Smart Medicine Reminder
"""

        send_email(receivers, subject, body)

        cursor.execute("""
            UPDATE medicines
            SET
                status = 'Missed',
                missed_sent = 1
            WHERE id = %s
        """, (medicine["id"],))

        print("Marked Missed:", medicine["id"])


# ==========================
# Main Lambda
# ==========================

def lambda_handler(event, context):
    connection = None
    cursor = None

    try:
        now = get_current_time()
        print("Current IST:", now)

        connection = get_connection()
        cursor = connection.cursor()

        # Medicine Reminder
        send_medicine_reminders(cursor, now)

        # Low Stock
        send_low_stock_alert(cursor)

        # Expiry
        send_expiry_alert(cursor, now)

        # Missed Dose
        send_missed_dose_alert(cursor, now)

        return {
            "statusCode": 200,
            "body": "Reminder service executed successfully."
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": str(e)
        }

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
            print("Database Closed")
