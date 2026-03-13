"""
@author : Léo Imbert
@created : 16/01/2026
@updated : 16/01/2026
"""

#? -------------------- IMPORTATIONS -------------------- ?#

import pyxel
import os

#? -------------------- CONSTANTS -------------------- ?#

MAX_IMAGES = 20
MIN_IMAGE_SIZE = 32
MAX_IMAGE_SIZE = 2048

MAX_TILEMAPS = 50
MIN_TILEMAP_SIZE = 10
MAX_TILEMAP_SIZE = 1024

MAX_MUSICS = 20

SOUNDS_NUMBER = 100

#? -------------------- UTILITIES -------------------- ?#

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def ask_int(text:str, min:int, max:int)-> int:
    while True:
        cls()
        print("*" + "-"*10 + "Pyxres Configurator" + "-"*10 + "*")
        print("")
        print(text)
        print("")

        n = input()

        try:
            n = int(n)
            if min <= n <= max:
                return n
        except ValueError:
            pass

def ask_str(text:str)-> str:
    while True:
        cls()
        print("*" + "-"*10 + "Pyxres Configurator" + "-"*10 + "*")
        print("")
        print(text)
        print("")

        n = input()

        if n:
            return n

#? -------------------- MENUS -------------------- ?#

def main_menu():
    c = ask_int("What do you want to do ?\n1. Create Pyxres\n2. Edit Pyxres\n3. Quit", 1, 3)

    if c == 1:
        create_menu()
    elif c == 2:
        edit_menu()
    elif c == 3:
        cls()
        pyxel.quit()

def create_menu():
    filename = ask_str("How do you want to name your pyxres ?\n(Please don't write the extension)") + ".pyxres"

    n_images = ask_int(f"How many images do you want ?\n(Between 1 and {MAX_IMAGES})", 1, MAX_IMAGES)
    images = []
    for i in range(n_images):
        width = ask_int(f"What is the width of the image {i} ?\n(Between {MIN_IMAGE_SIZE} and {MAX_IMAGE_SIZE})", MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
        height = ask_int(f"What is the height of the image {i} ?\n(Between {MIN_IMAGE_SIZE} and {MAX_IMAGE_SIZE})", MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
        images.append(pyxel.Image(width, height))
    pyxel.images.from_list(images)

    n_tilemaps = ask_int(f"How many tilemaps do you want ?\n(Between 1 and {MAX_TILEMAPS})", 1, MAX_TILEMAPS)
    tilemaps = []
    for i in range(n_tilemaps):
        width = ask_int(f"What is the width of the tilemap {i} ?\n(Between {MIN_TILEMAP_SIZE} and {MAX_TILEMAP_SIZE})", MIN_TILEMAP_SIZE, MAX_TILEMAP_SIZE)
        height = ask_int(f"What is the height of the tilemap {i} ?\n(Between {MIN_TILEMAP_SIZE} and {MAX_TILEMAP_SIZE})", MIN_TILEMAP_SIZE, MAX_TILEMAP_SIZE)
        tilemaps.append(pyxel.Tilemap(width, height, 0))
    pyxel.tilemaps.from_list(tilemaps)

    n_musics = ask_int(f"How many musics do you want ?\n(Between 1 and {MAX_MUSICS})", 1, MAX_MUSICS)

    pyxel.sounds.from_list([pyxel.Sound() for _ in range(SOUNDS_NUMBER + n_musics * 4)])
    for i in range(SOUNDS_NUMBER):
        pyxel.sounds[i].set_tones("T")
        pyxel.sounds[i].set_volumes("7")
        pyxel.sounds[i].set_effects("N")
        pyxel.sounds[i].speed = 1

    pyxel.save(filename)

    main_menu()

def edit_menu():
    filename = ""
    while not os.path.isfile(filename):
        filename = ask_str("What is the filename ?\n(Please don't write the extension)") + ".pyxres"
    pyxel.load(filename)
    images = pyxel.images.to_list()
    tilemaps = pyxel.tilemaps.to_list()
    n_musics = len(pyxel.sounds.to_list()[100:]) // 4

    c = ask_int(f"What do you want to do ?\n{filename} | Images : {len(images)} | Tilemaps : {len(tilemaps)} | Musics : {n_musics}\n1. Add Image\n2. Add Tilemap\n3. Add Music\n4. Remove the last Image\n5. Remove the last Tilemap\n6. Remove the last Music", 1, 6)

    if c == 1:
        if len(images) < MAX_IMAGES:
            width = ask_int(f"What is the width of the new image ?\n(Between {MIN_IMAGE_SIZE} and {MAX_IMAGE_SIZE})", MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
            height = ask_int(f"What is the height of the new image ?\n(Between {MIN_IMAGE_SIZE} and {MAX_IMAGE_SIZE})", MIN_IMAGE_SIZE, MAX_IMAGE_SIZE)
            pyxel.images.from_list(images + [pyxel.Image(width, height)])
            pyxel.save(filename)
        main_menu()
    elif c == 2:
        if len(tilemaps) < MAX_TILEMAPS:
            width = ask_int(f"What is the width of the new tilemap ?\n(Between {MIN_TILEMAP_SIZE} and {MAX_TILEMAP_SIZE})", MIN_TILEMAP_SIZE, MAX_TILEMAP_SIZE)
            height = ask_int(f"What is the height of the new tilemap ?\n(Between {MIN_TILEMAP_SIZE} and {MAX_TILEMAP_SIZE})", MIN_TILEMAP_SIZE, MAX_TILEMAP_SIZE)
            pyxel.tilemaps.from_list(tilemaps + [pyxel.Tilemap(width, height, 0)])
            pyxel.save(filename)
        main_menu()
    elif c == 3:
        if n_musics < MAX_MUSICS:
            pyxel.sounds.from_list(pyxel.sounds.to_list() + [pyxel.Sound() for _ in range(4)])
            pyxel.save(filename)
        main_menu()
    elif c == 4:
        if len(images) > 0:
            pyxel.images.from_list(images[:-1])
            pyxel.save(filename)
        main_menu()
    elif c == 5:
        if len(tilemaps) > 0:
            pyxel.tilemaps.from_list(tilemaps[:-1])
            pyxel.save(filename)
        main_menu()
    elif c == 6:
        if n_musics > 0:
            pyxel.sounds.from_list(pyxel.sounds.to_list()[:-4])
            pyxel.save(filename)
        main_menu()

#? -------------------- MAIN -------------------- ?#

if __name__ == "__main__":
    pyxel.init(64, 64)
    main_menu()
    pyxel.quit()