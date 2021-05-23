import email
from email.header import decode_header

from email_service.email import Email


def get_text_from_email(target_mailbox, target_subject):
    mail = Email()
    message_list = mail.get_message_list(target_mailbox)
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
    mail.logout()
