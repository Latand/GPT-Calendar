from gcsa.google_calendar import GoogleCalendar

"""
THIS SCRIPT SHOULD BE RUN DIRECTLY AND NOT IMPORTED

1. Get config.json following instructions from here:
https://google-calendar-simple-api.readthedocs.io/en/latest/getting_started.html#credentials
2. Save to infrastructure\google\creds\config.json
3. Run this script
4. Follow instructions in console
5. By the end you will have token.pickle file in this folder

"""

if __name__ == "__main__":
    GoogleCalendar(credentials_path="config.json", token_path="token.pickle")
