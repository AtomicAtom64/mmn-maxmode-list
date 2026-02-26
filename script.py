from urllib.parse import quote
from dataclasses import asdict, dataclass
import requests
import json

modesTxt = {}
modes = {}
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


with open("list.txt", "r") as file:
    for line in file:
        line = line.strip() 
        if not line:
            continue
        info = line.split(" - ")
        name = info[0].strip()
        game = info[1].strip()
        modesTxt[name] = game

for mode in modesTxt:
        try:
            modes[mode] = find_info(session, mode)
        except ValueError as e:
            print(e)
            
output = []
session.close()
for mode, modeData in modes.items():
    output = [asdict(mode) for mode in modes.values()]

with open("modes.json", "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)