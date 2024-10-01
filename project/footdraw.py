import os
import smtplib
import random

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
   
def recover_email(user, password):

    # Example usage with a custom sender name
    sender_name = "FootDraw"
    sender_email = os.environ["FOOTDRAW_EMAIL"]
    recipient_email = user.email
    subject = "FootDraw Login"
    text_content = "User: " + str(user.id) + "\n" + "Password: " + str(password)

    return send_email(
        sender_name=sender_name,
        sender_email=sender_email,
        recipient=recipient_email,
        subject=subject,
        text_content=text_content,
        smtp_server=os.environ["SMTP_SERVER"],
        smtp_port=os.environ["SMTP_PORT"],
    )
    
def send_email(
    sender_name,
    sender_email,
    recipient,
    subject,
    text_content,
    html_content=None,
    smtp_server="localhost",
    smtp_port=25,
):
    message = create_message(
        sender_name, sender_email, recipient, subject, text_content, html_content
    )

    try:
        # Connect to the SMTP server (modify server/port as needed)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # Start TLS encryption if required by Postfix configuration
            if server.has_extn("STARTTLS"):
                server.starttls()

            # Authenticate if required (check Postfix configuration)
            if server.has_extn("AUTH"):
                # Replace with your credentials
                server.login("your_username", "your_password")

            server.sendmail(sender_email, recipient, message.as_string())

            return True
    except:
        return False


def create_message(
    sender_name, sender_email, recipient, subject, text_content, html_content=None
):
    message = MIMEMultipart("alternative")
    message["From"] = (
        sender_name + " <" + sender_email + ">"
    )  # Set sender name and email
    message["To"] = recipient
    message["Subject"] = subject

    # Add plain text part
    part1 = MIMEText(text_content, "plain")
    message.attach(part1)

    # Add HTML part (optional)
    if html_content:
        part2 = MIMEText(html_content, "html")
        message.attach(part2)

    return message

def get_distinct_numbers_random(start, end):
    """Generates a list of distinct numbers between start and end in random order.

    Args:
        start: The starting number.
        end: The ending number.

    Returns:
        A list of distinct numbers in random order.
    """

    num_set = set(range(start, end + 1))
    random_numbers = random.sample(num_set, len(num_set))
    return random_numbers















