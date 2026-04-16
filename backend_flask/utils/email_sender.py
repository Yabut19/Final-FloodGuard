import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_password_email(recipient_email, password, name):
    try:
        sender_email = Config.MAIL_USERNAME
        sender_password = Config.MAIL_PASSWORD
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your FloodGuard LGU Admin Account"
        message["From"] = sender_email
        message["To"] = recipient_email

        # Create the plain-text and HTML version of your message
        text = f"""\
        Hi {name},
        
        An LGU Admin account has been created for you in the FloodGuard system.
        
        Here are your login details:
        Email: {recipient_email}
        Password: {password}
        
        Please log in and change your password immediately.
        """
        
        html = f"""\
        <html>
          <body>
            <h2>Welcome to FloodGuard!</h2>
            <p>Hi {name},</p>
            <p>An LGU Admin account has been created for you.</p>
            <p>Here are your login details:</p>
            <ul>
                <li><strong>Email:</strong> {recipient_email}</li>
                <li><strong>Password:</strong> {password}</li>
            </ul>
            <p>Please log in and change your password immediately.</p>
          </body>
        </html>
        """

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        # Create secure connection with server and send email
        if Config.MAIL_PORT == 465:
            with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                server.login(sender_email, sender_password)
                server.sendmail(
                    sender_email, recipient_email, message.as_string()
                )
        else:
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(
                    sender_email, recipient_email, message.as_string()
                )
        
        print(f"Email sent successfully to {recipient_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
