# birthday-calendar
This app pulls all contacts from your google account, that have a birthday set. Then it looks in your specified microsoft calendar, whether a matching event exists. If it doesn't find a matching event (by event subject), it creates an event series.

## Requirements
- python3.11
- pip-modules listed in requirements.txt

## Setup
### venv
- Create venv  
```python3 -m venv ./venv```
- activate venv  
```source /venv/bin/activate```
- install modules  
```pip install -r requirements.txt```

### Google Cloud
go to https://console.cloud.google.com  
- create a project
- enable the People API
- create credential "OAuth client ID"
- download credential file, put it into data/google as "credentials.json"
- configure "OAuth consent screen" and add test users (who are supposed to access the API)

### Azure
go to https://entra.microsoft.com/ -> Applications -> App registrations -> New registration
- Personal Microsoft Accounts only (alternatively you can use "Single tenant", for "multi-tenant" you have to verify the application)
- Redirect URI needs to include the same value as `redirect_uri` in data/settings.toml  

go to the now created application
- copy Client ID (and Tenant ID if app is in single-tenant mode), paste into settings.toml
- go to "API permissions", add delegated permissions `User.Read` and `Calendars.ReadWrite`

### data/settings.toml
- copy settings_sample.toml, create settings.toml
- set `tenant_id`

| value     | description                                 |
|-----------|---------------------------------------------|
| common    | for application in multi-tenant mode        |
| Tenant ID | for application in single-tenant mode       |
| consumers | for application in "Personal Accounts" mode |

- set `client_id`
- set `calendar_name` to the name of the calendar you want the events in

## Run the application
```python3 main.py```