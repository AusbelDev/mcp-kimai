# msal_outlook_calendar.py
import datetime as dt
import json
import logging
import os
import sys
from typing import Dict, List, Optional

import msal
import requests
from dotenv import load_dotenv

load_dotenv()
TENANT_ID = os.getenv("OUTLOOK_TENANT_ID")
CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TIMEZONE = os.getenv("OUTLOOK_TIMEZONE", "UTC")
PREFERRED_USERNAME = os.getenv("OUTLOOK_MSAL_USERNAME")

if not TENANT_ID or not CLIENT_ID:
    sys.exit("Set TENANT_ID and CLIENT_ID in .env")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Calendars.Read"]  # keep this stable across runs
GRAPH = "https://graph.microsoft.com/v1.0"


class OutlookService:
    def __init__(self):
        self.token = self.get_token()

    # ---- stable cache path (no extra deps) ----
    def cache_path(self) -> str:
        if os.name == "nt":  # Windows
            base = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
            return os.path.join(base, "msal_cache", f"{CLIENT_ID}.bin")
        else:
            base = os.path.join(os.path.expanduser("~"), ".config", "msal")
            return os.path.join(base, f"{CLIENT_ID}.bin")

    def ensure_dir(self, p: str):
        d = os.path.dirname(p)
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)

    def load_cache(self) -> msal.SerializableTokenCache:
        c = msal.SerializableTokenCache()
        p = self.cache_path()
        if os.path.exists(p):
            with open(p, "r") as f:
                c.deserialize(f.read())
        return c

    def save_cache(self, c: msal.SerializableTokenCache):
        if c.has_state_changed:
            p = self.cache_path()
            self.ensure_dir(p)
            with open(p, "w") as f:
                f.write(c.serialize())

    def pick_account(
        self, app: msal.PublicClientApplication, preferred: Optional[str] = None
    ):
        accts = app.get_accounts()
        if not accts:
            return None
        if preferred:
            for a in accts:
                if a.get("username") and a["username"].lower() == preferred.lower():
                    return a
        return accts[0]  # first known account

    def get_token(self) -> str:
        cache = self.load_cache()
        app = msal.PublicClientApplication(
            client_id=CLIENT_ID, authority=AUTHORITY, token_cache=cache
        )

        account = self.pick_account(app, PREFERRED_USERNAME)
        result = app.acquire_token_silent(SCOPES, account=account)

        if not result:
            # First time (or cache invalid) → device code
            flow = app.initiate_device_flow(scopes=SCOPES)
            if "user_code" not in flow:
                raise RuntimeError(
                    "Failed to start device flow. Check app registration and delegated permissions."
                )
            logger.info("\n=== DEVICE LOGIN ===")
            logger.info(
                f"Go to: {flow['verification_uri']}\nCode : {flow['user_code']}\n"
            )
            result = app.acquire_token_by_device_flow(flow)

        if "access_token" not in result:
            raise RuntimeError(f"Auth error: {result}")

        self.save_cache(cache)
        return result["access_token"]

    def iso(self, dt_obj: dt.datetime) -> str:
        if dt_obj.tzinfo is None:
            dt_obj = dt_obj.replace(tzinfo=dt.timezone.utc)
        return dt_obj.isoformat()

    def fetch_calendar_view(
        self, token: str, start: dt.datetime, end: dt.datetime
    ) -> List[Dict]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Prefer": f'outlook.timezone="{TIMEZONE}"',
        }
        params = {
            "startDateTime": self.iso(start),
            "endDateTime": self.iso(end),
            "$select": "id,subject,organizer,start,end,location,isAllDay,onlineMeetingUrl,webLink",
            "$orderby": "start/dateTime",
            "$top": "50",
        }
        url = f"{GRAPH}/me/calendarView"
        items: List[Dict] = []
        while url:
            r = requests.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
            items.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
            params = None
        return items

    def get_outlook_events(self, start: dt.datetime, end: dt.datetime) -> List[Dict]:
        events = self.fetch_calendar_view(self.token, start, end)
        return events

    def main(self):
        now = dt.datetime.now(dt.timezone.utc)
        token = self.get_token()
        events = self.fetch_calendar_view(token, now, now + dt.timedelta(days=7))
        print(f"Fetched {len(events)} events shown in {TIMEZONE}.")
        # Save events to a JSON file
        try:
            print(os.path.exists("./outlook_events"))
            if os.path.exists("./outlook_events"):
                with open(
                    "./outlook_events/outlook_events.json", "w", encoding="utf-8"
                ) as f:
                    json.dump(events, f, ensure_ascii=False, indent=4)
                print("Events saved to /outlook_events/outlook_events.json")

        except Exception as e:
            print(f"Failed to save events: {e}")


if __name__ == "__main__":
    outlook_events = OutlookService()
    outlook_events.main()
