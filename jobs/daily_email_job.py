from src.email_service import EmailService

service = EmailService()

count = service.send_daily_reminders()

print(
    f"Sent {count}"
)
