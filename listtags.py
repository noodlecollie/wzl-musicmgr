import argparse
from lib import id3

def parseArgs():
	parser = argparse.ArgumentParser(
		"listtags",
		description="Lists metadata tags on the specified file."
	)

	parser.add_argument(
		"file",
		nargs=1,
		help="File to dump tags from."
	)

	return parser.parse_args()

def main():
	args = parseArgs()
	tags = id3.dump_tag_string_dict(args.file[0])

	for key in tags:
		print(f"{key}: {tags[key]}")

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
