from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Champion:
    id: Optional[int] = None
    champion_key: str = ""
    name_en: str = ""
    name_kr: str = ""
    image_url: str = ""
    created_at: Optional[datetime] = None

@dataclass
class Player:
    id: Optional[int] = None
    discord_id: str = ""
    discord_name: str = ""
    summoner_name: str = ""
    wins: int = 0
    losses: int = 0
    rating: int = 1000
    created_at: Optional[datetime] = None

@dataclass
class Game:
    id: Optional[int] = None
    session_id: str = ""
    blue_team: str = ""
    red_team: str = ""
    winner_team: str = ""
    game_duration: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class BanPick:
    id: Optional[int] = None
    game_id: int = 0
    champion_key: str = ""
    team: str = ""  # blue, red
    action: str = ""  # ban, pick
    position: str = ""  # TOP, JUG, MID, ADC, SUP
    order_num: int = 0
    created_at: Optional[datetime] = None
