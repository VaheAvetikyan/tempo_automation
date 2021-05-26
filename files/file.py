from email_service import mail_folders, attachment_parser


def get_mail_folders():
    folders = mail_folders()
    return folders


def download_file(mailbox, file_format, one_file, quantity):
    filenames = attachment_parser(mailbox, file_format, one_file, quantity)
    return filenames
