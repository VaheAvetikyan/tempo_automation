import email
import os
from datetime import datetime
from email.header import decode_header

from email_service.email import Email


def attachment_parser(mailbox, file_format):
    start_time = datetime.now()
    folder_name = "tempo_sepa"
    mail = Email()
    messages = mail.get_message_list(mailbox)

    for msg in messages:
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)

                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if "attachment" in content_disposition and file_format in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                if not os.path.isdir(folder_name):
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                open(filepath, "wb").write(part.get_payload(decode=True))

    mail.logout()

    end_time = datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print("Execution took", execution_time, " ms")
