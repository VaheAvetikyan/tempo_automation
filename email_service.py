import email
import imaplib
import os
from email.header import decode_header


class Email:
    _instance = None
    # account credentials
    _username = os.environ.get('EMAIL')
    _password = os.environ.get('EMAIL_PASS')
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.login()
        return cls._instance

    def login(self):
        self.imap.login(self._username, self._password)

    def logout(self):
        self.imap.close()
        self.imap.logout()

    def folders_bytes(self):
        lst = self.imap.list()
        if lst[0] == 'OK':
            lst = lst[1]
        return lst

    def get_msg_list(self, target_mailbox, quantity):
        msg_list = []
        messages = self._get_messages(target_mailbox)
        for i in range(messages, messages - quantity, -1):
            res, msg = self.imap.fetch(str(i), "(RFC822)")
            if isinstance(msg[0], tuple):
                msg_list.append(msg)
        return msg_list

    def _get_messages(self, target_mailbox):
        status, messages = self.imap.select(mailbox=target_mailbox)
        messages = int(messages[0])
        return messages


class Message:
    msg = None
    frm = None
    subject = None
    body = None
    content_type = None
    content_disposition = None
    attachment_name = None
    attachment = None

    def __init__(self, msg):
        self._decode_message(msg)
        self._decode_subject()
        self._decode_from()
        self._parse_message_details()

    def _decode_message(self, msg):
        self.msg = email.message_from_bytes(msg[0][1])

    def _decode_subject(self):
        self.subject, encoding = decode_header(self.msg["Subject"])[0]
        if isinstance(self.subject, bytes):
            self.subject = self.subject.decode(encoding)

    def _decode_from(self):
        self.frm, encoding = decode_header(self.msg.get("From"))[0]
        if isinstance(self.frm, bytes):
            self.frm = self.frm.decode(encoding)

    def _parse_message_details(self):
        if self.msg.is_multipart():
            self._parse_multipart_message()
        else:
            self._pars_single_message()

    def _parse_multipart_message(self):
        for part in self.msg.walk():
            self.content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in self.content_disposition:
                self.attachment_name = part.get_filename()
                self.attachment = part.get_payload(decode=True)
            if part.get_content_type() == "text/plain":
                self.content_type = part.get_content_type()
                try:
                    self.body = part.get_payload(decode=True).decode()
                except:
                    pass
                break

    def _pars_single_message(self):
        self.content_type = self.msg.get_content_type()
        self.body = self.msg.get_payload(decode=True).decode()


def attachment_parser(mailbox, file_format, in_one_file, quantity):
    messages = mailbox_messages(mailbox, quantity)
    if in_one_file:
        filenames = write_to_one_file(messages, file_format)
    else:
        filenames = write_to_multiple_files(messages, file_format)
    return filenames


def write_to_one_file(messages, file_format):
    folder_name = "tempo"
    filename = "output." + file_format
    filepath = make_filepath(folder_name, filename)
    filenames = [filepath]
    for msg in messages:
        message = Message(msg)
        if message.msg.is_multipart() and file_format in message.content_disposition:
            if message.attachment:
                open(filepath, "ab").write(message.attachment)
    return filenames


def write_to_multiple_files(messages, file_format):
    folder_name = "tempo"
    filenames = []
    for msg in messages:
        message = Message(msg)
        if message.msg.is_multipart() and file_format in message.content_disposition:
            if message.attachment:
                filename = message.attachment_name
                filepath = make_filepath(folder_name, filename)
                if filepath in filenames:
                    index = filepath.find('.')
                    filepath = filepath[:index] + str(len(filenames)) + filepath[index:]
                open(filepath, "wb").write(message.attachment)
                filenames.append(filepath)
    return filenames


def text_parser(mailbox, target_subject, number):
    messages = mailbox_messages(mailbox, number)
    for msg in messages:
        message = Message(msg)
        if target_subject in message.subject:
            return message.body


def mailbox_messages(mailbox, quantity):
    mail = Email.instance()
    messages = mail.get_msg_list(mailbox, quantity)
    return messages


def mail_folders():
    mail = Email.instance()
    byte_list = mail.folders_bytes()
    folders = []
    encoding = 'utf-8'
    for item in byte_list:
        name = item.decode(encoding)
        name = name.split('"/"')
        folders.append(name[1][1:])
    return folders


def make_filepath(folder_name, filename):
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    filepath = os.path.join(folder_name, filename)
    return filepath
