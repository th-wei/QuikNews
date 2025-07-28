import os.path
from datetime import datetime
import time
import base64
import re
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json
SCOPES = ["https://mail.google.com/"]

def gmail_authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

def get_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

def get_content(service, messages):
    emails_data = []

    for msg in messages:
        msg_id = msg['id']
        msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()

        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')

        parts = payload.get('parts', [])
        body = ""

        def clean_html_content(html):
            """
            Cleans and normalizes HTML content using BeautifulSoup and regex.
            
            Args:
                html (str): Raw HTML content.

            Returns:
                str: Cleaned and normalized plain text.
            """
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text(separator="\n")  # Keep logical newlines

            # Normalize whitespace
            text = text.replace('\xa0', ' ')           # Non-breaking spaces → normal spaces
            text = re.sub(r'[ \t]+', ' ', text)        # Collapse tabs and multiple spaces
            text = re.sub(r'\n\s*\n+', '\n\n', text)   # Collapse multiple blank lines
            text = text.strip()                        # Trim leading/trailing whitespace

            return text


        def extract_parts(parts):
            nonlocal body
            for part in parts:
                mime_type = part.get('mimeType')
                if part.get('parts'):
                    extract_parts(part['parts'])
                elif mime_type in ['text/plain', 'text/html']:
                    data = part['body'].get('data')
                    if data:
                        decoded = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8')
                        if mime_type == 'text/html':
                            soup = BeautifulSoup(decoded, 'html.parser')
                            decoded = soup.get_text()
                        body += decoded + "\n"

        if 'data' in payload.get('body', {}):
            # Handle non-multipart emails
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        else:
            extract_parts(parts)

        emails_data.append({
            'subject': subject,
            'from': sender,
            'body': clean_html_content(body.strip())
        })
    return emails_data


def create_podcast_content():
    service = gmail_authenticate()

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    unix_todaystart = int(time.mktime(today_start.timetuple()))
    query = f'from:dan@axios.com after:{unix_todaystart}'
    print("Getting News After: " + str(today_start))
    emails = get_emails(service, query)

    if emails:
        news = get_content(service, emails)
        open("output.txt", "w").close()
        for content in news:
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(content['body'])
    else:
        print("No morning news.")