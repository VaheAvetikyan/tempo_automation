import os

from services.email import Email
from services.message import Message


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
                with open(filepath, "ab") as f:
                    f.write(message.attachment)
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
                with open(filepath, "wb") as f:
                    f.write(message.attachment)
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
