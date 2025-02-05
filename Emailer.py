import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

class Emailer:

    def __init__(self):
        self.SCOPES = "https://www.googleapis.com/auth/gmail.send"
        self.flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
        self.creds = self.flow.run_local_server(port=0)
        self.service = build('gmail', 'v1', credentials=self.creds)
    #This should only be called when the stock state is different than the known state
    def sendStockEmail(self, product: str, newStockState: str):
        message = MIMEText(f'The product {product} has changed stock availibility to {newStockState} ')
        message['to'] = 'smith.ethan133@gmail.com'
        message['subject'] = f'{product} is now {newStockState}'
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            message = (self.service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message successfully')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None

    def sendPriceEmail(product: str):
        pass

