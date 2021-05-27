import email
from email.header import decode_header


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

    def _pars_single_message(self):
        self.content_type = self.msg.get_content_type()
        self.body = self.msg.get_payload(decode=True).decode()
