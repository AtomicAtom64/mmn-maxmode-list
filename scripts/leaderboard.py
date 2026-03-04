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
    youtube_link: str

@dataclass
class Member:
    id: str
    name: str
    total_skill_pt: int
    records: list[Record]

def get_members(session):
    url = f"https://aml-api-eta.vercel.app/clans/{CLAN_ID}/members"
    r = session.get(url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch clan members: {r.status_code}")
    
    results = r.json()
    return [member["user_id"] for member in results]

def get_info(session, id):
    player_url = f"https://aml-api-eta.vercel.app/player/{id}/"
    
    r = session.get(player_url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch player info for ID {id}: {r.status_code}")
    
    results = r.json()
    player_name = results["name"].strip()
    total_skill_pt = int(results["totalSkillpt"] or 0)
    
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
            link = mode["videoLink"]
            records.append(Record(mode_name, skillpt, link))
    
    return Member(id, player_name, total_skill_pt, records)  

session = requests.Session()
members_id = get_members(session)

def fetch(id):
    try:
        return get_info(session, id)
    except Exception as e:
        print(f"Error fetching info for ID {id}: {e}")
        return None

with ThreadPoolExecutor(max_workers=5) as executor:
    members = list(executor.map(fetch, members_id))
    
members = [m for m in members if m is not None]

with open("resources/members.json", "w") as file:
    json.dump([asdict(member) for member in members], file, indent=2)

print(f"Finished in {time.time() - start_time:.2f} seconds")