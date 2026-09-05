import asyncio
import json
import time
from dataclasses import asdict, dataclass

from playwright.async_api import async_playwright


CLAN_ID = "1a68233f-ae59-431b-ba1b-e458b548acfa"
BASE_URL = "https://aml-api-eta.vercel.app"

start_time = time.time()


@dataclass
class Record:
    name: str
    skill_pt: int
    top: int
    link: str


@dataclass
class Member:
    id: str
    name: str
    youtube: str
    country: str
    total_skill_pt: int
    total_rng_pt: int
    modes_beaten: int
    records: list[Record]


async def fetch_json(page, url):
    response = await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=30_000
    )

    if response is None:
        raise Exception(f"No response received from {url}")

    if response.status != 200:
        body = await page.locator("body").inner_text()

        raise Exception(
            f"HTTP {response.status} {response.status_text}\n"
            f"URL: {url}\n"
            f"Body: {body[:500]}"
        )

    return await response.json()

async def get_members(page):
    url = f"{BASE_URL}/clans/{CLAN_ID}/members"

    results = await fetch_json(page, url)

    return (
        [member["user_id"] for member in results],
        [member["players"]["name"] for member in results]
    )


async def get_info(context, id, name, semaphore):
    async with semaphore:
        page = await context.new_page()

        try:
            print(f"Fetching {name}...")

            player_url = f"{BASE_URL}/player/{id}"
            modes_url = f"{BASE_URL}/player/{id}/records/skillValue"

            player_results = await fetch_json(page, player_url)
            modes_results = await fetch_json(page, modes_url)

            player_name = player_results["name"]
            player_youtuber = player_results["youtube"] or ""
            player_country = player_results["country"] or ""
            total_skill_pt = player_results["totalSkillpt"] or 0
            total_rng_pt = player_results["totalRNGpt"] or 0
            modes_beaten = player_results["modesBeaten"] or 0

            records = []

            if isinstance(modes_results, list):
                for mode in modes_results:
                    records.append(
                        Record(
                            mode["levels"]["name"],
                            mode["skillValue"],
                            mode["levels"]["top"],
                            mode["videoLink"]
                        )
                    )

            print(f"Successfully fetched {name}")

            return Member(
                id=id,
                name=player_name,
                youtube=player_youtuber,
                country=player_country,
                total_skill_pt=total_skill_pt,
                total_rng_pt=total_rng_pt,
                modes_beaten=modes_beaten,
                records=records
            )

        except Exception as e:
            print(f"Failed to fetch {name}: {e}")
            return None

        finally:
            await page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            )
        )

        try:
            page = await context.new_page()

            print("Fetching clan members...")

            members_id, members_names = await get_members(page)

            await page.close()

            print(f"Found {len(members_id)} members.")

            # Number of players being processed simultaneously.
            semaphore = asyncio.Semaphore(5)

            tasks = [
                get_info(context, id, name, semaphore)
                for id, name in zip(members_id, members_names)
            ]

            members = await asyncio.gather(*tasks)

            successful_members = [
                member for member in members
                if member is not None
            ]

            failed_count = len(members_id) - len(successful_members)

            print(
                f"Successfully fetched "
                f"{len(successful_members)}/{len(members_id)} members."
            )

            if failed_count > 0:
                print(
                    f"WARNING: {failed_count} member(s) failed. "
                    "members.json was NOT updated."
                )
                raise SystemExit(1)
            else:
                with open(
                    "resources/members.json",
                    "w",
                    encoding="utf-8"
                ) as file:
                    json.dump(
                        [asdict(member) for member in successful_members],
                        file,
                        indent=2,
                        ensure_ascii=False
                    )

                print("members.json updated successfully.")

            elapsed = time.time() - start_time

            print(
                f"Saved {len(members)} members "
                f"in {elapsed:.2f} seconds."
            )

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())