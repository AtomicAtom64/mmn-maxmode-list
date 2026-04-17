import time
from urllib.parse import quote
from dataclasses import asdict, dataclass
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from get_docs import get_main_list

mode_entries = []  # list of (name, game, custom name)

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
            
def find_info(session, name, game, custom_name=None):

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
            name=custom_name or modeData["name"].strip(),
            game=modeData["game"].strip(),
            developer=modeData["creator"].strip(),
            verifier=playerName,
            length=modeData["mmlength"].strip(),
            gameLink=modeData["link"].strip(),
            verifierLink=modeData["videoID"].strip()
        )

def fetch(entry, session):
    name, game, custom_name = entry
    try:
        return find_info(session, name, game, custom_name)
    except Exception as e:
        print(e)
        error_log.write(f"{e}\n")
        return None
    
texts = get_main_list()
modes_list = session.get("https://aml-api-eta.vercel.app/levels/ml/page/all/", timeout=10)
modes_list = modes_list.json()

for line in texts.splitlines():
    line = line.strip()
    if not line:
        continue
    
    custom_name = None
    if " $ " in line:
        parts = line.split(" $ ", 1)
        if len(parts) != 2:
            continue  # skip malformed lines
        custom_name = parts[1].strip()
        line = parts[0]

    parts = line.split(" - ", 1)
    if len(parts) != 2:
        continue  # skip malformed lines

    name, game = parts
    mode_entries.append((name.strip(), game.strip(), custom_name))

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda entry: fetch(entry, session), mode_entries))

output = [asdict(mode) for mode in results if mode]
with open("resources/main_list.json", "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)
    
print(f"Finished in {time.time() - start_time:.2f} seconds")
error_log.close()