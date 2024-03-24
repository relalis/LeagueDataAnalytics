#!/usr/local/bin/python3

# main.py

import asyncio, threading
from willump import Willump
from gameflow_ui import GameFlowUI
import summoner_handler
import runeloader

RIOT_API_KEY = "RIOT_API_KEY_HERE"
lol_lp_initial = 0
lol_lp_gain_session = 0
summoner_name = None
platform_id = None
wllp = None

def sort_players_by_role(players):
    role_order = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
    sorted_players = sorted(players, key=lambda x: role_order.index(x["selectedPosition"]))
    return sorted_players

async def fetch_lp_stats(wllp):
    ranked_stats = await summoner_handler.get_ranked_stats(wllp)

    app.update_ranked_stats(ranked_stats)
    return ranked_stats["leaguePoints"]

async def gameflow_listener(data):
    global RIOT_API_KEY, summoner_name, wllp, platform_id
    rawData = data["data"]
    Phase = rawData["phase"]

    if Phase is not None:
        app.update_current_phase(Phase)
        match Phase:
            case "GameStart":
                print("GameStart was triggered")
                if "teamOne" in rawData["gameData"]:
                    team_one = [{"summonerName": player["summonerName"], "selectedPosition": player["selectedPosition"]} for player in rawData["gameData"]["teamOne"]]
                    team_two = [{"summonerName": player["summonerName"], "selectedPosition": player["selectedPosition"]} for player in rawData["gameData"]["teamTwo"]]
                    print(team_one)
                    print(team_two)
                    if rawData["gameData"]["queue"]["isRanked"] == True:
                        team_one = sort_players_by_role(team_one)
                        team_two = sort_players_by_role(team_two)
                    print("players assigned")
                    if RIOT_API_KEY is not None:
                        player_snooper = await summoner_handler.get_current_match_participants(summoner_name, platform_id, RIOT_API_KEY)

                    app.update_teams(team_one, team_two, player_snooper)
                else:
                    print("no teamOne found in raw data")

            case "EndOfGame":
                global lol_lp_gain_session, lol_lp_initial
                lol_lp_gain_session = (await fetch_lp_stats(wllp)) - lol_lp_initial
                app.clear_teams()
                app.update_lp_gain(lol_lp_gain_session)
    else:
        app.update_current_phase("")

async def main():
    global summoner_name, wllp, lol_lp_initial, platform_id
    (rune_icons, rune_info) = await runeloader.load_all_rune_icons()
    app.load_rune_info(rune_icons, rune_info)
    wllp = await Willump.start()

    listener_subscription = await wllp.subscribe('OnJsonApiEvent')

    summoner_data = await summoner_handler.get_summoner_data(wllp)
    summoner_name = summoner_data["displayName"]

    lol_lp_initial = await fetch_lp_stats(wllp)

    listener_subscription.filter_endpoint('/lol-gameflow/v1/session', gameflow_listener)
    platform_id = (await (await wllp.request("GET", "/lol-platform-config/v1/namespaces/LoginDataPacket/platformId")).text()).replace('"', '')

    while True:
        await asyncio.sleep(1)

async def close_wllp():
    global wllp
    print("stopping app")
    await wllp.close()

def on_closing():
    asyncio.run(close_wllp())
    app.destroy()

if __name__ == "__main__":

    app = GameFlowUI(extended_features=(RIOT_API_KEY is not None))
    app.protocol("WM_DELETE_WINDOW", on_closing)

    main_thread = threading.Thread(target=asyncio.run, args=(main(),))
    main_thread.start()

    app.mainloop()
