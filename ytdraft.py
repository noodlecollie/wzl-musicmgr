import os
import argparse
from lib import config, ytdlp, utils

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))

def parseArgs():
	parser = argparse.ArgumentParser(
		"ytdraft",
		description="Downloads YouTube videos, converts them to audio, and places them in the specified folder."
	)

	parser.add_argument(
		"urls",
		nargs="+",
		help="URLs for YouTube videos to download."
	)

	parser.add_argument(
		"-o",
		"--output-dir",
		help="Directory for output files. Defaults to the configured draft directory."
	)

	return parser.parse_args()

def loadConfig():
	return config.Config(os.path.join(SCRIPT_DIR, "config.json"))

def main():
	args = parseArgs()
	configFile = loadConfig()

	if not args.output_dir:
		args.output_dir = configFile.getDraftDir()

	if os.path.isfile(args.output_dir):
		raise ValueError(f"Output directory {args.output_dir} is a file on disk")

	videoIDs = []

	for url in args.urls:
		try:
			videoIDs.append(ytdlp.extractVideoIDFromURL(url))
		except ValueError as ex:
			print(f"{ex}, ignoring")

	if not videoIDs:
		return

	os.makedirs(args.output_dir, exist_ok=True)

	successful = []
	failed = []

	for videoID in videoIDs:
		try:
			print("Downloading video", videoID)

			result = ytdlp.downloadYouTubeVideo(configFile, videoID, args.output_dir, utils.MP3_QUALITY_DRAFT)
			print(result.stdout)
			result.check_returncode()

			existed, name = ytdlp.fileAlreadyExistedOnDisk(result)

			if existed:
				if name:
					raise RuntimeError(f"File {name} already existed on disk")
				else:
					raise RuntimeError("File already existed on disk")

			successful.append(ytdlp.extractAudioNameFromResult(result))
		except Exception as ex:
			failed.append(f"{videoID}: {ex}")

	print("Success:", len(successful), "files")

	if successful:
		for entry in successful:
			print(f"  {entry}")

	print("Failed:", len(failed), "files")

	if failed:
		for entry in failed:
			print(f"  {entry}")

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
