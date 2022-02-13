import pandas as pd

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse
import re


class GoogleClient:

    def __init__(self, credentials_path):
        self._credentials = Credentials.from_service_account_file(
            credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])

    def read(self, url, sheet_name, first_row_as_header=False) -> pd.DataFrame:
        result = build('sheets', 'v4', credentials=self._credentials)\
            .spreadsheets()\
            .values()\
            .get(
                spreadsheetId=GoogleClient.get_spreadsheet_id_from_url(url),
                range=sheet_name)\
            .execute()

        data = result.get('values')

        res_df = pd.DataFrame(data).fillna(value="")

        if first_row_as_header and res_df.shape[0] > 0:
            res_df.columns = res_df.iloc[0]
            res_df = res_df[1:]

        return res_df


    @staticmethod
    def get_spreadsheet_id_from_url(url):
        path = urlparse(url).path

        res = re.search("spreadsheets/d/([^/]*).*", path)
        if res is None:
            raise ValueError(f"Couldn't extract google spreadsheet_id from url: {url}")

        return res.group(1)