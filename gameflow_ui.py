# gameflow_ui.py

import tkinter as tk
import asyncio
from tkinter import ttk
from PIL import Image, ImageTk
from io import BytesIO
import runeloader

class GameFlowUI(tk.Tk):

    def __init__(self, extended_features=False):
        super().__init__()

        self.title("Game Flow")
        self.geometry("400x400")
        self.resizable(False, False)

        self.runes_by_player = {}

        self.team_one_label = tk.Label(self, text="Team One", font=("Arial", 14))
        self.team_one_label.grid(row=0, column=0, padx=(10, 0))

        self.team_two_label = tk.Label(self, text="Team Two", font=("Arial", 14))
        self.team_two_label.grid(row=0, column=1, padx=(10, 0))

        self.team_one_listbox = tk.Listbox(self, height=5)
        self.team_one_listbox.grid(row=1, column=0, padx=(10, 0), pady=(10, 0))

        self.team_two_listbox = tk.Listbox(self, height=5)
        self.team_two_listbox.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))

        self.ranked_stats_label = tk.Label(self, font=("Arial", 12))
        self.ranked_stats_label.grid(row=2, column=0, columnspan=2)

        self.ranked_stats_wins_losses_label = tk.Label(self, font=("Arial", 12))
        self.ranked_stats_wins_losses_label.grid(row=3, column=0, columnspan=2)

        self.current_phase_label = tk.Label(self, font=("Arial", 12))
        self.current_phase_label.grid(row=4, column=0, columnspan=2)

        self.session_lp_gain = tk.Label(self, font=("Arial", 12))
        self.session_lp_gain.grid(row=5, column=0, columnspan=2)


        if extended_features:

            self.primary_runes_frame = tk.Frame(self)
            self.primary_runes_frame.grid(row=6, column=0)
            self.secondary_runes_frame = tk.Frame(self)
            self.secondary_runes_frame.grid(row=6, column=1)
            self.team_one_listbox.bind("<<ListboxSelect>>", self.on_player_selected)
            self.team_two_listbox.bind("<<ListboxSelect>>", self.on_player_selected)

    def load_rune_info(self, rune_icons, rune_info):
        self.rune_info = rune_info
        self.all_rune_icons = rune_icons

    def update_teams(self, team_one, team_two, player_snooper):
        self.team_one_listbox.delete(0, tk.END)
        self.team_two_listbox.delete(0, tk.END)

        for player in team_one:
            self.team_one_listbox.insert(tk.END, player["summonerName"])

        for player in team_two:
            self.team_two_listbox.insert(tk.END, player["summonerName"])

        for player in player_snooper:
            self.runes_by_player[player["summonerName"]] = player["perks"]

    def clear_teams(self):
        self.team_one_listbox.delete(0, tk.END)
        self.team_two_listbox.delete(0, tk.END)

    def on_player_selected(self, event):
        listbox = event.widget
        selected_index = listbox.curselection()

        if not selected_index:
            return

        player_name = listbox.get(selected_index)
        player_perks = self.runes_by_player.get(player_name)

        if player_perks is not None:
            self.assignRunes(player_perks)

    def update_ranked_stats(self, ranked_stats):
        self.ranked_stats_label.config(text=f"{ranked_stats['tier']} {ranked_stats['division']} {ranked_stats['leaguePoints']}LP")
        self.ranked_stats_wins_losses_label.config(text=f"Wins: {ranked_stats['wins']} Losses: {ranked_stats['losses']}")

    def update_current_phase(self, phase):
        self.current_phase_label.config(text=f"{phase}")

    def update_lp_gain(self, lp):
        self.session_lp_gain.config(text=f"LP this session: {lp}")

    def assignRunes(self, perks):
        primary_keystone = None
        secondary_keystone = None

        for keystone in self.rune_info:
            if keystone["id"] == perks["perkStyle"]:
                primary_keystone = keystone
            if keystone["id"] == perks["perkSubStyle"]:
                secondary_keystone = keystone

        for keystone, frame in zip([primary_keystone, secondary_keystone], [self.primary_runes_frame, self.secondary_runes_frame]):
            canvas = tk.Canvas(frame, width=36 * 4, height=36 * 4)
            canvas.grid(row=0, column=0)

            # Create a list to store the images
            canvas.images = []
            for row in range(4):
                columns = 4 if (keystone["id"] in [8100,8000] and row == 0) or (keystone["id"] == 8100 and row == 3) else 3
                for column in range(columns):
                    rune = keystone["slots"][row]["runes"][column]
                    rune_image = Image.open(BytesIO(self.all_rune_icons[rune["icon"]]))

                    if rune["id"] not in perks["perkIds"]:
                        alpha = rune_image.split()[-1]
                        rune_image = rune_image.convert('L').convert("RGB")
                        rune_image.putalpha(alpha)

                    pixels = 24 if (rune["id"] in [8112, 8124, 8128, 9923, 8135, 8134, 8105, 8106, 8005, 8008, 8021, 8010]) else 32

                    rune_image = ImageTk.PhotoImage(rune_image.resize((pixels, pixels), Image.ANTIALIAS))

                    x_offset = (36 - pixels) // 2
                    y_offset = (36 - pixels) // 2

                    # Calculate the additional x offset for centered rows
                    if pixels == 32:
                        row_x_offset = 16
                    else:
                        row_x_offset = 0

                    x_pos = x_offset + (36 * column) + row_x_offset
                    y_pos = y_offset + (36 * row)

                    # Append the rune image to the list before drawing it on the canvas
                    canvas.images.append(rune_image)
                    canvas.create_image(x_pos, y_pos, image=rune_image, anchor='nw')

# 5001 Scaling Health (15-90 HP, lvls 1-18)
# 5002 Armor (5 Armor)
# 5003 Magic Resist (6 MR)
# 5005 Attack Speed (9% Attack Speed)
# 5007 Scaling Cooldown Reduction (1-10% CDR, lvls 1-18)
# 5008 Adaptive Force (6 AD or 10 AP)