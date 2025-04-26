import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage
import time
from datetime import datetime

# Email configuration
from_email_addr = "1790169810@qq.com"
from_email_pass = "iynzmpvquwmdjgja"
to_email_addr = "1807652312@qq.com"

# GPIO Setup
channel = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

# Global variables to track moisture status
last_status = None
email_count = 0
max_emails_per_day = 4
email_interval = 6 * 60 * 60  # 6 hours in seconds

def send_email(needs_water):
    global email_count
    
    # Check daily email limit
    if email_count >= max_emails_per_day:
        return
    
    try:
        # Create email message
        msg = EmailMessage()
        
        # Set email content based on status
        if needs_water:
            body = f"Alert! Your plant needs watering!\nDetection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subject = "Plant Needs Watering!"
        else:
            body = f"Your plant has sufficient moisture.\nDetection time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subject = "Plant Moisture Status Normal"
        
        msg.set_content(body)
        msg['From'] = from_email_addr
        msg['To'] = to_email_addr
        msg['Subject'] = subject

        # Connect to SMTP server and send email
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(from_email_addr, from_email_pass)
            server.send_message(msg)
        
        print(f"Email sent: {subject}")
        email_count += 1
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def check_moisture():
    global last_status
    
    current_status = GPIO.input(channel)
    
    # Only send email when status changes
    if current_status != last_status:
        if current_status:
            print("Moisture level sufficient")
            send_email(needs_water=False)
        else:
            print("Low moisture detected!")
            send_email(needs_water=True)
        
        last_status = current_status

def main():
    print("Plant Moisture Monitoring System initialized...")
    print(f"Configured for maximum {max_emails_per_day} notifications per day")
    
    try:
        while True:
            check_moisture()
            
            # Reset email count every 6 hours
            time.sleep(email_interval)
            email_count = 0
            
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()