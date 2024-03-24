# runeloader.py

import asyncio
import aiohttp
import json

async def get_versions_file(session):
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    async with session.get(url) as response:
        return await response.json()

async def get_ddragon_runes(session):
    versions = await get_versions_file(session)
    url = f"https://ddragon.leagueoflegends.com/cdn/{versions[0]}/data/en_US/runesReforged.json"
    async with session.get(url) as response:
        return await response.json()

async def fetch_rune_icon(session, iconfile):
    url = f"https://ddragon.leagueoflegends.com/cdn/img/{iconfile}"
    async with session.get(url) as response:
        return await response.read()

async def load_all_rune_icons():
    async with aiohttp.ClientSession() as session:
        tasks = []
        rune_icons = {}
        rune_info = await get_ddragon_runes(session)

        for keystone in rune_info:
            for slot in keystone["slots"]:
                for rune in slot["runes"]:
                    iconfile = rune["icon"]
                    if iconfile not in rune_icons:
                        task = asyncio.ensure_future(fetch_rune_icon(session, iconfile))
                        tasks.append(task)
                        rune_icons[iconfile] = task

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Replace tasks with their results (icon content)
        for iconfile, task in rune_icons.items():
            rune_icons[iconfile] = task.result()

        print("Loaded runes")
        return (rune_icons, rune_info)
