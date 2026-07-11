# AWS Lambda

This folder contains the AWS Lambda function used in the **Smart Medicine Reminder and Inventory System**.

## Purpose

The Lambda function automates medicine-related notifications by interacting with the Amazon RDS database and Amazon SES.

### Features

- 💊 Sends medicine reminders
- ⚠️ Sends low stock alerts
- 📅 Sends medicine expiry alerts
- 🚨 Detects missed doses
- 📧 Sends email notifications using Amazon SES

## Trigger

The Lambda function is triggered automatically by **Amazon EventBridge** every minute.

## Environment Variables

- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `SES_SENDER`

## Dependencies

- boto3
- pymysql

## AWS Services Used

- AWS Lambda
- Amazon EventBridge
- Amazon RDS
- Amazon SES
- Amazon CloudWatch
