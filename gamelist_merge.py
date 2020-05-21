#!/usr/bin/python3
import click
import xml.etree.ElementTree as ET
import os
import sys
import shutil

dst_folder = None


def get_game_id(game):
    game_id = game.get('id')
    if game_id is None:
        rom_name = os.path.basename(game.find('path').text)
        game_id = os.path.splitext(rom_name)[0]
    return game_id


def get_dst_resource_folder(root):
    global dst_folder

    for game in root.findall('game'):
        if game.find('image') is not None:
            dst_folder = os.path.dirname(game.find('image').text)
            return

    exit(1)


def move_resources(game):
    res_image = game.find('image')
    res_cover = game.find('cover')
    res_marquee = game.find('marquee')

    if res_image is not None:
        dst_res = dst_folder + "/" + os.path.basename(res_image.text)
        shutil.copy(res_image.text.replace("~/", "/home/osmc/"), dst_res)
        res_image.text = dst_res
    if res_cover is not None:
        dst_res = dst_folder + "/" + os.path.basename(res_cover.text)
        shutil.copy(res_cover.text.replace("~/", "/home/osmc/"), dst_res)
        res_cover.text = dst_res
    if res_marquee is not None:
        dst_res = dst_folder + "/" + os.path.basename(res_marquee.text)
        shutil.copy(res_marquee.text.replace("~/", "/home/osmc/"), dst_res)
        res_marquee.text = dst_res


@click.command()
@click.option('--src', '-s', 'src', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True), help='Source file')
@click.option('--dst', '-d', 'dst', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=True, readable=True), help='Dest file')
@click.option('--tag', '-t', 'tag', required=False, type=click.STRING, help='Tag to move.')
def gamelist_merge(src, dst, tag):

    # parsing xmls
    print(src)
    src_tree = ET.parse(src)
    dst_tree = ET.parse(dst)

    # getting root
    src_root = src_tree.getroot()
    dst_root = dst_tree.getroot()

    print("Source file as {} entries".format(len(src_root)))
    print("Dest file as {} entries".format(len(dst_root)))

    get_dst_resource_folder(dst_root)

    # reading dest games for faster access
    game_dict = {}
    for dst_game in dst_root.findall('game'):
        game_dict[get_game_id(dst_game)] = dst_game

    updated = 0
    added = 0
    total = len(dst_root)

    for src_game in src_root.findall('game'):
        game_id = get_game_id(src_game)
        if game_id in game_dict:
            # Updating game name
            game_dict[game_id].find('name').text = src_game.find('name').text
            updated += 1
        else:
            # this game is not known, adding to dest
            move_resources(src_game)
            dst_root.append(src_game)
            added += 1

        print("\rU {:>4} / + {:>4} / {} Total".format(updated, added, total + added), end="")
        sys.stdout.flush()

    print("\nSource file as {} entries".format(len(src_root.findall('./game'))))
    print("Dest file as {} entries".format(len(dst_root.findall('./game'))))

    dst = dst + ".new"
    print("\nWritting new xml file to {}".format(dst))
    dst_tree.write(dst, encoding="UTF-8", xml_declaration=True)


if __name__ == '__main__':
    gamelist_merge()
