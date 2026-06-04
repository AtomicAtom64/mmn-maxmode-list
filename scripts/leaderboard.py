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
    skill_pt: int
    rng_pt: int
    top: int
    link: str

@dataclass
class Member:
    id: str
    name: str
    youtube: str
    country: str
    continent: str
    total_skill_pt: int
    total_rng_pt: int
    modes_beaten: int
    records: list[Record]

def get_members(session):
    url = f"https://aml-api-eta.vercel.app/clans/{CLAN_ID}/members"
    r = session.get(url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch clan members: {r.status_code}")
    
    results = r.json()
    return [member["user_id"] for member in results], [member["players"]["name"] for member in results]

def get_info(session, id, name):
    
    player_url = f"https://aml-api-eta.vercel.app/player/{id}"

    modes_url = f"https://aml-api-eta.vercel.app/player/{id}/records/skillValue"
    
    r = session.get(player_url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch player info for ID {id}: {r.status_code}")
    
    player_results = r.json()
    player_name = player_results["name"]
    player_youtuber = player_results["youtube"] or ""
    player_country = player_results["country"] or ""
    player_continent = player_results["continent"] or ""
    total_skill_pt = player_results["totalSkillpt"] or 0
    total_rng_pt = player_results["totalRNGpt"] or 0
    modesBeaten = player_results["modesBeaten"] or 0
    
    r = session.get(modes_url, timeout=10)
    if not r.ok:
        raise Exception(f"Failed to fetch player modes for ID {id}: {r.status_code}")
        
    modes_results = r.json()
    records = []
    
    if isinstance(modes_results, list):
        for mode in modes_results:
            mode_name = mode["levels"]["name"]
            skillpt = mode["skillValue"]
            rngpt = mode["rngValue"]
            top = mode["levels"]["top"]
            link = mode["videoLink"]
            records.append(Record(mode_name, skillpt, rngpt, top, link))
    
    return Member(id, player_name, player_youtuber, player_country, player_continent, total_skill_pt, total_rng_pt, modesBeaten, records)

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