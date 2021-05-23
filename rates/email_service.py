import imaplib
import email
import os
from email.header import decode_header

# account credentials
username = os.environ.get('EMAIL')
password = os.environ.get('EMAIL_PASS')
NUMBER_OF_MESSAGES = 5


def get_text_from_email(target_mailbox, target_subject):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)

    status, messages = imap.select(mailbox=target_mailbox)
    messages = int(messages[0])

    message_list = get_messages(imap, messages)
    for msg in message_list:
        if isinstance(msg[0], tuple):
            msg = email.message_from_bytes(msg[0][1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)
                print("Subject:", subject)

            if target_subject in subject:
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            return body
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        return body
    imap.close()
    imap.logout()


def get_messages(imap, messages):
    message_list = []
    for i in range(messages, messages - NUMBER_OF_MESSAGES, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")
        message_list.append(msg)

    return message_list
