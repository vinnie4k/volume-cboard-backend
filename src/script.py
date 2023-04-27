from __future__ import print_function
from constants import *
from datetime import datetime

import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def get_daily_flyers():
    """
    Returns a list of upcoming flyers from today
    """
    flyers = get_upcoming_flyers()
    daily_flyers = []
    utc = pytz.UTC

    for flyer in flyers:
        date_string = flyer.get("endDate")
        date = utc.localize(datetime.strptime(date_string, DATETIME_FORMAT))
        if date.day == utc.localize(datetime.today()).day:
            daily_flyers.append(flyer)
    return daily_flyers


def get_weekly_flyers():
    """
    Returns a list of this week's flyers
    """
    flyers = get_flyers()
    weekly_flyers = []
    utc = pytz.UTC

    for flyer in flyers:
        date_string = flyer.get("endDate")
        date = utc.localize(datetime.strptime(date_string, DATETIME_FORMAT))
        diff = date - utc.localize(datetime.now())
        if 0 <= diff.days < 7:
            weekly_flyers.append(flyer)
    return weekly_flyers


def get_past_flyers():
    """
    Returns a list of all past flyers
    """
    flyers = get_flyers()
    past_flyers = []
    utc = pytz.UTC

    for flyer in flyers:
        date_string = flyer.get("endDate")
        date = utc.localize(datetime.strptime(date_string, DATETIME_FORMAT))
        if utc.localize(datetime.now()) > date:
            past_flyers.append(flyer)
    return past_flyers


def get_upcoming_flyers():
    """
    Returns a list of all upcoming flyers
    """
    flyers = get_flyers()
    upcoming_flyers = []
    utc = pytz.UTC

    for flyer in flyers:
        date_string = flyer.get("endDate")
        date = utc.localize(datetime.strptime(date_string, DATETIME_FORMAT))
        if utc.localize(datetime.now()) < date:
            upcoming_flyers.append(flyer)
    return upcoming_flyers


def get_slugs_org_map():
    """
    Returns key-value pairs of slugs and organizations
    The keys are slugs and the organization is the value
    """
    creds = get_creds()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=ORGANIZATIONS_RANGE).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return {}

        dict = {}
        for row in values:
            dict[row[2]] = {"id": row[0], "name": row[1],
                            "slug": row[2], "type": row[3]}
        return dict

    except HttpError as err:
        print(err)
        return None


def get_org_from_slug(slug):
    """
    Returns one organization given a slug
    """
    organizations = get_organizations()

    if organizations is None:
        return None

    for org in organizations:
        if org.get("slug") == slug:
            id = int(org.get("id"))
            row = str(id + 1)

            try:
                service = build('sheets', 'v4', credentials=creds)

                # Call the Sheets API
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                            range='Organizations!A' + row + ':D' + row).execute()
                values = result.get('values', [])

                if not values:
                    print('No data found.')
                    return {}

                for row in values:
                    return {"id": row[0], "name": row[1],
                            "slug": row[2], "type": row[3]}

            except HttpError as err:
                print(err)
                return None


def get_flyers():
    """
    Returns all flyers
    """
    creds = get_creds()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=FLYERS_RANGE).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return []

        map = get_slugs_org_map()
        flyers = []
        for row in values:
            slugs = row[2].split(', ')
            orgs = []
            for slug in slugs:
                orgs.append(map.get(slug))

            flyers.append({"id": row[0], "title": row[1],
                           "organizations": orgs, "startDate": row[3],
                           "endDate": row[4], "imageURL": row[5], "postURL": row[6],
                           "location": row[7]})
        return flyers

    except HttpError as err:
        print(err)
        return None


def get_organizations():
    """
    Returns all organizations
    """
    creds = get_creds()

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=ORGANIZATIONS_RANGE).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return []

        orgs = []
        for row in values:
            orgs.append({"id": row[0], "name": row[1],
                         "slug": row[2], "type": row[3]})
        return orgs

    except HttpError as err:
        print(err)
        return None


def get_creds():
    """
    Returns the credentials
    """
    creds = None
    if os.path.exists(TOKEN_DIR):
        creds = Credentials.from_authorized_user_file(TOKEN_DIR, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_DIR, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_DIR, 'w') as token:
            token.write(creds.to_json())

    return creds
