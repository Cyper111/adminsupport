import os
import imaplib
import email
import datetime
import zipfile
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from email.header import decode_header

def connect_to_email(imap_server, email_address, password):
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, password)
    return imap

def search_emails(imap, since_date_str, before_date_str):
    imap.select("Inbox")
    status, msgnums = imap.search(None, 'SINCE', since_date_str, 'BEFORE', before_date_str)
    if status != 'OK':
        raise ValueError("Failed to search emails.")
    return msgnums[0].split()



def process_emails(imap, msgnums):
    base_dir = r'D:\Scripts\emaildownloads' #change for directory
    Path(base_dir).mkdir(exist_ok=True)
    print(f"Directory '{base_dir}' created successfully")

    for msgnum in msgnums:
        try:
            _, data = imap.fetch(msgnum, "(RFC822)")
            message = email.message_from_bytes(data[0][1])
            subject = message.get('Subject')
            decoded_subject = decode_header(subject)[0][0]
            if isinstance(decoded_subject, bytes):
                decoded_subject = decoded_subject.decode('utf-8')
            else:
                decoded_subject = str(decoded_subject)
            
            # Sanitize subject for use as a directory name
            sanitized_subject = sanitize_filename(decoded_subject)
            email_dir = os.path.join(base_dir, sanitized_subject)
            Path(email_dir).mkdir(exist_ok=True)
            print(f"Processing: {sanitized_subject}")
            
            download_attachments(message, email_dir)

            zip_filename = sanitized_subject + ".zip"
            zip_filepath = os.path.join(base_dir, zip_filename)
            create_zip(email_dir, zip_filepath)

            cleanup_directory(email_dir)
            print(f"Processed and zipped: {sanitized_subject}")
        except Exception as e:
            print(f"Error processing email '{sanitized_subject}' [{msgnum}]: {e}. Skipping...")
            continue

def sanitize_filename(filename):
    # Replace invalid characters with an underscore
    filename = re.sub(r'[\<\>:\"/\|?\*]', '_', filename)
    # Remove control characters
    filename = re.sub(r'[\x00-\x1F\x7F]', '', filename)
    # Replace characters like newline (\n) and carriage return (\r) with an underscore
    filename = re.sub(r'[\r\n]', '_', filename)
    # Trim spaces at the beginning and end
    filename = filename.strip()
    # Ensure the filename does not end with a period (Windows does not allow this)
    filename = re.sub(r'\.$', '_', filename)
    # Optional: truncate long filenames to avoid issues with filesystem limits
    filename = (filename[:250]) if len(filename) > 250 else filename
    return filename


def download_attachments(message, email_dir):
    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        filename = part.get_filename()
        if not filename:
            # If there is no filename, it's likely the message body
            content_type = part.get_content_type()
            if 'text/plain' in content_type:
                # If it's plain text, save it as a text file
                file_path = os.path.join(email_dir, "message_body.txt")
                with open(file_path, 'wb') as fp:
                    fp.write(part.get_payload(decode=True))
                print(f'Downloaded message body as "message_body.txt" from the email.')
        else:
            # If there is a filename, it's an attachment
            file_path = os.path.join(email_dir, filename)
            with open(file_path, 'wb') as fp:
                fp.write(part.get_payload(decode=True))
            print(f'Downloaded "{filename}" from the email.')


def create_zip(source_dir, zip_filepath):
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as z:
        for foldername, _, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                z.write(file_path, os.path.relpath(file_path, source_dir))
    print(f"Created zip at: {zip_filepath}")

def cleanup_directory(directory_path):
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for filename in files:
            file_path = os.path.join(root, filename)
            os.unlink(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)
    print(f"Cleaned up: {directory_path}")


if __name__ == "__main__":
    imap_server = "imap.gmail.com"
    email_address = "email@gmail.com" #change to your email
    password = input("Enter your password: ") #for gmail use app password

    # Dates for searching emails
    one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=2)
    one_week_ago_str = one_week_ago.strftime('%d-%b-%Y')
    tomorrow_str = tomorrow.strftime('%d-%b-%Y')

    try:
        imap = connect_to_email(imap_server, email_address, password)
        print("Connected to email server successfully.")
        
        msgnums = search_emails(imap, one_week_ago_str, tomorrow_str)
        if msgnums:
            print(f"Found {len(msgnums)} emails to process.")
            process_emails(imap, msgnums)
        else:
            print("No emails found in the specified date range.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        pass
    
    finally:
        imap.close()
        imap.logout()
        print("Logged out from the email server.")


