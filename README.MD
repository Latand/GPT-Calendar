# GPT-Calendar bot

This bot enables you to manage your Google Calendar from Telegram with text thanks to the power of GPT.

## How to use
1. [Create a new Google Cloud Platform (GCP) project](https://developers.google.com/workspace/guides/create-project)
2. You will need to enable the “Google Calendar API” for your project in order to use the API. You can do this by navigating to the [Google Calendar API page](https://console.developers.google.com/apis/library/calendar-json.googleapis.com) and clicking “Enable”.
3. [Configure the OAuth consent screen](https://developers.google.com/workspace/guides/configure-oauth-consent)
4. [Create a OAuth client ID credential and download the `config.json` file](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
5. Place config.json in `infrastructure/function_services/creds/config.json`
6. Run file [get_credentials.py](infrastructure%2Ffunction_services%2Fcreds%2Fget_credentials.py)
7. Follow the instructions in the file 
8. Install docker and docker-compose
9. Copy .env.dist to .env and fill in the variables (BOT_TOKEN, OPENAI_API_KEY)
10. Run `docker-compose up -d`