import asyncio
import json
import time

import countryflag
from playwright.async_api import async_playwright


CLAN_ID = "1a68233f-ae59-431b-ba1b-e458b548acfa"
BASE_URL = "https://aml-api-eta.vercel.app"

start_time = time.time()


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


async def get_country(context, user_id, name, semaphore):
    async with semaphore:
        page = await context.new_page()

        try:
            print(f"Fetching {name}...")

            url = f"{BASE_URL}/player/{user_id}"
            player = await fetch_json(page, url)

            return player.get("country", "")

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
                get_country(context, user_id, name, semaphore)
                for user_id, name in members
            ]

            results = await asyncio.gather(*tasks)

            countries = sorted({
                country
                for country in results
                if country
            })

            mapping = {
                country: countryflag.getflag([country])
                for country in countries
            }

            with open(
                "resources/countries.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    mapping,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            print(f"Found {len(countries)} countries.")
            print(
                f"Finished in "
                f"{time.time() - start_time:.2f} seconds"
            )

        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())