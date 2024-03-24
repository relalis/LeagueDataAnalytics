# summoner_handler.py

import aiohttp
import asyncio

async def get_current_match_participants(summoner_name, platform, RIOT_API_KEY):
    async with aiohttp.ClientSession() as session:
        players = []
        url = f"https://{platform}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
        async with session.get(url) as response:
            if response.status == 200:
                summoner_id = (await response.json())["id"]
                url = f"https://{platform}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={RIOT_API_KEY}"
                response = await session.get(url)
                if response.status == 200:
                    match_data = await response.json()
                    for participant in match_data['participants']:
                        players.append(participant)
                    return players
                else:
                    print(f"Failed to get match participants")

async def get_summoner_data(wllp):
    summoner = await (await wllp.request("GET", "/lol-summoner/v1/current-summoner")).json()
    return summoner

async def get_ranked_stats(wllp):

    ranked_stats = await (await wllp.request("GET", "/lol-ranked/v1/current-ranked-stats")).json()
    ranked_stats = ranked_stats["highestRankedEntry"]

    return ranked_stats