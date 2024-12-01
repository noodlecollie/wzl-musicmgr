import os
import sys
import argparse
from lib import config, ffmpeg

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))

def parseArgs():
	parser = argparse.ArgumentParser(
		"toflac",
		description="Converts an audio file to FLAC."
	)

	parser.add_argument(
		"input",
		nargs="+",
		help="Input files or folders to convert."
	)

	parser.add_argument(
		"output",
		help="Output file, or folder to output multiple files to."
	)

	return parser.parse_args()

def loadConfig():
	return config.Config(os.path.join(SCRIPT_DIR, "config.json"))

def convertSingleFile(configFile, input:str, output:str):
	outputPath = output

	if not os.path.isfile(outputPath):
		fileName = os.path.splitext(os.path.basename(input))[0]
		outputPath = os.path.join(outputPath, fileName + ".flac")

	print(f"Converting: {input} -> {outputPath}")
	ffmpeg.toFLAC(configFile, input, outputPath)

def convertMultipleFiles(configFile, input:list, output:str):
	if os.path.isfile(output):
		raise ValueError("Output must be a directory when converting multiple input files")

	if not os.path.isdir(output):
		os.makedirs(output)

	for item in input:
		if os.path.isfile(item):
			convertSingleFile(configFile, item, output)
			continue

		if os.path.isdir(item):
			for file in os.listdir(item):
				filePath = os.path.abspath(os.path.join(item, file))
				if os.path.isfile(filePath):
					convertSingleFile(configFile, filePath, output)

			continue

		print("Input", item, "was not found on disk, skipping", file=sys.stderr)

def main():
	args = parseArgs()
	configFile = loadConfig()

	if args.output is None:
		args.output = os.getcwd()
	else:
		args.output = os.path.abspath(args.output)

	if len(args.input) == 1 and os.path.isfile(args.input[0]):
		convertSingleFile(configFile, os.path.abspath(args.input[0]), args.output)
	else:
		convertMultipleFiles(configFile, args.input, args.output)

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
