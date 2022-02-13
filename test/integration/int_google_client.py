import config
from functions.services.google.google_client import GoogleClient


class GoogleClientInt:
    def __init__(self):
        self.ggl_client = GoogleClient(config.GOOGLE_API_CREDENTIALS_PATH)

    def test_read(self):
        sheets_url = "https://docs.google.com/spreadsheets/d/12gAIjbJdRe23yV8tTs233oOSN_MDXqMy95YUEWr_ogY"
        tab_name = "Orders2!1:10"

        res = self.ggl_client.read(sheets_url, tab_name, first_row_as_header=True)
        print(res)


GoogleClientInt().test_read()