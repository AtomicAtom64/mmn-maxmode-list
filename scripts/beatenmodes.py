import os
import time
from dataclasses import asdict, dataclass
import requests
import json
from concurrent.futures import ThreadPoolExecutor

CLAN_ID = "1a68233f-ae59-431b-ba1b-e458b548acfa"

members = []

start_time = time.time()
@dataclass
class Record:
    name: str
    game: str
    skill: int
    rng: int
    link: str
    time: str
    top: int
    hardestSkill: bool = False
    hardestRng: bool = False

@dataclass
class Member:
    name: str
    records: list[Record]

def get_members(session):
    url = f"https://aml-api-eta.vercel.app/clans/{CLAN_ID}/members"
    r = session.get(url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch clan members: {r.status_code}")
    
    results = r.json()
    return [member["user_id"] for member in results], [member["players"]["name"] for member in results]

def get_info(session, id, name):
    modes_url = f"https://aml-api-eta.vercel.app/player/{id}/records/skillValue"
    r = session.get(modes_url, timeout=10)
    if not r.ok:
        raise Exception(
            f"Failed to fetch player modes for ID {id}: {r.status_code}"
        )

    modes_results = r.json()
    records = []

    if isinstance(modes_results, list):
        for mode in modes_results:
            mode_name = mode["levels"]["name"]
            mode_game = mode["levels"]["game"]
            skillpt = mode["skillValue"]
            rngpt = mode["rngValue"]
            link = mode["videoLink"]
            timestamp = mode["timestamp"]
            top = mode["levels"]["top"]

            records.append(
                Record(
                    mode_name,
                    mode_game,
                    skillpt,
                    rngpt,
                    link,
                    timestamp,
                    top
                )
            )

    return Member(name, records)

session = requests.Session()
members_id, members_names = get_members(session)

def fetch(id, name):
    try:
        return get_info(session, id, name)
    except Exception as e:
        print(f"Error fetching info for ID {id}: {e}")
        return None

with ThreadPoolExecutor(max_workers=5) as executor:
    members = list(executor.map(fetch, members_id, members_names))
    
members = [m for m in members if m is not None]

for member in members:

    if not member.records:
        continue

    hardest_skill = min(
        member.records,
        key=lambda record: record.top
    )
    
    hardest_skill.hardestSkill = True

    highest_rng = max(
        record.rng
        for record in member.records
    )

    for record in member.records:
        if record.rng == highest_rng:
            record.hardestRng = True

with open("resources/beaten_modes.json", "w") as file:
    json.dump([asdict(member) for member in members], file, indent=2)

print(f"Finished in {time.time() - start_time:.2f} seconds")