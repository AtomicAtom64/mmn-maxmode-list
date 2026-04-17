import time
from dataclasses import dataclass
import requests
from concurrent.futures import ThreadPoolExecutor

mode_entries = []  # list of (name, game)

start_time = time.time()
session = requests.Session()

error_log = open("scripts/errors.txt", "w")

@dataclass
class Mode:
    name: str
    game: str
    developer: str
    verifier: str
    length: str
    gameLink: str
    verifierLink: str
            
def find_info(session, name, game):

    match = next(
        (m for m in modes_list if m["name"].strip().lower() == name.lower() and m["game"].strip().lower() == game.lower()), # type: ignore
        None
    )
    if match is None:
        raise ValueError(f"No match found for '{name}' in '{game}'")

    query = match["id"] # type: ignore
    modeUrl = f"https://aml-api-eta.vercel.app/level/{query}"
    
    r = session.get(modeUrl, timeout=10)
    data = r.json()
    modeData = data["data"]
    playerName = data["records"][0]["players"]["name"].strip() if data["records"] else ""
    
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
        return find_info(session, name, game)
    except Exception as e:
        print(e)
        error_log.write(f"{e}\n")
        return None
    
with open("scripts/modes.txt", "r") as texts:
    for line in texts:
        line = line.strip()
        if not line:
            continue

        parts = line.split(" - ", 1)
        if len(parts) != 2:
            continue  # skip malformed lines

        name, game = parts
        mode_entries.append((name.strip(), game.strip()))
        
modes_list = session.get("https://aml-api-eta.vercel.app/levels/ml/page/all/", timeout=10)
modes_list = modes_list.json()

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda entry: fetch(entry, session), mode_entries))
    
print(f"Finished in {time.time() - start_time:.2f} seconds")
error_log.close()