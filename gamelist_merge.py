#!/usr/bin/python3
import click
import xml.etree.ElementTree as ET
import os
import sys

def check_game_id(root):
	for game in root.findall('game'):
		game_id = game.get('id')
		if game_id:
			# print("Found : " + game_id)
			pass
		else:
			rom_name = os.path.basename(game.find('path').text)
			game_id = os.path.splitext(rom_name)[0]
			# print("Creating : " + game_id)
			game.set('id', game_id)

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

	print("Source file as {} entries".format(len(src_root.findall('./game') )))
	print("Dest file as {} entries".format(len(dst_root.findall('./game') )))

	check_game_id(src_root)
	check_game_id(dst_root)


	updated = 0
	added = 0
	total = len(dst_root)

	for src_game in src_root.findall('game'):
		dst_game = dst_root.find("./game[@id='{}']".format(src_game.get('id')))
		if dst_game:
			# game found, name to be updated
			dst_game.find('name').text = src_game.find('name').text
			updated += 1
#			print("{} -> {}".format(src_game.find('path').text, dst_game.find('path').text))
			pass
		else:
			dst_root.append(src_game)
			#print("{} not found in dest".format(src_game.find('path').text))
			added += 1

		print("U {:>4} / + {:>4} / {} Total".format(updated, added, total + added), end="\r")
		sys.stdout.flush()

	print("\nSource file as {} entries".format(len(src_root.findall('./game') )))
	print("Dest file as {} entries".format(len(dst_root.findall('./game') )))

	dst = dst + ".new"
	print("\nWritting new xml file to {}".format(dst))
	dst_tree.write(dst)

if __name__ == '__main__':
    gamelist_merge()
