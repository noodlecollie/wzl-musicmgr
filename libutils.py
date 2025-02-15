import argparse
from lib.music_library import MusicLibrary, KEY_TRACK_TITLE

def addCheckOption(parser: argparse.ArgumentParser, optName: str, helpStr: str, defaultVal: bool = True):
	parser.add_argument(
		"--check-" + optName,
		choices=["yes", "no"],
		default="yes" if defaultVal else "no",
		help=helpStr + " (default: %(default)s)"
	)

def parseArgs():
	parser = argparse.ArgumentParser(
		"libutils",
		description="Script for performing integrity checks and other useful functions on Rekordbox library XML"
	)

	parser.add_argument(
		"path",
		nargs=1,
		help="Rekordbox library XML to read"
	)

	addCheckOption(
		parser,
		"missing-from-everything",
		"Check for any tracks missing from the 'Everything' playlist"
	)

	return parser.parse_args()

def checkMissingFromEverything(library: MusicLibrary):
	everything = {id: True for id in library.playlist_track_ids(("DnB","Everything"))}

	playlistsToSkip = [
		("DnB","Everything"),
		("DnB", "[Import]"),
		("DnB", "Drafts"),
	]

	missing = {}

	for path in library.playlist_paths():
		if path[0] != "DnB" or path in playlistsToSkip:
			continue

		for id in library.playlist_track_ids(path):
			title = library.collection[id][KEY_TRACK_TITLE]

			if title.startswith("DRAFT ") or title == "--------------------":
				continue

			if id not in everything:
				missing[id] = True

	if missing:
		print(len(missing), "tracks were missing from the 'Everything' playlist:")

		for id in missing.keys():
			print(f"  {library.track_desc_str(id)}")
	else:
		print("No tracks were missing from the 'Everything' playlist")

def main():
	args = parseArgs()
	library = MusicLibrary(args.path[0])

	if args.check_missing_from_everything == "yes":
		checkMissingFromEverything(library)

main()
