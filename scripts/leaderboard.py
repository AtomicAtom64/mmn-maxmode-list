import os
import time
from dataclasses import asdict, dataclass
from dotenv import load_dotenv
import requests
import json
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

CLAN_ID = os.getenv('CLAN_ID')

members = []

start_time = time.time()
@dataclass
class Record:
    mode_name: str
    mode_skill_pt: int
    mode_rng_pt: int
    youtube_link: str

@dataclass
class Member:
    id: str
    name: str
    total_skill_pt: int
    total_rng_pt: int
    records: list[Record]

def get_members(session):
    url = f"https://aml-api-eta.vercel.app/clans/{CLAN_ID}/members"
    r = session.get(url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch clan members: {r.status_code}")
    
    results = r.json()
    return [member["user_id"] for member in results], [member["players"]["name"] for member in results]

def get_info(session, id, name):
    player_name = name

    modes_url = f"https://aml-api-eta.vercel.app/player/{id}/records/skillValue"
    
    r = session.get(modes_url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch player modes for ID {id}: {r.status_code}")
        
    modes_results = r.json()
    records = []
    
    if isinstance(modes_results, list):
        for mode in modes_results:
            mode_name = mode["levels"]["name"]
            skillpt = int(mode.get("skillValue") or 0)
            rngpt = int(mode.get("rngValue") or 0)
            link = mode["videoLink"]
            records.append(Record(mode_name, skillpt, rngpt, link))
            
    total_skill_pt = sum(record.mode_skill_pt for record in records)
    total_rng_pt = sum(record.mode_rng_pt for record in records)
    
    return Member(id, player_name, total_skill_pt, total_rng_pt, records)

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

with open("resources/members.json", "w") as file:
    json.dump([asdict(member) for member in members], file, indent=2)

print(f"Finished in {time.time() - start_time:.2f} seconds")