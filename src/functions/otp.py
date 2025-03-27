import smtplib
from email.mime.text import MIMEText


SENDER_EMAIL = "yadnyeshvinchurkar.abt@gmail.com"  #  Gmail
SENDER_PASSWORD = "dlcy zbit zwjv lfmy"  # Generate App Password from Google


async def send_email(to_email, otp,purpose):

    subject = f"Your OTP for {purpose}"
    body = f"Your OTP for {purpose} is: {otp}\n\nThis OTP is valid for 10 minutes."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)  # Login
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())  # Send email
        server.quit()
        return(" Otp has been sent to your Email !!!")
    except Exception as e:
        return(f"Failed to send email: {e}")

