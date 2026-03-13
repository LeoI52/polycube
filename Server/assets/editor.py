"""
@author : Léo Imbert
@created : 28/09/2025
@updated : 16/01/2026
"""

#? ---------- IMPORTATIONS ---------- ?#

import pyxel
import json
import os

#? ---------- CONSTANTS ---------- ?#

DEFAULT_PYXEL_COLORS = [0x000000, 0x2B335F, 0x7E2072, 0x19959C, 0x8B4852, 0x395C98, 0xA9C1FF, 0xEEEEEE, 0xD4186C, 0xD38441, 0xE9C35B, 0x70C6A9, 0x7696DE, 0xA3A3A3, 0xFF9798, 0xEDC7B0]

MOUSE_ICON = [[0,2],[2,1,2],[2,1,1,2],[2,1,1,1,2],[2,1,1,1,1,2],[2,1,1,2,2],[0,2,2,1,2]]

EMPTY_ICON = [
    [1]*16,
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1]*16]

HOME_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1],[1,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
SPRITE_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,0,1,1,1,1,1,1,0,1,1,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
TILEMAP_ICON = [[1]*16,[1]+[0]*14+[1],[1]+[0]*14+[1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1],[1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1],[1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1]+[0]*14+[1],[1]+[0]*14+[1],[1]*16]
PYXRES_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1],[1,0,0,0,1,1,0,1,1,0,1,1,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,0,1,1,0,1,1,0,1,1,0,0,0,1],[1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
AUTOTILE_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1],[1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
ANIMATION_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,1,1,0,0,0,1,1,0,0,0,0,1],[1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,1],[1,0,0,1,0,0,1,0,1,0,0,1,0,0,0,1],[1,0,0,0,1,1,0,0,0,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,0,1,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
RANDOM_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
PALETTE_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,0,0,1,1,0,0,1],[1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,0,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
SOUND_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,1,1,1,1,0,1,0,0,1],[1,0,0,0,0,0,1,1,1,1,1,0,0,1,0,1],[1,0,0,1,1,1,1,1,1,1,1,0,0,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,0,0,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,0,0,1,0,1],[1,0,0,1,1,1,1,1,1,1,1,0,0,1,0,1],[1,0,0,0,0,0,1,1,1,1,1,0,0,1,0,1],[1,0,0,0,0,0,0,1,1,1,1,0,1,0,0,1],[1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
MUSIC_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,1,1,1,1,1,1,1,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,1,1,1,0,1],[1,0,0,0,0,1,1,1,1,1,1,1,1,1,0,1],[1,0,0,0,0,1,1,1,0,0,0,1,1,1,0,1],[1,0,0,0,1,1,1,1,0,0,1,1,1,1,0,1],[1,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1],[1,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1],[1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,1],[1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]

SPRITE_EDITOR = 0
TILEMAP_EDITOR = 1
AUTOTILE_EDITOR = 2
ANIMATION_EDITOR = 3
SOUND_EDITOR = 4
MUSIC_EDITOR = 5

SELECT_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,1,1,0,1,1,0,0,1,1,0,1,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,1,0,1,1,0,0,1,1,0,1,1,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
PEN_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1],[1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1],[1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1],[1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1],[1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1],[1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],[1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,1],[1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1],[1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1],[1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1],[1,0,1,1,0,0,1,0,0,0,0,0,0,0,0,1],[1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
MIRROR_ICON = [[1]*16,[1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1],[1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1],[1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1],[1,0,1,1,0,0,0,0,0,0,0,0,1,1,0,1],[1,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1],[1,0,1,0,1,0,0,0,0,0,0,1,0,1,0,1],[1,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,1,1,0,0,0,0,1,0,1],[1,0,1,1,0,0,0,0,0,0,0,0,1,1,0,1],[1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1],[1,0,0,0,1,1,0,0,0,0,1,1,0,0,0,1],[1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1],[1]*16]
LINE_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,1,1,1,0,0,1],[1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1],[1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,1,1,1,0,0,0,0,0,1],[1,0,0,0,0,0,1,1,1,0,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,0,0,0,0,0,0,0,1],[1,0,0,0,1,1,1,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
FILLED_RECT_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0]+[1]*10+[0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
RECT_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,1]+[1]*6+[1,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,0]+[0]*6+[0,1,0,0,1],[1,0,0,1,1]+[1]*6+[1,1,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
FILLED_ELLI_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1],[1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1],[1,0,0,0,1,1,1,1,1,1,1,1,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
ELLI_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1],[1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1],[1,0,0,1,0,0,0,0,0,0,0,0,1,0,0,1],[1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
BUCKET_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1],[1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1],[1,0,0,1,0,0,1,0,0,0,0,0,0,0,0,1],[1,0,0,1,0,1,1,1,0,0,0,0,0,0,0,1],[1,0,0,1,1,0,1,0,1,1,0,0,0,0,0,1],[1,0,0,1,0,0,1,0,0,1,1,1,0,0,0,1],[1,0,1,1,0,0,1,0,0,0,1,1,1,0,0,1],[1,0,1,1,1,0,0,0,0,0,0,1,1,0,0,1],[1,0,0,1,1,1,0,0,0,0,1,1,1,0,0,1],[1,0,0,0,1,1,1,1,1,1,0,1,1,0,0,1],[1,0,0,0,0,1,1,1,1,0,0,1,0,0,0,1],[1,0,0,0,0,0,1,1,0,0,0,1,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]
SWAP_ICON = [[1]*16,[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,1,1,1,1,1,0,0,0,0,1],[1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1],[1,0,0,0,1,0,0,0,0,0,1,1,1,0,0,1],[1,0,1,0,1,0,1,0,0,1,1,1,1,1,0,1],[1,0,1,1,1,1,1,0,0,1,0,1,0,1,0,1],[1,0,0,1,1,1,0,0,0,0,0,1,0,0,0,1],[1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],[1,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],[1]*16]

SELECT_TOOL = 0
PEN_TOOL = 1
MIRROR_TOOL = 2
LINE_TOOL = 3
FILLED_RECT_TOOL = 4
RECT_TOOL = 5
FILLED_ELLI_TOOL = 6
ELLI_TOOL = 7
BUCKET_TOOL = 8
SWAP_TOOL = 9

TOOLS_SHORTCUTS = {
    pyxel.KEY_S:SELECT_TOOL,
    pyxel.KEY_P:PEN_TOOL,
    pyxel.KEY_M:MIRROR_TOOL,
    pyxel.KEY_L:LINE_TOOL,
    pyxel.KEY_R:FILLED_RECT_TOOL,
    pyxel.KEY_E:FILLED_ELLI_TOOL,
    pyxel.KEY_B:BUCKET_TOOL,
    pyxel.KEY_O:SWAP_TOOL,
}

#? ---------- SPRITE CONSTANTS ---------- ?#

EDITOR_X, EDITOR_Y, EDITOR_SIZE = 25, 16, 128
COLOR_PICKER_X, COLOR_PICKER_Y = EDITOR_X + EDITOR_SIZE + 16, EDITOR_Y + EDITOR_SIZE - 40
ZOOMS = [8, 16, 32, 64, 128]

#? ---------- TILEMAP CONSTANTS ---------- ?#

TILEMAP_TILE_SIZE = 8
TILES_PICKER_X, TILES_PICKER_Y, TILES_PICKER_SIZE = EDITOR_X + EDITOR_SIZE + 16, EDITOR_Y + EDITOR_SIZE - 64, 64

#? ---------- ANIMATION CONSTANTS ---------- ?#

PREVIOUS_ICON = [[2,2,2,2,2,2,2,2],[2,0,0,0,2,0,0,2],[2,0,0,2,0,0,0,2],[2,0,2,0,0,2,0,2],[2,0,2,0,0,2,0,2],[2,0,0,2,0,0,0,2],[2,0,0,0,2,0,0,2],[2,2,2,2,2,2,2,2]]
PLAY_ICON = [[2,2,2,2,2,2,2,2],[2,0,0,0,0,0,0,2],[2,0,2,0,0,2,0,2],[2,0,2,0,0,2,0,2],[2,0,2,0,0,2,0,2],[2,0,2,0,0,2,0,2],[2,0,0,0,0,0,0,2],[2,2,2,2,2,2,2,2]]
NEXT_ICON = [[2,2,2,2,2,2,2,2],[2,0,0,2,0,0,0,2],[2,0,0,0,2,0,0,2],[2,0,2,0,0,2,0,2],[2,0,2,0,0,2,0,2],[2,0,0,0,2,0,0,2],[2,0,0,2,0,0,0,2],[2,2,2,2,2,2,2,2]]

#? ---------- SOUND CONSTANTS ---------- ?#

SOUND_EDITOR_X, SOUND_EDITOR_Y, SOUND_EDITOR_W, SOUND_EDITOR_H = 25, 16, 128, 120
RESET_ICON = [[2,2,2,2,2,2,2,2],[2,0,0,2,0,0,0,2],[2,0,2,2,2,2,0,2],[2,0,0,2,0,0,2,2],[2,0,0,0,0,0,2,2],[2,0,2,0,0,2,0,2],[2,0,0,2,2,0,0,2],[2,2,2,2,2,2,2,2]]
SOUND_DICT = {
    0: 'b4', 1: 'b-4', 2: 'a4', 3: 'a-4', 4: 'g4', 5: 'g-4', 6: 'f4', 7: 'e4', 8: 'e-4', 9: 'd4', 10: 'd-4', 11: 'c4',
    12: 'b3', 13: 'b-3', 14: 'a3', 15: 'a-3', 16: 'g3', 17: 'g-3', 18: 'f3', 19: 'e3', 20: 'e-3', 21: 'd3', 22: 'd-3', 23: 'c3',
    24: 'b2', 25: 'b-2', 26: 'a2', 27: 'a-2', 28: 'g2', 29: 'g-2', 30: 'f2', 31: 'e2', 32: 'e-2', 33: 'd2', 34: 'd-2', 35: 'c2',
    36: 'b1', 37: 'b-1', 38: 'a1', 39: 'a-1', 40: 'g1', 41: 'g-1', 42: 'f1', 43: 'e1', 44: 'e-1', 45: 'd1', 46: 'd-1', 47: 'c1',
    48: 'b0', 49: 'b-0', 50: 'a0', 51: 'a-0', 52: 'g0', 53: 'g-0', 54: 'f0', 55: 'e0', 56: 'e-0', 57: 'd0', 58: 'd-0', 59: 'c0',
    None:'r',
}


