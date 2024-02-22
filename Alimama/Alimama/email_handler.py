import imaplib
import email
from email.header import decode_header
import settings

# Connect to the server
mail = imaplib.IMAP4_SSL(settings.EMAIL_INCOME, settings.EMAIL_INCOME_PORT)

# Login to our account
mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

# Select the mailbox you want to check (INBOX, for example)
mail.select("inbox")

# Search for specific mails by status
status, messages = mail.search(None, 'ALL')

# Convert the result list to a list of email IDs
messages = messages[0].split(b' ')

for mail_id in messages:
    # Fetch each email's MIME data
    status, data = mail.fetch(mail_id, '(RFC822)')

    # Raw email text including headers and alternate payloads
    raw_email = data[0][1]

    # Parse the raw email using email
    email_message = email.message_from_bytes(raw_email)

    # Decode email subject
    subject = decode_header(email_message["subject"])[0][0]
    if isinstance(subject, bytes):
        # If it's a bytes type, decode to str
        subject = subject.decode()

    print("Subject:", subject)
    # You can process the email here (e.g., saving it to your Django model)

# Close the mailbox
mail.close()

# Logout from the server
mail.logout()
