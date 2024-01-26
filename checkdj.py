import argparse
import os
import sys
from lib import config, validation

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))

def parseArgs():
	parser = argparse.ArgumentParser(
		"checkdj",
		description="Runs validation checks on a directory to search for potential library compatibility issues with "
		"CDJ controllers."
	)

	parser.add_argument(
		"-l",
		"--list-files",
		action="store_true",
		help="Prints lists of files that fail each validation check."
	)

	parser.add_argument(
		"--absolute-paths",
		action="store_true",
		help="If set, file paths reported via --list-files will be absolute; otherwise, they will be relative to their "
		"root directory."
	)

	parser.add_argument(
		"dirs",
		nargs="*",
		help="One or more directories to scan recursively. Relative paths are treated as being relative to the "
		"directory which holds the library config file. If no paths are specified, the configured DJ directory is used."
	)

	return parser.parse_args()

def loadConfig():
	return config.Config(os.path.join(SCRIPT_DIR, "config.json"))

def computePaths(configFile:config.Config, paths:list):
	outPaths = []

	for path in paths:
		if os.path.isabs(path):
			outPaths.append(path)
		else:
			outPaths.append(os.path.join(configFile.getBaseDirPath(), path))

	return outPaths

def addResult(results:dict, key:str, value:str):
	if key not in results:
		results[key] = [value]
	else:
		results[key].append(value)

def main():
	args = parseArgs()

	configFile = loadConfig()
	paths = computePaths(configFile, args.dirs) if args.dirs else [configFile.getDJDirPath()]

	filesToProcess = {}

	for inputPath in paths:
		print("Checking:", inputPath)

		if not os.path.isdir(inputPath):
			continue

		for root, dirs, files in os.walk(inputPath):
			for file in files:
				if not os.path.splitext(file)[1] in validation.ALL_MEDIA_FORMATS:
					continue

				fileAbsPath = os.path.realpath(os.path.join(root, file))
				filesToProcess[fileAbsPath] = os.path.relpath(fileAbsPath, inputPath)

	print(f"Found {len(filesToProcess)} files to validate")

	if not filesToProcess:
		sys.exit(0)

	results = {}

	for fileKey in filesToProcess:
		filePath = fileKey if args.absolute_paths else filesToProcess[fileKey]
		validationErrors = validation.validateFile(fileKey)

		for error in validationErrors:
			addResult(results, error, filePath)

	if not results:
		print("All files validated")
		sys.exit(0)

	print("Results:")

	for key in results:
		values = results[key]
		print(f"  {key}: {len(values)} files")

		if args.list_files:
			for value in values:
				print(f"    {value}")
			print()

	sys.exit(1)

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
