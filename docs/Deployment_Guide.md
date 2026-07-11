# 🚀 Deployment Guide

## Smart Medicine Reminder and Inventory System

This guide explains how to deploy the project on Amazon Web Services (AWS).

---

## Prerequisites

- AWS Account
- Ubuntu EC2 Instance
- Amazon RDS (MySQL)
- Amazon SES (Verified Email)
- Amazon Route 53 Hosted Zone
- AWS Lambda Function
- Amazon EventBridge Rule
- Python 3.x
- Git

---

## Step 1: Launch EC2 Instance

- Launch an Ubuntu EC2 instance.
- Allow HTTP (80), HTTPS (443), and SSH (22) in the Security Group.
- Connect to the instance using SSH.

---

## Step 2: Install Dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx -y
```

---

## Step 3: Clone Repository

```bash
git clone https://github.com/bhosalekiran2205-glitch/Smart-Medicine-Reminder-And-Inventory-System.git
cd Smart-Medicine-Reminder-And-Inventory-System
```

---

## Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Step 5: Install Python Packages

```bash
pip install -r requirements.txt
```

---

## Step 6: Configure Amazon RDS

- Create a MySQL database in Amazon RDS.
- Update the database credentials in `app.py`.

---

## Step 7: Configure Amazon SES

- Verify sender email.
- Update the sender email configuration.

---

## Step 8: Configure Lambda & EventBridge

- Create an AWS Lambda function.
- Create an EventBridge rule to trigger the Lambda function every minute.

---

## Step 9: Configure Route 53

- Create a Hosted Zone.
- Point the domain to the EC2 instance using an A Record.

---

## Step 10: Run the Application

```bash
python app.py
```

Or using Gunicorn:

```bash
gunicorn app:app
```

---

## AWS Services Used

- Amazon EC2
- Amazon RDS
- AWS Lambda
- Amazon EventBridge
- Amazon SES
- Amazon Route 53
- Amazon CloudWatch

---

## Deployment Completed

The Smart Medicine Reminder and Inventory System is now deployed on AWS and accessible through the configured domain.
