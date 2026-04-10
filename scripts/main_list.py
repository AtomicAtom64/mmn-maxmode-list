import time
from urllib.parse import quote
from dataclasses import asdict, dataclass
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from get_docs import get_main_list

mode_entries = []  # list of (name, game)
modes = {}

start_time = time.time()
session = requests.Session()

@dataclass
class Mode:
    name: str
    game: str
    developer: str
    verifier: str
    length: str
    gameLink: str
    verifierLink: str
            
def find_info(session, query):
    query = query.strip()
    query = query.replace("’", "'")
    properQuery = query.replace(")", "")
    searchUrl = f"https://aml-api-eta.vercel.app/search/{quote(properQuery, safe='')}"

    r = session.get(searchUrl, timeout=10)
    if not r.ok:
        raise Exception(f"Search failed: {r.status_code}")

    results = r.json()
    data = results[0]
    if not data:
        raise ValueError(f"No matches found for '{query}'")

    match = next(
        (item for item in data if item["name"].strip().lower() == query.lower()),
        None
    )
    if not match:
        raise ValueError(f"Mode '{query}' not found in search results.")
    
    query = match["id"]
    modeUrl = f"https://aml-api-eta.vercel.app/level/{query}"
    
    r = session.get(modeUrl, timeout=10)
    data = r.json()
    modeData = data["data"]
    playerName = data["records"][0]["players"]["name"].strip()
    
    return Mode(
            name=modeData["name"].strip(),
            game=modeData["game"].strip(),
            developer=modeData["creator"].strip(),
            verifier=playerName,
            length=modeData["mmlength"].strip(),
            gameLink=modeData["link"].strip(),
            verifierLink=modeData["videoID"].strip()
        )

def fetch(entry, session):
    name, game = entry
    try:
        return find_info(session, name)
    except Exception as e:
        print(e)
        return None
    
texts = get_main_list()
for line in texts.splitlines():
    line = line.strip()
    if not line:
        continue

    parts = line.split(" - ", 1)
    if len(parts) != 2:
        continue  # skip malformed lines

    name, game = parts
    mode_entries.append((name.strip(), game.strip()))

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda entry: fetch(entry, session), mode_entries))

output = [asdict(mode) for mode in results if mode]
with open("resources/main_list.json", "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)
    
print(f"Finished in {time.time() - start_time:.2f} seconds")