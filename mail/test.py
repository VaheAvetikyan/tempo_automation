import imaplib
import email
import os
from datetime import datetime
from email.header import decode_header

start_time = datetime.now()

# account credentials
username = "reconciliation_support@tempo.eu.com"
password = "matevosyan1986"
# number of top emails to fetch
NUMBER_OF_EMAILS = 10

# create an IMAP4 class with SSL
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

# mailbox_list = imap.list()
# print(mailbox_list)

status, messages = imap.select(mailbox='"Online Transactions"')
# total number of emails
messages = int(messages[0])
print("total number of emails ", messages)

folder_name = "tempo_sepa"

for i in range(1, messages):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
                # print("Subject:", subject)

            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)
            # print("From:", From)

            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    if "attachment" in content_disposition and ".xml" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            if not os.path.isdir(folder_name):
                                # make a folder for this email (named after the subject)
                                os.mkdir(folder_name)
                            filepath = os.path.join(folder_name, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))

# close the connection and logout
imap.close()
imap.logout()

end_time = datetime.now()
time_diff = (end_time - start_time)
execution_time = time_diff.total_seconds() * 1000
print("Execution took", execution_time, " ms")


def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)