#? ---------- UTILITY CLASSES ---------- ?#

class ColorButton:
    
    def __init__(self, x:int, y:int, color_id:int, colors_len:int):
        self.x, self.y = x, y
        self.w, self.h = 8, 8
        self.color_id = color_id
        self.colors_len = colors_len
        self.selected = False

    def update(self, current_color:int):
        if self.x <= pyxel.mouse_x < self.x + self.w and self.y <= pyxel.mouse_y < self.y + self.h and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return self.color_id
        self.selected = current_color == self.color_id
        return None
    
    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, self.color_id)
        if self.selected:
            pyxel.rectb(self.x, self.y, self.w, self.h, self.colors_len + 1)

class IconButton:

    def __init__(self, x:int, y:int, id:int, icon:list, colors_len:int):
        self.x, self.y = x, y
        self.w, self.h = len(icon[0]), len(icon)
        self.id = id
        self.icon = icon
        self.colors_len = colors_len
        self.selected = False

    def update(self, current_id:int=0):
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, self.x, self.y, self.w, self.h) and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return self.id
        
        self.selected = current_id == self.id
        return None

    def draw(self):
        for y in range(len(self.icon)):
            for x in range(len(self.icon[y])):
                c = self.icon[y][x]
                if c:
                    c = self.colors_len + 1 if self.selected else self.colors_len + 2
                    pyxel.rect(self.x + x, self.y + y, 1, 1, c)

class Selector:

    def __init__(self, x:int, y:int, label:str, values:list, colors_len:int, start_index:int=0):
        self.x, self.y = x, y
        self.label = label
        self.values = values
        self.colors_len = colors_len
        self.__index = start_index

        self.btn_w = 8
        self.btn_h = 8

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, new_index:int):
        if new_index >= 0 and new_index < len(self.values):
            self.__index = new_index

    @property
    def value(self):
        return self.values[self.__index]
    
    @value.setter
    def value(self, new_value:int):
        self.__index = self.values.index(new_value)

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        label_w = len(self.label) * 4
        value_str = str(self.value)
        value_w = len(value_str) * 4
        minus_x = self.x + label_w
        plus_x = minus_x + self.btn_w + value_w + 4

        if (minus_x <= mx < minus_x + self.btn_w and self.y <= my < self.y + self.btn_h and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
            if pyxel.btn(pyxel.KEY_LSHIFT):
                self.__index = max(0, self.__index - 10)
            else:
                self.__index = max(0, self.__index - 1)
            return True

        if (plus_x <= mx < plus_x + self.btn_w and self.y <= my < self.y + self.btn_h and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
            if pyxel.btn(pyxel.KEY_LSHIFT):
                self.__index = min(len(self.values) - 1, self.__index + 10)
            else:
                self.__index = min(len(self.values) - 1, self.__index + 1)
            return True
            
        return False

    def draw(self):
        label_w = len(self.label) * 4
        value_str = str(self.value)
        value_w = len(value_str) * 4

        minus_x = self.x + label_w
        value_x = minus_x + self.btn_w + 2
        plus_x = value_x + value_w + 2

        pyxel.text(self.x, self.y + 2, self.label, self.colors_len + 1)

        pyxel.rect(minus_x, self.y, self.btn_w, self.btn_h, self.colors_len + 2)
        pyxel.text(minus_x + 2, self.y + 2, "-", self.colors_len + 1)

        pyxel.text(value_x, self.y + 2, value_str, self.colors_len + 1)

        pyxel.rect(plus_x, self.y, self.btn_w, self.btn_h, self.colors_len + 2)
        pyxel.text(plus_x + 2, self.y + 2, "+", self.colors_len + 1)

class Button:

    def __init__(self, x:int, y:int, id:int, colors_len:int):
        self.x, self.y = x, y
        self.w, self.h = 8, 8
        self.id = id
        self.colors_len = colors_len
        self.selected = False

    def update(self):
        if self.x <= pyxel.mouse_x < self.x + self.w and self.y <= pyxel.mouse_y < self.y + self.h and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.selected = not self.selected
    
    def draw(self):
        x = 0 if not self.selected else 2
        pyxel.rect(self.x, self.y, self.w, self.h, self.colors_len + x)
        pyxel.text(self.x + 1, self.y + 2, str(self.id), self.colors_len + 1)

class Entry:

    def __init__(self, x:int, y:int, label:str, colors_len:int, max_length:int=10, default_value:str=""):
        self.x, self.y = x, y
        self.label = label
        self.colors_len = colors_len
        self.max_length = max_length
        self.text = default_value
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        self.entry_w = max_length * 4 + 4
        self.entry_h = 8

    @property
    def value(self):
        return self.text
    
    @value.setter
    def value(self, new_value:str):
        self.text = new_value[:self.max_length]

    def update(self):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        label_w = len(self.label) * 4
        entry_x = self.x + label_w
        
        if (entry_x <= mx < entry_x + self.entry_w and 
            self.y <= my < self.y + self.entry_h and 
            pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
            self.active = True
        elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_RETURN):
            self.active = False
        
        if self.active:
            if pyxel.btnp(pyxel.KEY_BACKSPACE) and len(self.text) > 0:
                self.text = self.text[:-1]
            
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key):
                    char = chr(ord('a') + (key - pyxel.KEY_A))
                    if pyxel.btn(pyxel.KEY_SHIFT):
                        char = char.upper()
                    if len(self.text) < self.max_length:
                        self.text += char
            
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key):
                    if len(self.text) < self.max_length:
                        self.text += chr(ord('0') + (key - pyxel.KEY_0))
            
            if pyxel.btnp(pyxel.KEY_COLON) and len(self.text) < self.max_length:
                self.text += "/"

            if pyxel.btnp(pyxel.KEY_COMMA) and len(self.text) < self.max_length:
                self.text += ","
            
            if pyxel.btnp(pyxel.KEY_SPACE) and len(self.text) < self.max_length:
                self.text += " "
        
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self):
        label_w = len(self.label) * 4
        entry_x = self.x + label_w
        
        pyxel.text(self.x, self.y + 2, self.label, self.colors_len + 1)
        
        box_color = self.colors_len + 2 if not self.active else self.colors_len + 1
        pyxel.rect(entry_x, self.y, self.entry_w, self.entry_h, self.colors_len)
        pyxel.rectb(entry_x, self.y, self.entry_w, self.entry_h, box_color)
        
        if self.text:
            pyxel.text(entry_x + 2, self.y + 2, self.text, self.colors_len + 1)
        
        if self.active and self.cursor_visible:
            cursor_x = entry_x + 2 + len(self.text) * 4
            pyxel.line(cursor_x, self.y + 1, cursor_x, self.y + 6, self.colors_len + 1)

#? ---------- UTILITY FUNCTIONS ---------- ?#

def collision_point_rect(x1:int, y1:int, x2:int, y2:int, w2:int, h2:int)-> bool:
    return x2 <= x1 < x2 + w2 and y2 <= y1 < y2 + h2

#? ---------- CLASSES ---------- ?#

