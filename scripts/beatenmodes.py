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

    return [
        (member["user_id"], member["players"]["name"])
        for member in results
    ]


async def get_info(context, id, name, semaphore):
    async with semaphore:
        page = await context.new_page()

        try:
            print(f"Fetching {name}...")

            modes_url = f"{BASE_URL}/player/{id}/records/skillValue"

            modes_results = await fetch_json(page, modes_url)

            records = []

            if isinstance(modes_results, list):
                for mode in modes_results:
                    records.append(
                        Record(
                            name=mode["levels"]["name"],
                            game=mode["levels"]["game"],
                            skill=mode["skillValue"],
                            rng=mode["rngValue"],
                            link=mode["videoLink"],
                            time=mode["timestamp"],
                            top=mode["levels"]["top"]
                        )
                    )

            return Member(
                name=name,
                records=records
            )

        except Exception as e:
            print(f"Error fetching {name}: {e}")
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

            members = await get_members(page)

            await page.close()

            print(f"Found {len(members)} members.")

            semaphore = asyncio.Semaphore(5)

            tasks = [
                get_info(context, user_id, name, semaphore)
                for user_id, name in members
            ]

            members = await asyncio.gather(*tasks)

            successful_members = [
                member for member in members
                if member is not None
            ]

            print(
                f"Successfully fetched "
                f"{len(successful_members)}/{len(members)} members."
            )

            if len(successful_members) != len(members):
                print(
                    "ERROR: Some members failed. "
                    "Output file was NOT updated."
                )
                raise SystemExit(1)

            for member in successful_members:
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

            with open(
                "resources/beaten_modes.json",
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    [asdict(member) for member in successful_members],
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            print(
                f"Finished in "
                f"{time.time() - start_time:.2f} seconds"
            )

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())