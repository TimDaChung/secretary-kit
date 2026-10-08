"""Fetch Slack List items assigned to the user, entirely in memory.

Reads config.report_lists[] (enabled entries only), calls files.info for the
status option labels, paginates slackLists.items.list, and prints one JSON
object to stdout. Writes no files, so there is nothing to clean up afterwards.

Usage: python report_lists.py [--config PATH]
Output: {"<list_id>": {"ok": true, "total": N, "items": [{"id", "name", "status"}]}}
        or {"<list_id>": {"ok": false, "error": "..."}}; {"skipped": "..."} when no token.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://slack.com/api/"
MAX_PAGES = 50


def get_token() -> str | None:
    token = os.environ.get("SLACK_USER_TOKEN")
    if token or sys.platform != "win32":
        return token
    # User-level env var not inherited by this process yet
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, "SLACK_USER_TOKEN")[0]
    except OSError:
        return None


def call(method: str, params: dict[str, str], token: str) -> dict:
    url = f"{API}{method}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def status_labels(list_id: str, status_col: str, token: str) -> dict[str, str]:
    info = call("files.info", {"file": list_id}, token)
    if not info.get("ok"):
        raise RuntimeError(f"files.info: {info.get('error')}")
    schema = info.get("file", {}).get("list_metadata", {}).get("schema", [])
    for col in schema:
        if col.get("id") == status_col:
            choices = (col.get("options") or {}).get("choices", [])
            return {c.get("value"): c.get("label") for c in choices}
    return {}


def fetch_items(list_id: str, token: str) -> list[dict]:
    items: list[dict] = []
    cursor = ""
    for _ in range(MAX_PAGES):
        params = {"list_id": list_id, "limit": "100"}
        if cursor:
            params["cursor"] = cursor
        page = call("slackLists.items.list", params, token)
        if not page.get("ok"):
            raise RuntimeError(f"slackLists.items.list: {page.get('error')}")
        items.extend(page.get("items", []))
        cursor = page.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            break
    return items


def mine(entry: dict, user_id: str, token: str) -> dict:
    list_id = entry["list_id"]
    assignee_cols = entry.get("assignee_cols") or [entry.get("assignee_col")]
    labels = status_labels(list_id, entry["status_col"], token)
    all_items = fetch_items(list_id, token)
    result = []
    for item in all_items:
        fields = {f.get("column_id"): f for f in item.get("fields", [])}
        if not any(user_id in (fields.get(c, {}).get("user") or []) for c in assignee_cols):
            continue
        status_raw = (fields.get(entry["status_col"], {}).get("select") or [None])[0]
        result.append({
            "id": item.get("id"),
            "name": fields.get(entry["name_col"], {}).get("text"),
            "status": labels.get(status_raw, status_raw),
        })
    return {"ok": True, "total": len(all_items), "items": result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(Path.home() / "secretary-data" / "config.json"))
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    token = get_token()
    if not token:
        print(json.dumps({"skipped": "no SLACK_USER_TOKEN"}))
        return
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    default_user = config.get("user", {}).get("user_id", "")

    out: dict[str, dict] = {}
    for entry in config.get("report_lists", []):
        if not entry.get("enabled"):
            continue
        user_id = entry.get("assignee_user_id") or default_user
        try:
            out[entry["list_id"]] = mine(entry, user_id, token)
        except Exception as e:  # report per-list failure, keep other lists going
            out[entry["list_id"]] = {"ok": False, "error": str(e)}
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