class SoundEffect:

    def __init__(self):
        self.notes = [None for _ in range(SOUND_EDITOR_W // 2)]
        self.tone = "T"
        self.volume = "7"
        self.effect = "N"
        self.speed = 1

    def save(self, sound:int):
        trimmed_notes = list(self.notes)
        while trimmed_notes and trimmed_notes[-1] is None:
            trimmed_notes.pop()

        pyxel.sounds[sound].set_notes("".join([SOUND_DICT[note] for note in trimmed_notes]))
        pyxel.sounds[sound].set_tones(self.tone)
        pyxel.sounds[sound].set_volumes(self.volume)
        pyxel.sounds[sound].set_effects(self.effect)
        pyxel.sounds[sound].speed = self.speed

    def load(self, sound:int):
        self.tone = {0:"T", 1:"S", 2:"P", 3:"N"}.get(pyxel.sounds[sound].tones[0])
        self.volume = str(pyxel.sounds[sound].volumes[0])
        self.effect = {0:"N", 1:"S", 2:"V", 3:"F", 4:"H", 5:"Q"}.get(pyxel.sounds[sound].effects[0])
        self.speed = pyxel.sounds[sound].speed
        self.notes = [None if x == -1 else 59 - x for x in pyxel.sounds[sound].notes]
        if len(self.notes) < SOUND_EDITOR_W // 2:
            self.notes += [None for _ in range(SOUND_EDITOR_W // 2 - len(self.notes))]

#? ---------- EDITOR ---------- ?#

class Editor:

    def __init__(self, color_palette:list, filename:str="assets.pyxres", fullscreen:bool=True):
        #? Pyxel Init
        pyxel.init(258, 160, title="Editor", fps=60, quit_key=pyxel.KEY_NONE)
        pyxel.fullscreen(fullscreen)
        pyxel.colors.from_list(color_palette + [0x2B335F, 0xEEEEEE, 0x4A90E2])

        #? Pyxres Config
        self.load(filename)

        #? CONSTANTS
        self.COLORS_LEN = len(color_palette)

        #? Main Variables
        self.current_tab = SPRITE_EDITOR
        self.current_tool = SELECT_TOOL
        self.tab_buttons = [IconButton(0, 16, SPRITE_EDITOR, SPRITE_ICON, self.COLORS_LEN),
                          IconButton(0, 32, TILEMAP_EDITOR, TILEMAP_ICON, self.COLORS_LEN),
                          IconButton(0, 48, AUTOTILE_EDITOR, AUTOTILE_ICON, self.COLORS_LEN),
                          IconButton(0, 64, ANIMATION_EDITOR, ANIMATION_ICON, self.COLORS_LEN),
                          IconButton(0, 80, SOUND_EDITOR, SOUND_ICON, self.COLORS_LEN),
                          IconButton(0, 96, MUSIC_EDITOR, MUSIC_ICON, self.COLORS_LEN)]
        self.tool_buttons = [IconButton(169, 16, SELECT_TOOL, SELECT_ICON, self.COLORS_LEN),
                             IconButton(185, 16, PEN_TOOL, PEN_ICON, self.COLORS_LEN),
                             IconButton(201, 16, MIRROR_TOOL, MIRROR_ICON, self.COLORS_LEN),
                             IconButton(217, 16, LINE_TOOL, LINE_ICON, self.COLORS_LEN),
                             IconButton(169, 32, FILLED_RECT_TOOL, FILLED_RECT_ICON, self.COLORS_LEN),
                             IconButton(185, 32, RECT_TOOL, RECT_ICON, self.COLORS_LEN),
                             IconButton(201, 32, FILLED_ELLI_TOOL, FILLED_ELLI_ICON, self.COLORS_LEN),
                             IconButton(217, 32, ELLI_TOOL, ELLI_ICON, self.COLORS_LEN),
                             IconButton(169, 48, BUCKET_TOOL, BUCKET_ICON, self.COLORS_LEN),
                             IconButton(185, 48, SWAP_TOOL, SWAP_ICON, self.COLORS_LEN)]
        
        #? Sprite Variables
        self.s_color = 0
        self.s_grid = False
        self.s_history = []
        self.s_selection = None
        self.s_clipboard = None
        self.s_drag_start = None
        self.s_tile_size = EDITOR_SIZE // 16
        self.s_offset_x = self.s_offset_y = 0
        self.s_color_buttons = self.place_s_color_buttons()
        self.s_zoom_selector = Selector(101, 148, "Zoom:", ZOOMS[::-1], self.COLORS_LEN, 3)
        self.s_grid_selector = Selector(89, 4, "Grid size:", [1, 2, 4, 8, 16], self.COLORS_LEN, 3)
        self.s_image_selector = Selector(25, 148, "Image:", [x for x in range(self.NUMBER_IMAGES)], self.COLORS_LEN)

        #? Tilemap Variables
        self.t_grid = False
        self.t_history = []
        self.t_clipboard = None
        self.t_selection = None
        self.t_drag_start = None
        self.t_tile_selected = (0, 0)
        self.t_tile_offset_x = self.t_tile_offset_y = 0
        self.t_tilemap_offset_x = self.t_tilemap_offset_y = 0
        self.t_grid_selector = Selector(89, 4, "Grid size:", [1, 2, 4, 8], self.COLORS_LEN, 3)
        self.t_tilemap_selector = Selector(25, 148, "Tilemap:", [x for x in range(self.NUMBER_TILEMAPS)], self.COLORS_LEN)
        self.t_layer_selector = Selector(93, 148, "Layer:", ["None"] + [x for x in range(self.NUMBER_TILEMAPS)], self.COLORS_LEN)
        self.t_image_selector = Selector(169, 148, "Image:", [x for x in range(self.NUMBER_IMAGES)], self.COLORS_LEN, pyxel.tilemaps[0].imgsrc)

        #? Autotile Editor Variables
        self.a_tiles_y = {x:[] for x in range(self.NUMBER_IMAGES)}
        self.a_buttons = {x:self.place_a_buttons() for x in range(self.NUMBER_IMAGES)}
        self.a_image_selector = Selector(20, 2, "Image:", [x for x in range(self.NUMBER_IMAGES)], self.COLORS_LEN)

        #? Animation Editor Variables
        self.n_frame = 0
        self.n_frame_timer = 0
        self.n_is_playing = False
        self.n_animation = [None for _ in range(7)]
        self.n_colkey_entry = Entry(160, 64, "Colkey:", self.COLORS_LEN, 2, "0")
        self.n_start_uv_entry = Entry(160, 32, "Start (u,v):", self.COLORS_LEN, 7)
        self.n_sprite_wh_entry = Entry(160, 48, "Sprite (w,h):", self.COLORS_LEN, 5)
        self.n_frames_entry = Entry(160, 80, "Total frames:", self.COLORS_LEN, 2, "1")
        self.n_speed_entry = Entry(160, 96, "Frame duration:", self.COLORS_LEN, 4, "10")
        self.n_play_button = IconButton(126, EDITOR_Y + EDITOR_SIZE + 2, 1, PLAY_ICON, self.COLORS_LEN)
        self.n_next_button = IconButton(136, EDITOR_Y + EDITOR_SIZE + 2, 2, NEXT_ICON, self.COLORS_LEN)
        self.n_prev_button = IconButton(116, EDITOR_Y + EDITOR_SIZE + 2, 0, PREVIOUS_ICON, self.COLORS_LEN)
        self.n_image_selector = Selector(160, 16, "Image:", [x for x in range(self.NUMBER_IMAGES)], self.COLORS_LEN)

        #? Sound Editor Variables
        self.so_sounds = [SoundEffect() for _ in range(100)]
        self.so_play_button = IconButton(125, 4, 1, PLAY_ICON, self.COLORS_LEN)
        self.so_reset_button = IconButton(135, 4, 1, RESET_ICON, self.COLORS_LEN)
        self.so_tone_selector = Selector(157, 26, "Tone:", ["T", "S", "P", "N"], self.COLORS_LEN)
        self.so_sound_selector = Selector(27, 4, "Sound:", [x for x in range(100)], self.COLORS_LEN)
        self.so_speed_selector = Selector(157, 16, "Speed:", [x for x in range(1, 31)], self.COLORS_LEN)
        self.so_volume_selector = Selector(157, 46, "Volume:", [str(x) for x in range(8)], self.COLORS_LEN, 7)
        self.so_effect_selector = Selector(157, 36, "Effect:", ["N", "S", "V", "F", "H", "Q"], self.COLORS_LEN)

        #? Load Sound Editor
        for i in range(100):
            self.so_sounds[i].load(i)
        self.so_speed_selector.value = self.so_sounds[0].speed
        self.so_tone_selector.value = self.so_sounds[0].tone
        self.so_effect_selector.value = self.so_sounds[0].effect
        self.so_volume_selector.value = self.so_sounds[0].volume

        #? Music Editor Variables
        self.m_import_entry = Entry(27, 32, "Import:", self.COLORS_LEN, 20)
        self.m_play_button = IconButton(125, 4, 1, PLAY_ICON, self.COLORS_LEN)
        self.m_reset_button = IconButton(135, 4, 1, RESET_ICON, self.COLORS_LEN)
        self.m_import_button = IconButton(148, 32, 1, NEXT_ICON, self.COLORS_LEN)
        self.m_music_selector = Selector(27, 4, "Music:", [x for x in range((self.NUMBER_SOUNDS - 100) // 4)], self.COLORS_LEN)
        
        #? Pyxel Run
        pyxel.run(self.update, self.draw)

    #? ---------- PYXRES ---------- ?#

    def load(self, pyxres_path):
        if os.path.isfile(pyxres_path):
            pyxel.load(pyxres_path)
            sound_list  = pyxel.sounds.to_list()
            if len(sound_list) < 100:
                pyxel.sounds.from_list(sound_list + [pyxel.Sound() for _ in range(100 - len(sound_list))])
                for i in range(len(sound_list), 100):
                    pyxel.sounds[i].set_tones("T")
                    pyxel.sounds[i].set_volumes("7")
                    pyxel.sounds[i].set_effects("N")
                    pyxel.sounds[i].speed = 1
        else:
            pyxel.images.from_list([pyxel.Image(256, 256) for _ in range(2)])
            pyxel.tilemaps.from_list([pyxel.Tilemap(256, 256, 0) for _ in range(5)])
            pyxel.sounds.from_list([pyxel.Sound() for _ in range(140)])
            for i in range(100):
                pyxel.sounds[i].set_tones("T")
                pyxel.sounds[i].set_volumes("7")
                pyxel.sounds[i].set_effects("N")
                pyxel.sounds[i].speed = 1

        self.PYXRES_PATH = pyxres_path
        self.NUMBER_IMAGES = len(pyxel.images.to_list())
        self.NUMBER_TILEMAPS = len(pyxel.tilemaps.to_list())
        self.NUMBER_SOUNDS = len(pyxel.sounds.to_list())

    def save(self):
        for i, sound in enumerate(self.so_sounds):
            sound.save(i)

        pyxel.save(self.PYXRES_PATH)

    #? ---------- DRAW METHODS ---------- ?#

    def rect(self, min_x:int, min_y:int, max_x:int, max_y:int, filled:bool=True):
        rect = set()
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                if filled or (y in [min_y, max_y] or x in [min_x, max_x]):
                    rect.add((x, y))
        return rect

    def elli(self, min_x:int, min_y:int, max_x:int, max_y:int, filled:bool=True):
        elli = set()
        width = max_x - min_x
        height = max_y - min_y
        if width == 0 or height == 0:
            return self.rect(min_x, min_y, max_x, max_y, not filled)

        rx = width / 2.0
        ry = height / 2.0
        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0

        for yy in range(min_y, max_y + 1):
            for xx in range(min_x, max_x + 1):
                dx = xx - cx
                dy = yy - cy
                val = (dx*dx) / (rx*rx + 1e-9) + (dy*dy) / (ry*ry + 1e-9)
                if filled:
                    if val <= 1.0 + 1e-9:
                        elli.add((xx, yy))
                else:
                    if val <= 1.0 + 1e-9:
                        outside_neighbor = False
                        for nx, ny in ((xx+1,yy),(xx-1,yy),(xx,yy+1),(xx,yy-1)):
                            if nx < min_x or nx > max_x or ny < min_y or ny > max_y:
                                outside_neighbor = True
                                break
                            ndx = nx - cx
                            ndy = ny - cy
                            nval = (ndx*ndx) / (rx*rx + 1e-9) + (ndy*ndy) / (ry*ry + 1e-9)
                            if nval > 1.0 + 1e-9:
                                outside_neighbor = True
                                break
                        if outside_neighbor:
                            elli.add((xx, yy))
        return elli

    def line(self, x0:int, y0:int, x1:int, y1:int):
        line = set()
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            line.add((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

        return line

    #? ---------- SPRITE EDITOR ---------- ?#

    def place_s_color_buttons(self):
        l = []
        c = x = y = 0
        while c < self.COLORS_LEN:
            l.append(ColorButton(COLOR_PICKER_X + x * 8, COLOR_PICKER_Y + y * 8, c, self.COLORS_LEN))
            x = (x + 1) % 8
            if x == 0:
                y += 1
            c += 1
        return l

    def push_sprite_history(self):
        snapshot = [[pyxel.images[self.s_image_selector.value].pget(x, y) for x in range(pyxel.images[self.s_image_selector.value].width)] for y in range(pyxel.images[self.s_image_selector.value].height)]
        self.s_history.append((self.s_image_selector.value, snapshot))
        if len(self.s_history) > 40:
            self.s_history.pop(0)

    def undo_sprite(self):
        if self.s_history:
            image, snapshot = self.s_history.pop()
            for y in range(pyxel.images[self.s_image_selector.value].height):
                for x in range(pyxel.images[self.s_image_selector.value].width):
                    pyxel.images[image].pset(x, y, snapshot[y][x])

    def flood_fill_sprite(self, x:int, y:int, old_color:int, new_color:int):
        if old_color == new_color:
            return set()

        pixels = set()
        x0, y0 = self.s_offset_x, self.s_offset_y
        x1, y1 = self.s_offset_x + self.s_zoom_selector.value, self.s_offset_y + self.s_zoom_selector.value

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (x0 <= cx < x1 and y0 <= cy < y1 and pyxel.images[self.s_image_selector.value].pget(cx, cy) == old_color) and (cx, cy) not in pixels:
                pixels.add((cx, cy))
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
        return pixels

    def swap_fill_sprite(self, old_color:int, new_color:int):
        if old_color == new_color:
            return set()
    
        pixels = set()
        x0, y0 = self.s_offset_x, self.s_offset_y
        x1, y1 = self.s_offset_x + self.s_zoom_selector.value, self.s_offset_y + self.s_zoom_selector.value

        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if pyxel.images[self.s_image_selector.value].pget(x, y) == old_color:
                    pixels.add((x, y))
        return pixels

    def commit_pixels(self, pixels:set):
        x0, y0 = self.s_offset_x, self.s_offset_y
        x1, y1 = self.s_offset_x + self.s_zoom_selector.value - 1, self.s_offset_y + self.s_zoom_selector.value - 1
        for (x, y) in pixels:
            if x0 <= x <= x1 and y0 <= y <= y1:
                pyxel.images[self.s_image_selector.value].pset(x, y, self.s_color)

    def draw_preview_pixels(self, pixels:set):
        for (x, y) in pixels:
            if x < self.s_offset_x or x >= self.s_offset_x + self.s_zoom_selector.value or y < self.s_offset_y or y >= self.s_offset_y + self.s_zoom_selector.value:
                continue
            sx = EDITOR_X + (x - self.s_offset_x) * self.s_tile_size
            sy = EDITOR_Y + (y - self.s_offset_y) * self.s_tile_size
            pyxel.rect(sx, sy, self.s_tile_size, self.s_tile_size, self.s_color)

    def copy_sprite(self):
        if not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        self.s_clipboard = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                abs_x = x + self.s_offset_x
                abs_y = y + self.s_offset_y
                color = pyxel.images[self.s_image_selector.value].pget(abs_x, abs_y)
                self.s_clipboard.append((x - min_x, y - min_y, color))

    def cut_sprite(self):
        if not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        self.copy_sprite()
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                abs_x = x + self.s_offset_x
                abs_y = y + self.s_offset_y
                pyxel.images[self.s_image_selector.value].pset(abs_x, abs_y, 0)

    def paste_sprite(self):
        if not self.s_clipboard or not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        
        for rel_x, rel_y, color in self.s_clipboard:
            abs_x = min_x + rel_x + self.s_offset_x
            abs_y = min_y + rel_y + self.s_offset_y
            
            if 0 <= abs_x < pyxel.images[self.s_image_selector.value].width and 0 <= abs_y < pyxel.images[self.s_image_selector.value].height:
                pyxel.images[self.s_image_selector.value].pset(abs_x, abs_y, color)

    def rotate_sprite_selection(self):
        if not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        if width != height:
            return
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.s_offset_x
                abs_y = y + self.s_offset_y
                row.append(pyxel.images[self.s_image_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)
        
        for y in range(height):
            for x in range(width):
                new_x = min_x + y
                new_y = min_y + (width - 1 - x)
                
                if new_x <= max_x and new_y <= max_y:
                    abs_x = new_x + self.s_offset_x
                    abs_y = new_y + self.s_offset_y
                    if 0 <= abs_x < pyxel.images[self.s_image_selector.value].width and 0 <= abs_y < pyxel.images[self.s_image_selector.value].height:
                        pyxel.images[self.s_image_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def flip_sprite_selection_horizontal(self):
        if not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        width = max_x - min_x + 1
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.s_offset_x
                abs_y = y + self.s_offset_y
                row.append(pyxel.images[self.s_image_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)

        for y in range(max_y - min_y + 1):
            for x in range(width):
                new_x = min_x + (width - 1 - x)
                abs_x = new_x + self.s_offset_x
                abs_y = (min_y + y) + self.s_offset_y
                if 0 <= abs_x < pyxel.images[self.s_image_selector.value].width and 0 <= abs_y < pyxel.images[self.s_image_selector.value].height:
                    pyxel.images[self.s_image_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def flip_sprite_selection_vertical(self):
        if not self.s_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.s_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        height = max_y - min_y + 1
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.s_offset_x
                abs_y = y + self.s_offset_y
                row.append(pyxel.images[self.s_image_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)
        
        for y in range(height):
            for x in range(max_x - min_x + 1):
                new_y = min_y + (height - 1 - y)
                abs_x = (min_x + x) + self.s_offset_x
                abs_y = new_y + self.s_offset_y
                if 0 <= abs_x < pyxel.images[self.s_image_selector.value].width and 0 <= abs_y < pyxel.images[self.s_image_selector.value].height:
                    pyxel.images[self.s_image_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def update_sprite_editor(self):
        #? Grid
        if pyxel.btnp(pyxel.KEY_G): self.s_grid = not self.s_grid

        #? Scroll Wheel
        if pyxel.mouse_wheel < 0:
            self.s_selection = None
            self.s_zoom_selector.index += 1
            self.s_tile_size = EDITOR_SIZE // self.s_zoom_selector.value
        elif pyxel.mouse_wheel > 0:
            self.s_selection = None
            self.s_zoom_selector.index -= 1
            self.s_tile_size = EDITOR_SIZE // self.s_zoom_selector.value

        #? Selection Shortcuts
        if pyxel.btn(pyxel.KEY_CTRL) or pyxel.btn(pyxel.KEY_GUI):
            if pyxel.btnp(pyxel.KEY_R):
                self.push_sprite_history()
                self.rotate_sprite_selection()
            elif pyxel.btnp(pyxel.KEY_H):
                self.push_sprite_history()
                self.flip_sprite_selection_horizontal()
            elif pyxel.btnp(pyxel.KEY_F):
                self.push_sprite_history()
                self.flip_sprite_selection_vertical()
            elif pyxel.btnp(pyxel.KEY_C):
                self.copy_sprite()
            elif pyxel.btnp(pyxel.KEY_X):
                self.push_sprite_history()
                self.cut_sprite()
            elif pyxel.btnp(pyxel.KEY_V):
                self.push_sprite_history()
                self.paste_sprite()
            elif pyxel.btnp(pyxel.KEY_Z):
                self.undo_sprite()

        #? Tools Shortcut
        for key in TOOLS_SHORTCUTS.keys():
            if pyxel.btnp(key) and not (pyxel.btn(pyxel.KEY_CTRL) or pyxel.btn(pyxel.KEY_GUI)):
                self.current_tool = TOOLS_SHORTCUTS[key]

        #? Editor
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, EDITOR_X, EDITOR_Y, EDITOR_SIZE, EDITOR_SIZE):
            mx = (pyxel.mouse_x - EDITOR_X) // self.s_tile_size + self.s_offset_x
            my = (pyxel.mouse_y - EDITOR_Y) // self.s_tile_size + self.s_offset_y

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):

                if self.current_tool in [FILLED_RECT_TOOL, RECT_TOOL, FILLED_ELLI_TOOL, ELLI_TOOL, LINE_TOOL]:
                    self.s_drag_start = (mx, my)
                elif self.current_tool == BUCKET_TOOL:
                    self.push_sprite_history()
                    self.commit_pixels(self.flood_fill_sprite(mx, my, pyxel.images[self.s_image_selector.value].pget(mx, my), self.s_color))
                elif self.current_tool == SWAP_TOOL:
                    self.push_sprite_history()
                    self.commit_pixels(self.swap_fill_sprite(pyxel.images[self.s_image_selector.value].pget(mx, my), self.s_color))
                elif self.current_tool == SELECT_TOOL:
                    x = (pyxel.mouse_x - EDITOR_X) // self.s_tile_size
                    y = (pyxel.mouse_y - EDITOR_Y) // self.s_tile_size
                    self.s_selection = [x, y, x, y]

            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                if self.current_tool == PEN_TOOL:
                    pyxel.images[self.s_image_selector.value].pset(mx, my, self.s_color)
                elif self.current_tool == MIRROR_TOOL:
                    pyxel.images[self.s_image_selector.value].pset(mx, my, self.s_color)
                    axis_x = self.s_offset_x + self.s_zoom_selector.value // 2
                    mx_mirror = axis_x - (mx - axis_x) - 1
                    if 0 <= mx_mirror < pyxel.images[self.s_image_selector.value].width:
                        pyxel.images[self.s_image_selector.value].pset(mx_mirror, my, self.s_color)
                elif self.current_tool == SELECT_TOOL and self.s_selection:
                    x = (pyxel.mouse_x - EDITOR_X) // self.s_tile_size
                    y = (pyxel.mouse_y - EDITOR_Y) // self.s_tile_size
                    self.s_selection[2] = x
                    self.s_selection[3] = y

            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.s_drag_start:
                x0, y0 = self.s_drag_start
                max_x, max_y = max(x0, mx), max(y0, my)
                min_x, min_y = min(x0, mx), min(y0, my)

                self.push_sprite_history()

                if self.current_tool == FILLED_RECT_TOOL:
                    self.commit_pixels(self.rect(min_x, min_y, max_x, max_y))
                elif self.current_tool == RECT_TOOL:
                    self.commit_pixels(self.rect(min_x, min_y, max_x, max_y, False))
                elif self.current_tool == FILLED_ELLI_TOOL:
                    self.commit_pixels(self.elli(min_x, min_y, max_x, max_y))
                elif self.current_tool == ELLI_TOOL:
                    self.commit_pixels(self.elli(min_x, min_y, max_x, max_y, False))
                elif self.current_tool == LINE_TOOL:
                    self.commit_pixels(self.line(x0, y0, mx, my))

                self.s_drag_start = None

            if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                self.s_color = pyxel.images[self.s_image_selector.value].pget(mx, my)

        else:
            self.s_drag_start = None

        #? Movement
        if pyxel.btnp(pyxel.KEY_RIGHT, repeat=5):
            self.s_offset_x += self.s_zoom_selector.value // 2
        if pyxel.btnp(pyxel.KEY_LEFT, repeat=5):
            self.s_offset_x -= self.s_zoom_selector.value // 2
        if pyxel.btnp(pyxel.KEY_DOWN, repeat=5):
            self.s_offset_y += self.s_zoom_selector.value // 2
        if pyxel.btnp(pyxel.KEY_UP, repeat=5):
            self.s_offset_y -= self.s_zoom_selector.value // 2
        self.s_offset_x = max(0, min(pyxel.images[self.s_image_selector.value].width - self.s_zoom_selector.value, self.s_offset_x))
        self.s_offset_y = max(0, min(pyxel.images[self.s_image_selector.value].height - self.s_zoom_selector.value, self.s_offset_y))

        #? Selectors
        self.s_image_selector.update()
        self.s_grid_selector.update()
        z = self.s_zoom_selector.update()

        if z:
            self.s_selection = None
            self.s_tile_size = EDITOR_SIZE // self.s_zoom_selector.value

        #? Color Buttons
        for color_button in self.s_color_buttons:
            c = color_button.update(self.s_color)
            self.s_color = c if c is not None else self.s_color

        #? Tool Buttons
        for tool_button in self.tool_buttons:
            c = tool_button.update(self.current_tool)
            self.current_tool = c if c is not None else self.current_tool

    def draw_sprite_editor(self):
        #? Selectors
        self.s_image_selector.draw()
        self.s_zoom_selector.draw()
        self.s_grid_selector.draw()

        #? Color Buttons
        for color_button in self.s_color_buttons:
            color_button.draw()

        #? Tool Buttons
        for tool_button in self.tool_buttons:
            tool_button.draw()

        #? Color Number
        tx = (pyxel.mouse_x - COLOR_PICKER_X) // 8
        ty = (pyxel.mouse_y - COLOR_PICKER_Y) // 8
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, COLOR_PICKER_X, COLOR_PICKER_Y, 64, 32) and tx + ty * 8 < self.COLORS_LEN:
            pyxel.text(COLOR_PICKER_X, COLOR_PICKER_Y - 8, f"{tx + ty * 8}", self.COLORS_LEN + 1)
        else:
            pyxel.text(COLOR_PICKER_X, COLOR_PICKER_Y - 8, f"{self.s_color}", self.COLORS_LEN + 1)

        #? Editor
        for y in range(self.s_zoom_selector.value):
            for x in range(self.s_zoom_selector.value):
                c = pyxel.images[self.s_image_selector.value].pget(self.s_offset_x + x, self.s_offset_y + y)
                pyxel.rect(EDITOR_X + x * self.s_tile_size, EDITOR_Y + y * self.s_tile_size, self.s_tile_size, self.s_tile_size, c)
            
        #? Draw Preview
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, EDITOR_X, EDITOR_Y, EDITOR_SIZE, EDITOR_SIZE):
            mx = (pyxel.mouse_x - EDITOR_X) // self.s_tile_size + self.s_offset_x
            my = (pyxel.mouse_y - EDITOR_Y) // self.s_tile_size + self.s_offset_y
            pixels = set()

            pyxel.text(EDITOR_X + 1, 8, f"({mx},{my})", self.COLORS_LEN + 1)

            if self.current_tool == BUCKET_TOOL:
                pixels = self.flood_fill_sprite(mx, my, pyxel.images[self.s_image_selector.value].pget(mx, my), self.s_color)
            elif self.current_tool == SWAP_TOOL:
                pixels = self.swap_fill_sprite(pyxel.images[self.s_image_selector.value].pget(mx, my), self.s_color)

            if self.s_drag_start:
                x0, y0 = self.s_drag_start
                min_x, max_x = min(x0, mx), max(x0, mx)
                min_y, max_y = min(y0, my), max(y0, my)

                if self.current_tool == FILLED_RECT_TOOL:
                    pixels = self.rect(min_x, min_y, max_x, max_y)
                elif self.current_tool == RECT_TOOL:
                    pixels = self.rect(min_x, min_y, max_x, max_y, False)
                elif self.current_tool == FILLED_ELLI_TOOL:
                    pixels = self.elli(min_x, min_y, max_x, max_y)
                elif self.current_tool == ELLI_TOOL:
                    pixels = self.elli(min_x, min_y, max_x, max_y, False)
                elif self.current_tool == LINE_TOOL:
                    pixels = self.line(x0, y0, mx, my)

            self.draw_preview_pixels(pixels)

        #? Grid
        if self.s_grid:
            for y in range(EDITOR_Y, EDITOR_Y + EDITOR_SIZE, self.s_grid_selector.value * self.s_tile_size):
                pyxel.rect(EDITOR_X, y, EDITOR_SIZE, 1, self.COLORS_LEN)
            for x in range(EDITOR_X, EDITOR_X + EDITOR_SIZE, self.s_grid_selector.value * self.s_tile_size):
                pyxel.rect(x, EDITOR_Y, 1, EDITOR_SIZE, self.COLORS_LEN)
            pyxel.rect(EDITOR_X, EDITOR_Y + EDITOR_SIZE - 1, EDITOR_SIZE, 1, self.COLORS_LEN)
            pyxel.rect(EDITOR_X + EDITOR_SIZE - 1, EDITOR_Y, 1, EDITOR_SIZE, self.COLORS_LEN)

        #? Selection Preview
        if self.s_selection and self.current_tool == SELECT_TOOL:
            x0, y0, x1, y1 = self.s_selection
            min_x, max_x = min(x0, x1), max(x0, x1)
            min_y, max_y = min(y0, y1), max(y0, y1)

            pyxel.rectb(EDITOR_X + min_x * self.s_tile_size, EDITOR_Y + min_y * self.s_tile_size, (max_x - min_x + 1) * self.s_tile_size, (max_y - min_y + 1) * self.s_tile_size, self.COLORS_LEN + 1)

    #? ---------- TILEMAP EDITOR ---------- ?#

    def push_tilemap_history(self):
        snapshot = [[pyxel.tilemaps[self.t_tilemap_selector.value].pget(x, y) for x in range(pyxel.tilemaps[self.t_tilemap_selector.value].width)] for y in range(pyxel.tilemaps[self.t_tilemap_selector.value].height)]
        self.t_history.append((self.t_tilemap_selector.value, snapshot))
        if len(self.t_history) > 40:
            self.t_history.pop(0)

    def undo_tilemap(self):
        if self.t_history:
            tilemap, snapshot = self.t_history.pop()
            for y in range(pyxel.tilemaps[self.t_tilemap_selector.value].height):
                for x in range(pyxel.tilemaps[self.t_tilemap_selector.value].width):
                    pyxel.tilemaps[tilemap].pset(x, y, snapshot[y][x])

    def flood_fill_tilemap(self, x:int, y:int, old_tile:tuple, new_tile:tuple):
        if old_tile == new_tile:
            return set()

        pixels = set()
        x0, y0 = self.t_tilemap_offset_x, self.t_tilemap_offset_y
        x1, y1 = self.t_tilemap_offset_x + 16, self.t_tilemap_offset_y + 16

        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (x0 <= cx < x1 and y0 <= cy < y1 and pyxel.tilemaps[self.t_tilemap_selector.value].pget(cx, cy) == old_tile) and (cx, cy) not in pixels:
                pixels.add((cx, cy))
                stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
        return pixels

    def swap_fill_tilemap(self, old_tile:tuple, new_tile:tuple):
        if old_tile == new_tile:
            return set()
    
        pixels = set()
        x0, y0 = self.t_tilemap_offset_x, self.t_tilemap_offset_y
        x1, y1 = self.t_tilemap_offset_x + 16, self.t_tilemap_offset_y + 16

        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if pyxel.tilemaps[self.t_tilemap_selector.value].pget(x, y) == old_tile:
                    pixels.add((x, y))
        return pixels

    def commit_tiles(self, tiles:set):
        x0, y0 = self.t_tilemap_offset_x, self.t_tilemap_offset_y
        x1, y1 = self.t_tilemap_offset_x + 16 - 1, self.t_tilemap_offset_y + 16 - 1
        tx, ty = (self.t_tile_selected[0] + self.t_tile_offset_x // 8, self.t_tile_selected[1] + self.t_tile_offset_y // 8)
        for (x, y) in tiles:
            if x0 <= x <= x1 and y0 <= y <= y1:
                pyxel.tilemaps[self.t_tilemap_selector.value].pset(x, y, (tx, ty))

    def draw_preview_tiles(self, tiles:set):
        tx, ty = (self.t_tile_selected[0] + self.t_tile_offset_x // 8, self.t_tile_selected[1] + self.t_tile_offset_y // 8)
        for (x, y) in tiles:
            if x < self.t_tilemap_offset_x or x >= self.t_tilemap_offset_x + 16 or y < self.t_tilemap_offset_y or y >= self.t_tilemap_offset_y + 16:
                continue
            sx = EDITOR_X + (x - self.t_tilemap_offset_x) * TILEMAP_TILE_SIZE
            sy = EDITOR_Y + (y - self.t_tilemap_offset_y) * TILEMAP_TILE_SIZE
            pyxel.blt(sx, sy, self.t_image_selector.value, tx * 8, ty * 8, TILEMAP_TILE_SIZE, TILEMAP_TILE_SIZE)

    def copy_tilemap(self):
        if not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        self.t_clipboard = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                abs_x = x + self.t_tilemap_offset_x
                abs_y = y + self.t_tilemap_offset_y
                tile = pyxel.tilemaps[self.t_tilemap_selector.value].pget(abs_x, abs_y)
                self.t_clipboard.append((x - min_x, y - min_y, tile))

    def cut_tilemap(self):
        if not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        self.copy_tilemap()
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                abs_x = x + self.t_tilemap_offset_x
                abs_y = y + self.t_tilemap_offset_y
                pyxel.tilemaps[self.t_tilemap_selector.value].pset(abs_x, abs_y, (0, 0))

    def paste_tilemap(self):
        if not self.t_clipboard or not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        
        for rel_x, rel_y, tile in self.t_clipboard:
            abs_x = min_x + rel_x + self.t_tilemap_offset_x
            abs_y = min_y + rel_y + self.t_tilemap_offset_y
            
            if 0 <= abs_x < pyxel.tilemaps[self.t_tilemap_selector.value].width and 0 <= abs_y < pyxel.tilemaps[self.t_tilemap_selector.value].height:
                pyxel.tilemaps[self.t_tilemap_selector.value].pset(abs_x, abs_y, tile)

    def rotate_tilemap_selection(self):
        if not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        if width != height:
            return
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.t_tilemap_offset_x
                abs_y = y + self.t_tilemap_offset_y
                row.append(pyxel.tilemaps[self.t_tilemap_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)
        
        for y in range(height):
            for x in range(width):
                new_x = min_x + y
                new_y = min_y + (width - 1 - x)
                
                if new_x <= max_x and new_y <= max_y:
                    abs_x = new_x + self.t_tilemap_offset_x
                    abs_y = new_y + self.t_tilemap_offset_y
                    if 0 <= abs_x < pyxel.tilemaps[self.t_tilemap_selector.value].width and 0 <= abs_y < pyxel.tilemaps[self.t_tilemap_selector.value].height:
                        pyxel.tilemaps[self.t_tilemap_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def flip_tilemap_selection_horizontal(self):
        if not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        width = max_x - min_x + 1
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.t_tilemap_offset_x
                abs_y = y + self.t_tilemap_offset_y
                row.append(pyxel.tilemaps[self.t_tilemap_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)

        for y in range(max_y - min_y + 1):
            for x in range(width):
                new_x = min_x + (width - 1 - x)
                abs_x = new_x + self.t_tilemap_offset_x
                abs_y = (min_y + y) + self.t_tilemap_offset_y
                if 0 <= abs_x < pyxel.tilemaps[self.t_tilemap_selector.value].width and 0 <= abs_y < pyxel.tilemaps[self.t_tilemap_selector.value].height:
                    pyxel.tilemaps[self.t_tilemap_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def flip_tilemap_selection_vertical(self):
        if not self.t_selection or self.current_tool != SELECT_TOOL:
            return
        
        x0, y0, x1, y1 = self.t_selection
        min_x, min_y = min(x0, x1), min(y0, y1)
        max_x, max_y = max(x0, x1), max(y0, y1)
        
        height = max_y - min_y + 1
        
        temp_buffer = []
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                abs_x = x + self.t_tilemap_offset_x
                abs_y = y + self.t_tilemap_offset_y
                row.append(pyxel.tilemaps[self.t_tilemap_selector.value].pget(abs_x, abs_y))
            temp_buffer.append(row)
        
        for y in range(height):
            for x in range(max_x - min_x + 1):
                new_y = min_y + (height - 1 - y)
                abs_x = (min_x + x) + self.t_tilemap_offset_x
                abs_y = new_y + self.t_tilemap_offset_y
                if 0 <= abs_x < pyxel.tilemaps[self.t_tilemap_selector.value].width and 0 <= abs_y < pyxel.tilemaps[self.t_tilemap_selector.value].height:
                    pyxel.tilemaps[self.t_tilemap_selector.value].pset(abs_x, abs_y, temp_buffer[y][x])

    def update_tilemap_editor(self):
        #? Grid
        if pyxel.btnp(pyxel.KEY_G): self.t_grid = not self.t_grid

        #? Selection Shortcuts
        if pyxel.btn(pyxel.KEY_CTRL) or pyxel.btn(pyxel.KEY_GUI):
            if pyxel.btnp(pyxel.KEY_R):
                self.push_tilemap_history()
                self.rotate_tilemap_selection()
            elif pyxel.btnp(pyxel.KEY_H):
                self.push_tilemap_history()
                self.flip_tilemap_selection_horizontal()
            elif pyxel.btnp(pyxel.KEY_F):
                self.push_tilemap_history()
                self.flip_tilemap_selection_vertical()
            elif pyxel.btnp(pyxel.KEY_C):
                self.copy_tilemap()
            elif pyxel.btnp(pyxel.KEY_X):
                self.push_tilemap_history()
                self.cut_tilemap()
            elif pyxel.btnp(pyxel.KEY_V):
                self.push_tilemap_history()
                self.paste_tilemap()
            elif pyxel.btnp(pyxel.KEY_Z):
                self.undo_tilemap()
            elif pyxel.btnp(pyxel.KEY_T):
                self.place_tiles()

        #? Tools Shortcut
        for key in TOOLS_SHORTCUTS.keys():
            if pyxel.btnp(key) and not (pyxel.btn(pyxel.KEY_CTRL) or pyxel.btn(pyxel.KEY_GUI)):
                self.current_tool = TOOLS_SHORTCUTS[key]

        #? Editor
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, EDITOR_X, EDITOR_Y, EDITOR_SIZE, EDITOR_SIZE):
            mx = (pyxel.mouse_x - EDITOR_X) // TILEMAP_TILE_SIZE + self.t_tilemap_offset_x 
            my = (pyxel.mouse_y - EDITOR_Y) // TILEMAP_TILE_SIZE + self.t_tilemap_offset_y 
            tx, ty = (self.t_tile_selected[0] + self.t_tile_offset_x // 8, self.t_tile_selected[1] + self.t_tile_offset_y // 8)

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):

                if self.current_tool in [FILLED_RECT_TOOL, RECT_TOOL, FILLED_ELLI_TOOL, ELLI_TOOL, LINE_TOOL]:
                    self.t_drag_start = (mx, my)
                if self.current_tool == BUCKET_TOOL:
                    self.push_tilemap_history()
                    self.commit_tiles(self.flood_fill_tilemap(mx, my, pyxel.tilemaps[self.t_tilemap_selector.value].pget(mx, my), (tx, ty)))
                elif self.current_tool == SWAP_TOOL:
                    self.push_tilemap_history()
                    self.commit_tiles(self.swap_fill_tilemap(pyxel.tilemaps[self.t_tilemap_selector.value].pget(mx, my), (tx, ty)))
                elif self.current_tool == SELECT_TOOL:
                    x = (pyxel.mouse_x - EDITOR_X) // TILEMAP_TILE_SIZE
                    y = (pyxel.mouse_y - EDITOR_Y) // TILEMAP_TILE_SIZE
                    self.t_selection = [x, y, x, y]

            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                if self.current_tool == PEN_TOOL:
                    pyxel.tilemaps[self.t_tilemap_selector.value].pset(mx, my, (tx, ty))
                elif self.current_tool == MIRROR_TOOL:
                    pyxel.tilemaps[self.t_tilemap_selector.value].pset(mx, my, (tx, ty))
                    axis_x = self.t_tilemap_offset_x + 8
                    mx_mirror = axis_x - (mx - axis_x) - 1
                    if 0 <= mx_mirror < pyxel.tilemaps[self.t_tilemap_selector.value].width:
                        pyxel.tilemaps[self.t_tilemap_selector.value].pset(mx_mirror, my, (tx, ty))
                elif self.current_tool == SELECT_TOOL and self.t_selection:
                    x = (pyxel.mouse_x - EDITOR_X) // TILEMAP_TILE_SIZE
                    y = (pyxel.mouse_y - EDITOR_Y) // TILEMAP_TILE_SIZE
                    self.t_selection[2] = x
                    self.t_selection[3] = y

            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self.t_drag_start:
                x0, y0 = self.t_drag_start
                max_x, max_y = max(x0, mx), max(y0, my)
                min_x, min_y = min(x0, mx), min(y0, my)

                self.push_tilemap_history()

                if self.current_tool == FILLED_RECT_TOOL:
                    self.commit_tiles(self.rect(min_x, min_y, max_x, max_y))
                elif self.current_tool == RECT_TOOL:
                    self.commit_tiles(self.rect(min_x, min_y, max_x, max_y, False))
                elif self.current_tool == FILLED_ELLI_TOOL:
                    self.commit_tiles(self.elli(min_x, min_y, max_x, max_y))
                elif self.current_tool == ELLI_TOOL:
                    self.commit_tiles(self.elli(min_x, min_y, max_x, max_y, False))
                elif self.current_tool == LINE_TOOL:
                    self.commit_tiles(self.line(x0, y0, mx, my))

                self.t_drag_start = None

            if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
                tx, ty = pyxel.tilemaps[self.t_tilemap_selector.value].pget(mx, my)
                self.t_tile_offset_x = tx * 8
                self.t_tile_offset_y = ty * 8
                self.t_tile_selected = (0, 0)
        else:
            self.t_drag_start = None

        #? Tiles Picker
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, TILES_PICKER_X, TILES_PICKER_Y, TILES_PICKER_SIZE, TILES_PICKER_SIZE):
            mx = (pyxel.mouse_x - TILES_PICKER_X) // 8
            my = (pyxel.mouse_y - TILES_PICKER_Y) // 8

            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.t_tile_selected = (mx, my)

        #? Movement
        if pyxel.btn(pyxel.KEY_LSHIFT):
            if pyxel.btnp(pyxel.KEY_RIGHT, repeat=5):
                self.t_tile_offset_x += 8
            if pyxel.btnp(pyxel.KEY_LEFT, repeat=5):
                self.t_tile_offset_x -= 8
            if pyxel.btnp(pyxel.KEY_DOWN, repeat=5):
                self.t_tile_offset_y += 8
            if pyxel.btnp(pyxel.KEY_UP, repeat=5):
                self.t_tile_offset_y -= 8
        else:
            if pyxel.btnp(pyxel.KEY_RIGHT, repeat=5):
                self.t_tilemap_offset_x += 8
            if pyxel.btnp(pyxel.KEY_LEFT, repeat=5):
                self.t_tilemap_offset_x -= 8
            if pyxel.btnp(pyxel.KEY_DOWN, repeat=5):
                self.t_tilemap_offset_y += 8
            if pyxel.btnp(pyxel.KEY_UP, repeat=5):
                self.t_tilemap_offset_y -= 8
        self.t_tilemap_offset_x = max(0, min(pyxel.tilemaps[self.t_tilemap_selector.value].width - 16, self.t_tilemap_offset_x))
        self.t_tilemap_offset_y = max(0, min(pyxel.tilemaps[self.t_tilemap_selector.value].height - 16, self.t_tilemap_offset_y))
        self.t_tile_offset_x = max(0, min(pyxel.images[self.t_image_selector.value].width - 64, self.t_tile_offset_x))
        self.t_tile_offset_y = max(0, min(pyxel.images[self.t_image_selector.value].height - 64, self.t_tile_offset_y))

        #? Selectors
        t = self.t_tilemap_selector.update()
        if t:
            imgsrc = pyxel.tilemaps[self.t_tilemap_selector.value].imgsrc
            self.t_image_selector.value = imgsrc if isinstance(imgsrc, int) else pyxel.images.to_list().index(imgsrc)
        t = self.t_image_selector.update()
        if t:
            pyxel.tilemaps[self.t_tilemap_selector.value].imgsrc = self.t_image_selector.value
        self.t_layer_selector.update()
        self.t_grid_selector.update()

        #? Tool Buttons
        for tool_button in self.tool_buttons:
            c = tool_button.update(self.current_tool)
            self.current_tool = c if c is not None else self.current_tool

    def draw_tilemap_editor(self):
        #? Selectors
        self.t_tilemap_selector.draw()
        self.t_image_selector.draw()
        self.t_layer_selector.draw()
        self.t_grid_selector.draw()

        #? Editor
        if self.t_layer_selector.value != "None":
            pyxel.bltm(EDITOR_X, EDITOR_Y, self.t_layer_selector.value, self.t_tilemap_offset_x * 8, self.t_tilemap_offset_y * 8, EDITOR_SIZE, EDITOR_SIZE)
            pyxel.bltm(EDITOR_X, EDITOR_Y, self.t_tilemap_selector.value, self.t_tilemap_offset_x * 8, self.t_tilemap_offset_y * 8, EDITOR_SIZE, EDITOR_SIZE, 0)
        else:
            pyxel.bltm(EDITOR_X, EDITOR_Y, self.t_tilemap_selector.value, self.t_tilemap_offset_x * 8, self.t_tilemap_offset_y * 8, EDITOR_SIZE, EDITOR_SIZE)

        #? Draw Preview
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, EDITOR_X, EDITOR_Y, EDITOR_SIZE, EDITOR_SIZE):
            mx = (pyxel.mouse_x - EDITOR_X) // TILEMAP_TILE_SIZE + self.t_tilemap_offset_x
            my = (pyxel.mouse_y - EDITOR_Y) // TILEMAP_TILE_SIZE + self.t_tilemap_offset_y
            tx, ty = (self.t_tile_selected[0] + self.t_tile_offset_x // 8, self.t_tile_selected[1] + self.t_tile_offset_y // 8)
            tiles = set()

            pyxel.text(EDITOR_X + 1, 8, f"({mx},{my})", self.COLORS_LEN + 1)

            if self.current_tool == BUCKET_TOOL:
                tiles = self.flood_fill_tilemap(mx, my, pyxel.tilemaps[self.t_tilemap_selector.value].pget(mx, my), (tx, ty))
            elif self.current_tool == SWAP_TOOL:
                tiles = self.swap_fill_tilemap(pyxel.tilemaps[self.t_tilemap_selector.value].pget(mx, my), (tx, ty))

            if self.t_drag_start:
                x0, y0 = self.t_drag_start
                min_x, max_x = min(x0, mx), max(x0, mx)
                min_y, max_y = min(y0, my), max(y0, my)

                if self.current_tool == FILLED_RECT_TOOL:
                    tiles = self.rect(min_x, min_y, max_x, max_y)
                elif self.current_tool == RECT_TOOL:
                    tiles = self.rect(min_x, min_y, max_x, max_y, False)
                elif self.current_tool == FILLED_ELLI_TOOL:
                    tiles = self.elli(min_x, min_y, max_x, max_y)
                elif self.current_tool == ELLI_TOOL:
                    tiles = self.elli(min_x, min_y, max_x, max_y, False)
                elif self.current_tool == LINE_TOOL:
                    tiles = self.line(x0, y0, mx, my)

            self.draw_preview_tiles(tiles)

        #? Grid
        if self.t_grid:
            for y in range(EDITOR_Y, EDITOR_Y + EDITOR_SIZE, self.t_grid_selector.value * TILEMAP_TILE_SIZE):
                pyxel.rect(EDITOR_X, y, EDITOR_SIZE, 1, self.COLORS_LEN)
            for x in range(EDITOR_X, EDITOR_X + EDITOR_SIZE, self.t_grid_selector.value * TILEMAP_TILE_SIZE):
                pyxel.rect(x, EDITOR_Y, 1, EDITOR_SIZE, self.COLORS_LEN)
            pyxel.rect(EDITOR_X, EDITOR_Y + EDITOR_SIZE - 1, EDITOR_SIZE, 1, self.COLORS_LEN)
            pyxel.rect(EDITOR_X + EDITOR_SIZE - 1, EDITOR_Y, 1, EDITOR_SIZE, self.COLORS_LEN)

        #? Selection Preview
        if self.t_selection and self.current_tool == SELECT_TOOL:
            x0, y0, x1, y1 = self.t_selection
            min_x, max_x = min(x0, x1), max(x0, x1)
            min_y, max_y = min(y0, y1), max(y0, y1)

            pyxel.rectb(EDITOR_X + min_x * TILEMAP_TILE_SIZE, EDITOR_Y + min_y * TILEMAP_TILE_SIZE, (max_x - min_x + 1) * TILEMAP_TILE_SIZE, (max_y - min_y + 1) * TILEMAP_TILE_SIZE, self.COLORS_LEN + 1)

        #? Tool Buttons
        for tool_button in self.tool_buttons:
            tool_button.draw()

        #? Tiles Picker
        pyxel.blt(TILES_PICKER_X, TILES_PICKER_Y, self.t_image_selector.value, self.t_tile_offset_x, self.t_tile_offset_y, 64, 64)
        pyxel.rectb(TILES_PICKER_X + self.t_tile_selected[0] * 8, TILES_PICKER_Y + self.t_tile_selected[1] * 8, 8, 8, self.COLORS_LEN + 1)
        if collision_point_rect(pyxel.mouse_x, pyxel.mouse_y, TILES_PICKER_X, TILES_PICKER_Y, TILES_PICKER_SIZE, TILES_PICKER_SIZE):
            tx = (pyxel.mouse_x - TILES_PICKER_X) // 8 + self.t_tile_offset_x // 8
            ty = (pyxel.mouse_y - TILES_PICKER_Y) // 8 + self.t_tile_offset_y // 8
            pyxel.text(TILES_PICKER_X, TILES_PICKER_Y - 8, f"({tx},{ty})", self.COLORS_LEN + 1)
        else:
            pyxel.text(TILES_PICKER_X, TILES_PICKER_Y - 8, f"({self.t_tile_offset_x // 8 + self.t_tile_selected[0]},{self.t_tile_offset_y // 8 + self.t_tile_selected[1]})", self.COLORS_LEN + 1)

    #? ---------- AUTOTILE EDITOR ---------- ?#

    def get_neighbors(self, tilemap_id:int, tiles_y:list, x:int, y:int):
        n = 0
        if y > 0 and pyxel.tilemaps[tilemap_id].pget(x, y - 1)[1] in tiles_y:
            n += 1
        if x < pyxel.tilemaps[self.t_tilemap_selector.value].width and pyxel.tilemaps[tilemap_id].pget(x + 1, y)[1] in tiles_y:
            n += 2
        if y < pyxel.tilemaps[self.t_tilemap_selector.value].height and pyxel.tilemaps[tilemap_id].pget(x, y + 1)[1] in tiles_y:
            n += 4
        if x > 0 and pyxel.tilemaps[tilemap_id].pget(x - 1, y)[1] in tiles_y:
            n += 8

        if n == 15:
            if y > 0 and x > 0 and pyxel.tilemaps[tilemap_id].pget(x - 1, y - 1)[1] in tiles_y:
                n += 1
            if y > 0 and x < pyxel.tilemaps[self.t_tilemap_selector.value].width and pyxel.tilemaps[tilemap_id].pget(x + 1, y - 1)[1] in tiles_y:
                n += 2
            if y < pyxel.tilemaps[self.t_tilemap_selector.value].height and x < pyxel.tilemaps[self.t_tilemap_selector.value].width and pyxel.tilemaps[tilemap_id].pget(x + 1, y + 1)[1] in tiles_y:
                n += 4
            if y < pyxel.tilemaps[self.t_tilemap_selector.value].height and x > 0 and pyxel.tilemaps[tilemap_id].pget(x - 1, y + 1)[1] in tiles_y:
                n += 8

        return n
    
    def place_tiles(self):
        new_tiles = [[(0, 0) for _ in range(pyxel.tilemaps[self.t_tilemap_selector.value].width)] for _ in range(pyxel.tilemaps[self.t_tilemap_selector.value].height)]

        for y in range(pyxel.tilemaps[self.t_tilemap_selector.value].height):
            for x in range(pyxel.tilemaps[self.t_tilemap_selector.value].width):
                tile_x, tile_y  = pyxel.tilemaps[self.t_tilemap_selector.value].pget(x, y)
                tiles_y = self.a_tiles_y[self.t_image_selector.value]

                if tile_y in tiles_y:
                    neighbors = self.get_neighbors(self.t_tilemap_selector.value, tiles_y, x, y)
                    new_tiles[y][x] = (neighbors, tile_y)
                else:
                    new_tiles[y][x] = (tile_x, tile_y)

        for y in range(pyxel.tilemaps[self.t_tilemap_selector.value].height):
            for x in range(pyxel.tilemaps[self.t_tilemap_selector.value].width):
                pyxel.tilemaps[self.t_tilemap_selector.value].pset(x, y, new_tiles[y][x])

    def place_a_buttons(self):
        l = []
        c = 0
        for y in [2, 12]:
            for x in range(16):
                l.append(Button(80 + x * 10, y, c, self.COLORS_LEN))
                c += 1
        return l

    def draw_tileset(self, x:int, y:int, image:int, tile_y:int):
        pyxel.blt(x, y + 8, image, 0, tile_y * 8, 8, 8)

        pyxel.blt(x + 10, y, image, 6 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 18, y, image, 14 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 26, y, image, 12 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 10, y + 8, image, 7 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 18, y + 8, image, 30 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 26, y + 8, image, 13 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 10, y + 16, image, 3 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 18, y + 16, image, 11 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 26, y + 16, image, 9 * 8, tile_y * 8, 8, 8)

        pyxel.blt(x + 36, y, image, 4 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 36, y + 8, image, 5 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 36, y + 16, image, 1 * 8, tile_y * 8, 8, 8)

        pyxel.blt(x + 10, y + 26, image, 2 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 18, y + 26, image, 10 * 8, tile_y * 8, 8, 8)
        pyxel.blt(x + 26, y + 26, image, 8 * 8, tile_y * 8, 8, 8)

    def update_autotile_editor(self):
        #? Buttons
        for button in self.a_buttons[self.a_image_selector.value]:
            button.update()

        self.a_tiles_y[self.a_image_selector.value] = [b.id for b in self.a_buttons[self.a_image_selector.value] if b.selected]

        #? Selectors
        self.a_image_selector.update()

    def draw_autotile_editor(self):
        #? Selectors
        self.a_image_selector.draw()

        #? Buttons
        for button in self.a_buttons[self.a_image_selector.value]:
            button.draw()

        #? Tilesets
        x, y = 0, 0
        for i in range(len(self.a_tiles_y[self.a_image_selector.value])):
            self.draw_tileset(16 + x, 22 + y, self.a_image_selector.value, self.a_tiles_y[self.a_image_selector.value][i])
            x = (x + 46) % 230
            if x == 0:
                y += 36

    #? ---------- ANIMATION EDITOR ---------- ?#

    def update_animation_editor(self):
        #? Entries
        self.n_start_uv_entry.update()
        self.n_sprite_wh_entry.update()
        self.n_colkey_entry.update()
        self.n_frames_entry.update()
        self.n_speed_entry.update()

        #? Selectors
        self.n_image_selector.update()

        #? Buttons
        if self.n_play_button.update(5) is not None:
            self.n_is_playing = not self.n_is_playing
        
        if self.n_prev_button.update(5) is not None:
            if self.n_frame > 0:
                self.n_frame -= 1
                self.n_is_playing = False
        
        if self.n_next_button.update(5) is not None:
            try:
                total_frames = int(self.n_frames_entry.value)
                if self.n_frame < total_frames - 1:
                    self.n_frame += 1
                    self.n_is_playing = False
            except:
                pass

        #? Retrieving
        u = v = w = h = c = t = s = None

        try:
            u, v = map(int, self.n_start_uv_entry.value.split(","))
            w, h = map(int, self.n_sprite_wh_entry.value.split(","))
            c = int(self.n_colkey_entry.value)
            t = int(self.n_frames_entry.value)
            s = int(self.n_speed_entry.value)
            
            if self.n_is_playing and t > 0:
                self.n_frame_timer += 1
                if self.n_frame_timer >= s:
                    self.n_frame_timer = 0
                    self.n_frame = (self.n_frame + 1) % t
            
        except:
            pass

        self.n_animation = (u, v, w, h, c, t, s)

    def draw_animation_editor(self):
        #? Entries
        self.n_start_uv_entry.draw()
        self.n_sprite_wh_entry.draw()
        self.n_colkey_entry.draw()
        self.n_frames_entry.draw()
        self.n_speed_entry.draw()

        #? Selectors
        self.n_image_selector.draw()

        #? Buttons
        self.n_prev_button.draw()
        self.n_play_button.draw()
        self.n_next_button.draw()

        #? Draw current frame
        u, v, w, h, c, t, s = self.n_animation
        if all(x is not None for x in [u, v, w, h, t, s]) and t > 0:
            frame_u = u + (self.n_frame * w)
            
            scale_x = EDITOR_SIZE / w
            scale_y = EDITOR_SIZE / h
            scale = min(scale_x, scale_y)
            
            scaled_w = int(w * scale)
            scaled_h = int(h * scale)
            
            center_x = EDITOR_X + (EDITOR_SIZE - scaled_w) // 2
            center_y = EDITOR_Y + (EDITOR_SIZE - scaled_h) // 2
            
            for py in range(h):
                for px in range(w):
                    pixel_color = pyxel.images[self.n_image_selector.value].pget(frame_u + px, v + py)
                    if pixel_color != c:
                        draw_x = center_x + int(px * scale)
                        draw_y = center_y + int(py * scale)
                        pyxel.rect(draw_x, draw_y, int(scale), int(scale), pixel_color)
            
            frame_text = f"Frame: {self.n_frame + 1}/{t}"
            pyxel.text(EDITOR_X, EDITOR_Y + EDITOR_SIZE + 2, frame_text, self.COLORS_LEN + 1)

    #? ---------- SOUND EDITOR ---------- ?#

    def update_sound_editor(self):
        #? Editor
        if (SOUND_EDITOR_X <= pyxel.mouse_x < SOUND_EDITOR_X + SOUND_EDITOR_W) and (SOUND_EDITOR_Y <= pyxel.mouse_y < SOUND_EDITOR_Y + SOUND_EDITOR_H):
            col = (pyxel.mouse_x - SOUND_EDITOR_X) // 2
            row = (pyxel.mouse_y - SOUND_EDITOR_Y) // 2

            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                self.so_sounds[self.so_sound_selector.value].notes[col] = row
            if pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT):
                self.so_sounds[self.so_sound_selector.value].notes[col] = None

        #? Play
        if pyxel.btnp(pyxel.KEY_SPACE) or self.so_play_button.update(5):
            if not pyxel.play_pos(0):
                v = self.so_sound_selector.value
                self.so_sounds[v].save(v)
                pyxel.play(0, v)
            else:
                pyxel.stop(0)

        #? Reset
        if self.so_reset_button.update(5):
            v = self.so_sound_selector.value
            self.so_sounds[v] = SoundEffect()
            self.so_speed_selector.value = self.so_sounds[v].speed
            self.so_tone_selector.value = self.so_sounds[v].tone
            self.so_effect_selector.value = self.so_sounds[v].effect
            self.so_volume_selector.value = self.so_sounds[v].volume

        #? Selectors
        s = self.so_sound_selector.update()
        sp = self.so_speed_selector.update()
        t = self.so_tone_selector.update()
        e = self.so_effect_selector.update()
        vo = self.so_volume_selector.update()

        v = self.so_sound_selector.value
        if s:
            self.so_speed_selector.value = self.so_sounds[v].speed
            self.so_tone_selector.value = self.so_sounds[v].tone
            self.so_effect_selector.value = self.so_sounds[v].effect
            self.so_volume_selector.value = self.so_sounds[v].volume

        if sp:    self.so_sounds[v].speed = self.so_speed_selector.value
        if t:     self.so_sounds[v].tone = self.so_tone_selector.value
        if e:     self.so_sounds[v].effect = self.so_effect_selector.value
        if vo:    self.so_sounds[v].volume = self.so_volume_selector.value

    def draw_sound_editor(self):
        #? Selectors
        self.so_sound_selector.draw()
        self.so_speed_selector.draw()
        self.so_tone_selector.draw()
        self.so_effect_selector.draw()
        self.so_volume_selector.draw()

        #? Buttons
        self.so_play_button.draw()
        self.so_reset_button.draw()

        #? Editor
        pyxel.rect(SOUND_EDITOR_X, SOUND_EDITOR_Y, SOUND_EDITOR_W, SOUND_EDITOR_H, self.COLORS_LEN + 1)
        for col, row in enumerate(self.so_sounds[self.so_sound_selector.value].notes):
            if row is not None:
                cell_x = SOUND_EDITOR_X + col * 2
                cell_y = SOUND_EDITOR_Y + row * 2
                pyxel.rect(cell_x, cell_y, 2, 2, self.COLORS_LEN + 2)

    #? ---------- MUSIC ---------- ?#

    def import_music(self):
        filename = self.m_import_entry.value + ".json"
        if os.path.isfile(filename):
            f = open(filename, "rt")
            music = json.loads(f.read())
            music_n = 100 + self.m_music_selector.value * 4
            for i, sound in enumerate(music):
                pyxel.sounds[music_n + i].set(*sound)
            self.m_import_entry.value= ""

    def update_music_editor(self):
        #? Selectors
        m = self.m_music_selector.update()
        if m:
            self.m_import_entry.value = ""

        #? Entry
        self.m_import_entry.update()

        #? Import
        if self.m_import_button.update(5):
            self.import_music()

        #? Play
        if pyxel.btnp(pyxel.KEY_SPACE) or self.m_play_button.update(5):
            if not pyxel.play_pos(0):
                n = 100 + self.m_music_selector.value * 4
                for i in range(4):
                    pyxel.play(i, n + i)
            else:
                for i in range(4):
                    pyxel.stop(i)

        #? Reset
        if self.m_reset_button.update(5):
            n = 100 + self.m_music_selector.value * 4
            for i in range(4):
                pyxel.sounds[n + i].set("", "", "", "", 15)

    def draw_music_editor(self):
        #? Selectors
        self.m_music_selector.draw()

        #? Entry
        self.m_import_entry.draw()

        #? Buttons
        self.m_play_button.draw()
        self.m_reset_button.draw()
        self.m_import_button.draw()

    #? ---------- MAIN ---------- ?#

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.save()
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_S) and (pyxel.btn(pyxel.KEY_CTRL) or pyxel.btn(pyxel.KEY_GUI)):
            self.save()

        for tab_button in self.tab_buttons:
            c = tab_button.update(self.current_tab)
            self.current_tab = c if c is not None else self.current_tab

        if self.current_tab == SPRITE_EDITOR:         self.update_sprite_editor()
        elif self.current_tab == TILEMAP_EDITOR:      self.update_tilemap_editor()
        elif self.current_tab == AUTOTILE_EDITOR:     self.update_autotile_editor()
        elif self.current_tab == ANIMATION_EDITOR:    self.update_animation_editor()
        elif self.current_tab == SOUND_EDITOR:        self.update_sound_editor()
        elif self.current_tab == MUSIC_EDITOR:        self.update_music_editor()

    def draw(self):
        pyxel.cls(self.COLORS_LEN)

        for tab_button in self.tab_buttons:
            tab_button.draw()

        if self.current_tab == SPRITE_EDITOR:         self.draw_sprite_editor()
        elif self.current_tab == TILEMAP_EDITOR:      self.draw_tilemap_editor()
        elif self.current_tab == AUTOTILE_EDITOR:     self.draw_autotile_editor()
        elif self.current_tab == ANIMATION_EDITOR:    self.draw_animation_editor()
        elif self.current_tab == SOUND_EDITOR:        self.draw_sound_editor()
        elif self.current_tab == MUSIC_EDITOR:        self.draw_music_editor()

        for y in range(len(MOUSE_ICON)):
            for x in range(len(MOUSE_ICON[y])):
                if MOUSE_ICON[y][x] != 0:
                    pyxel.rect(pyxel.mouse_x + x, pyxel.mouse_y + y, 1, 1, self.COLORS_LEN + MOUSE_ICON[y][x])

if __name__ == "__main__":
    EXTENDED_PICO8_COLORS = [0x000000, 0x1D2B53, 0x7E2553, 0x008751, 0xAB5236, 0x5F574F, 0xC2C3C7, 0xFFF1E8, 0xFF004D, 0xFFA300, 0xFFEC27, 0x00E436, 0x29ADFF, 0x83769C, 0xFF77A8, 0xFFCCAA, 0x1A1C2C, 0x5D275D, 0x008080, 0x1B6535, 0x73464D, 0x9D9D9D, 0xFFFFFF, 0xFF6C24, 0xFFD93F, 0xB2D732, 0x3CA370, 0x0066CC, 0x45283C, 0xA288AE, 0xF3B4B4, 0xD4A373]
    Editor(EXTENDED_PICO8_COLORS)