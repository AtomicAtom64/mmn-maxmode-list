import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor
import countryflag

CLAN_ID = "1a68233f-ae59-431b-ba1b-e458b548acfa"

start_time = time.time()


def get_members(session):
    url = f"https://aml-api-eta.vercel.app/clans/{CLAN_ID}/members"

    r = session.get(url, timeout=10)
    r.raise_for_status()

    results = r.json()

    return [
        (member["user_id"], member["players"]["name"])
        for member in results
    ]


def get_country(session, user_id, name):
    try:
        url = f"https://aml-api-eta.vercel.app/player/{user_id}"

        r = session.get(url, timeout=10)
        r.raise_for_status()

        player = r.json()

        return {
            "country": player.get("country", "")
        }

    except Exception as e:
        print(f"Error fetching {name}: {e}")
        return None


session = requests.Session()

members = get_members(session)

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(
        executor.map(
            lambda member: get_country(session, member[0], member[1]),
            members
        )
    )

countries = sorted({
    r["country"]
    for r in results
    if r["country"]
})

mapping = {
    country: countryflag.getflag([country])
    for country in countries
}

with open("resources/countries.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"Finished in {time.time() - start_time:.2f} seconds")