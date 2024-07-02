import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleManager:
    def __init__(self):
        self.creds = None
        self.service = None
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/cloud-platform"
        ]

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

    def create_places_service(self, key):
        return build("places", "v1", credentials=self.creds)

    def create_google_sheets_file(self, title):
        try:
            service = build("sheets", "v4", credentials=self.creds)
            spreadsheet = {"properties": {"title": title}}
            spreadsheet = (
                service.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
            return spreadsheet.get("spreadsheetId")
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
    
    def read(self, spreadsheet_id, range):
        try:
            service = build("sheets", "v4", credentials=self.creds)

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=spreadsheet_id, range=range)
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return

            return values
        except HttpError as err:
            print(err)
        
    def update(self, spreadsheet_id, range_name, value_input_option, _values):
        try:
            service = build("sheets", "v4", credentials=self.creds)
            
            body = {"values": _values}
            
            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )
            print(f"{result.get('updatedCells')} cells updated.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return error
