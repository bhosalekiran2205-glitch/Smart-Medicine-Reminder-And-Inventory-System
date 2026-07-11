# 💊 Smart Medicine Reminder and Inventory System

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)
![AWS](https://img.shields.io/badge/AWS-Cloud-orange?style=for-the-badge&logo=amazonaws)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue?style=for-the-badge&logo=mysql)

</p>


# 📖 Overview

The **Smart Medicine Reminder and Inventory System** is a cloud-based healthcare application developed using **Flask** and **Amazon Web Services (AWS)**.

The system helps users manage medicines efficiently by providing automated reminders, inventory management, expiry tracking, missed-dose monitoring, and email notifications.

The application is deployed on **Amazon EC2**, stores data in **Amazon RDS (MySQL)**, schedules reminder execution using **Amazon EventBridge** and **AWS Lambda**, sends reminder emails through **Amazon SES**, provides a custom domain using **Amazon Route 53**, and monitors the infrastructure using **Amazon CloudWatch

# ✨ Key Features

- 👤 User Registration & Login
- 💊 Medicine Inventory Management
- ⏰ Automated Medicine Reminders
- 📅 Medicine Schedule Management
- ⚠️ Missed Dose Detection
- 📦 Low Stock Monitoring
- 📧 Email Notifications using Amazon SES
- ☁️ Cloud Deployment on AWS
- 📊 CloudWatch Monitoring
- 🌐 Custom Domain with Amazon Route 53

---

# 🏗️ AWS Architecture

The application follows a cloud-based architecture deployed on Amazon Web Services (AWS).

### Architecture Workflow

User  
⬇  
Amazon Route 53 (Custom Domain)  
⬇  
Amazon EC2 (Flask Web Application)  
⬇  
Amazon RDS (MySQL Database)  
⬇  
Amazon EventBridge (Scheduled Trigger - Every 1 Minute)  
⬇  
AWS Lambda (Reminder Processing)  
⬇  
Amazon SES (Email Notifications)

Amazon CloudWatch continuously monitors the application's logs and performance.

> 📌 **Architecture Diagram**

<p align="center">
<img src="docs/architecture.png" width="900">
</p>


---

# ☁️ AWS Services Used

| AWS Service | Purpose |
|-------------|----------|
| Amazon EC2 | Hosts the Flask web application |
| Amazon RDS (MySQL) | Stores users, medicines, reminders, and logs |
| Amazon EventBridge | Triggers reminder execution every minute |
| AWS Lambda | Processes medicine reminders |
| Amazon SES | Sends reminder and missed-dose emails |
| Amazon Route 53 | Provides custom domain routing |
| Amazon CloudWatch | Monitoring, metrics, and logs |

---

# 🛠️ Technology Stack

| Category | Technologies |
|-----------|--------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Database | MySQL (Amazon RDS) |
| Cloud Platform | Amazon Web Services (AWS) |
| Email Service | Amazon SES |
| Scheduling | Amazon EventBridge + AWS Lambda |
| Monitoring | Amazon CloudWatch |
| DNS | Amazon Route 53 |
| Version Control | Git & GitHub |

---

# 📂 Project Structure

```
Smart-Medicine-Reminder-And-Inventory-System
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── add_medicine.html
│   ├── base.html
│   ├── chatbot.html
│   ├── dashboard.html
│   ├── history.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── reports.html
│   └── schedule.html
│
├── database/
├── docs/
├── Lambda/
├── screenshots/
│
├── app.py
├── requirements.txt
├── README.md
└── LICENSE
```
---

# ⚙️ Installation Guide

### Clone the Repository

```bash
git clone https://github.com/bhosalekiran2205-glitch/Smart-Medicine-Reminder-And-Inventory-System.git
```

### Move into the Project Folder

```bash
cd Smart-Medicine-Reminder-And-Inventory-System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Flask Application

```bash
python app.py
---

# ☁️ AWS Deployment

The application is deployed on Amazon Web Services (AWS) using the following architecture:

- Amazon EC2 hosts the Flask application.
- Amazon RDS stores application data.
- Amazon EventBridge triggers AWS Lambda every minute.
- AWS Lambda processes reminder events.
- Amazon SES sends reminder emails.
- Amazon Route 53 provides the custom domain.
- Amazon CloudWatch monitors application health and logs.

---

# 📸 Application Screenshots

| Screen | Description |
|---------|-------------|
| Landing Page | Home page of the application |
| Login Page | User authentication |
| Register Page | New user registration |
| Dashboard | User dashboard with medicine overview |
| Add Medicine | Add new medicines and schedules |
| Schedule | View scheduled medicines |
| History | Medicine history and adherence |
| Reports | Reports and analytics |
| Chatbot | AI-powered medicine assistant |

# 🔮 Future Enhancements

- SMS Notifications
- Mobile Application
- AI-based Medicine Recommendation
- Voice Assistant Integration
- Family Member Dashboard
- Wearable Device Integration
- Medicine Barcode Scanner
- Multi-language Support

---

# 👩‍💻 Author

**Kiran Bhosale**

Bachelor of Computer Applications (BCA)

Cloud & Full Stack Developer

GitHub:
https://github.com/bhosalekiran2205-glitch

---

# 📄 License

This project is licensed under the MIT License.
