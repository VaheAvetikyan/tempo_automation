import imaplib
import os


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
