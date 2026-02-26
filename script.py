from urllib.parse import quote
import requests

modesTxt = {}
modes = {}

class Mode:
    def __init__(self, name, game, developer, verifier, length, gameLink, verifierLink):
        self.name = name
        self.game = game
        self.developer = developer
        self.verifier = verifier
        self.length = length
        self.gameLink = gameLink
        self.verifierLink = verifierLink
        
def find_info(query):
    query = query.strip()
    searchUrl = f"https://aml-api-eta.vercel.app/search/{quote(query)}"

    r = requests.get(searchUrl)
    results = r.json()

    data = results[0]

    match = next(
        (item for item in data if item["name"].strip() == query),
        None
    )
    
    if not match:
        raise ValueError(f"Mode '{query}' not found in search results.")
    
    query = match["id"]
    modeUrl = f"https://aml-api-eta.vercel.app/level/{query}"
    
    r = requests.get(modeUrl)
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
            modes[mode] = find_info(mode)
        except ValueError as e:
            print(e)
            
for mode in modes:
    print(f"Name: {modes[mode].name}")
    print(f"Game: {modes[mode].game}")
    print(f"Developer: {modes[mode].developer}")
    print(f"Verifier: {modes[mode].verifier}")
    print(f"Length: {modes[mode].length}")
    print(f"Game Link: {modes[mode].gameLink}")
    print(f"Verifier Link: {modes[mode].verifierLink}")
    print("\n")

with open("modes.json", "w") as file:
    file.write("[")
    file.write("\n]")
    