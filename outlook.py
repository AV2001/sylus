import requests
from msal import ConfidentialClientApplication
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Outlook:
    AUTHORITY = 'https://login.microsoftonline.com/common'
    SCOPES = ['User.Read', 'Mail.Read', 'Mail.Send', 'Mail.ReadWrite']
    BASE_URL = 'https://graph.microsoft.com/v1.0/me/'

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.msal_app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.AUTHORITY
        )

    def get_authorization_url(self, state):
        return self.msal_app.get_authorization_request_url(
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri,
            state=state
        )

    def acquire_token_by_code(self, code):
        return self.msal_app.acquire_token_by_authorization_code(
            code,
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

    def fetch_emails(self, access_token, date=None, sender=None):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Construct filter query
        filter_query = ""
        if date:
            filter_query += f"receivedDateTime ge {date}T00:00:00Z and receivedDateTime lt {date}T23:59:59Z"
        if sender:
            if filter_query:
                filter_query += " and "
            filter_query += f"from/emailAddress/address eq '{sender}'"

        # Construct request URL
        request_url = self.BASE_URL + "messages"
        if filter_query:
            request_url += f"?$filter={filter_query}"

        messages_response = requests.get(request_url, headers=headers)
        messages_response.raise_for_status()
        messages_data = messages_response.json().get('value', [])

        cleaned_messages = []
        for message in messages_data:
            html_content = message['body']['content']
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(['script', 'style']):
                script.extract()
            cleaned_text = soup.get_text()
            message['body']['content'] = cleaned_text
            cleaned_messages.append(message)
        return cleaned_messages

    def send_email(self, access_token, to_address, subject, content):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        body = {
            'message': {
                'subject': subject,
                'body': {
                    'contentType': 'HTML',
                    'content': content
                },
                'toRecipients': [
                    {
                        'emailAddress': {
                            'address': to_address
                        }
                    }
                ]
            }
        }
        response = requests.post(
            f'{self.BASE_URL}sendMail', headers=headers, json=body)
        response.raise_for_status()


# Instantiate Outlook with your credentials
APPLICATION_ID = os.getenv('APPLICATION_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'
outlook = Outlook(APPLICATION_ID, CLIENT_SECRET, REDIRECT_URI)
