import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
PORT = int(os.getenv('MAIL_PORT', 587))
USERNAME = os.getenv('MAIL_USERNAME')
PASSWORD = os.getenv('MAIL_PASSWORD')
# Strip any spaces from the password (common in Google App Passwords)
if PASSWORD:
    PASSWORD = PASSWORD.replace(' ', '')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_credentials_email(to_email, full_name, password):
    """
    Sends an email to the user with their login credentials.
    """
    if not USERNAME or not PASSWORD:
        logging.error("Email credentials not configured.")
        return False, "Email server not configured"

    try:
        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = to_email
        msg['Subject'] = "Your FloodGuard Account Credentials"

        body = f"""
        <html>
          <body>
            <h2>Welcome to FloodGuard, {full_name}!</h2>
            <p>Your account has been successfully created.</p>
            <p><strong>Username/Email:</strong> {to_email}</p>
            <p><strong>Temporary Password:</strong> {password}</p>
            <p>Please log in and change your password immediately.</p>
            <br>
            <p>Stay safe,</p>
            <p>The FloodGuard Team</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        logger.info(f"Attempting to connect to SMTP server: {SERVER}:{PORT}")
        logger.info(f"Using username: {USERNAME}")
        
        try:
            server = smtplib.SMTP(SERVER, PORT)
            server.set_debuglevel(1) # Enable SMTP debug output
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
            logger.info(f"Credentials sent to {to_email}")
        finally:
            try:
                server.quit()
            except Exception:
                pass # Ignore errors during quit
        
        logger.info(f"Credentials sent to {to_email}")
        return True, "Email sent successfully"
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending to {to_email}: {e}", exc_info=True)
        return False, f"SMTP Error: {str(e)}"
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}", exc_info=True)
        return False, f"Error: {str(e)}"


def send_dismissal_notification(reporter_email, reporter_name, report_type, location, rejection_reason):
    """
    Sends an email to the reporter when their report is dismissed.
    """
    if not USERNAME or not PASSWORD:
        logging.error("Email credentials not configured.")
        return False, "Email server not configured"

    try:
        msg = MIMEMultipart()
        msg['From'] = USERNAME
        msg['To'] = reporter_email
        msg['Subject'] = "Update on Your FloodGuard Report"

        body = f"""
        <html>
          <body>
            <h2>Hello {reporter_name},</h2>
            <p>We have reviewed your report and wanted to provide an update.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Report Details:</h3>
                <p><strong>Type:</strong> {report_type}</p>
                <p><strong>Location:</strong> {location}</p>
            </div>
            
            <p><strong>Status:</strong> <span style="color: #dc3545;">Report Dismissed</span></p>
            <p><strong>Reason:</strong> {rejection_reason}</p>
            
            <p>After careful review by our LGU officials, this report has been determined to not require immediate action at this time. This could be due to various factors such as the report being a duplicate, false alarm, or the situation has already been addressed.</p>
            
            <p>If you believe this assessment is incorrect or if the situation has changed, please feel free to submit a new report with updated information.</p>
            
            <br>
            <p>Thank you for helping keep our community safe,</p>
            <p>The FloodGuard Team</p>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        logger.info(f"Sending dismissal notification to {reporter_email}")
        
        try:
            server = smtplib.SMTP(SERVER, PORT)
            server.set_debuglevel(1)
            server.starttls()
            server.login(USERNAME, PASSWORD)
            server.send_message(msg)
            logger.info(f"Dismissal notification sent to {reporter_email}")
        finally:
            try:
                server.quit()
            except Exception:
                pass
        
        return True, "Dismissal notification sent successfully"
    
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending dismissal notification to {reporter_email}: {e}", exc_info=True)
        return False, f"SMTP Error: {str(e)}"
    except Exception as e:
        logger.error(f"Failed to send dismissal notification to {reporter_email}: {e}", exc_info=True)
        return False, f"Error: {str(e)}"
