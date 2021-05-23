import imaplib
import os


class Email:
    _NUMBER_OF_MESSAGES = 5
    # account credentials
    _username = os.environ.get('EMAIL')
    _password = os.environ.get('EMAIL_PASS')
    # create an IMAP4 class with SSL
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    def __init__(self):
        self.login()

    def login(self):
        self.imap.login(self._username, self._password)

    def logout(self):
        self.imap.close()
        self.imap.logout()

    def get_message_list(self, target_mailbox):
        message_list = []
        messages = self._get_messages(target_mailbox)
        for i in range(messages, messages - self._NUMBER_OF_MESSAGES, -1):
            res, msg = self.imap.fetch(str(i), "(RFC822)")
            message_list.append(msg)
        return message_list

    def _get_messages(self, target_mailbox):
        status, messages = self.imap.select(mailbox=target_mailbox)
        messages = int(messages[0])
        return messages
