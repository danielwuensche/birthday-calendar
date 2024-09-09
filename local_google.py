import os.path
from local_classes import Birthday
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def authenticate(scopes: list[str]):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("data/google/token.json"):
        creds = Credentials.from_authorized_user_file("data/google/token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "data/google/credentials.json", scopes
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("data/google/token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_contacts(credentials):
    try:
        service = build("people", "v1", credentials=credentials)

        # Call the People API
        results = (
            service.people()
            .connections()
            .list(
                resourceName="people/me",
                pageSize=1000,
                personFields="names,birthdays",
            )
            .execute()
        )
        connections = results.get("connections", [])
        return connections
    except HttpError as err:
        print(err)


def get_birthdays(settings) -> list[Birthday]:
    creds = authenticate(settings["scopes"])
    connections = get_contacts(creds)

    out_birthdays = []
    for person in connections:
        birthdays = person.get("birthdays", [])
        names = person.get("names", [])
        if not birthdays or not names:
            continue

        birthday = birthdays[0].get("date")
        day = birthday["day"]
        month = birthday["month"]
        # if the birthday year has not been set, the value might be 1604 or the key might not exist
        if ("year" in birthday.keys() and birthday["year"] == 1604) or "year" not in birthday.keys():
            year = 2020
        else:
            year = birthday["year"]
        name = names[0].get("displayName")

        out_birthdays.append(Birthday(name, datetime.date(year=year, month=month, day=day)))

    return out_birthdays