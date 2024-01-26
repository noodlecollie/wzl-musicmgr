import argparse
import os
from lib import config, validation, utils

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))

def parseArgs():
	parser = argparse.ArgumentParser(
		"makedj",
		description="Batch converts tracks to CDJ-applicable formats."
	)

	parser.add_argument(
		"files",
		nargs="+",
		help="Files or folders to convert."
	)

	parser.add_argument(
		"-i",
		"--input-root",
		help="Root directory for input files. Defaults to the configured Personal directory."
	)
	parser.add_argument(
		"-o",
		"--output-root",
		help="Root directory for output files. Defaults to the configured DJ directory."
	)

	parser.add_argument(
		"-r",
		"--recursive",
		action="store_true",
		help="If set, any folders provided will be searched recursively."
	)

	return parser.parse_args()

def loadConfig():
	return config.Config(os.path.join(SCRIPT_DIR, "config.json"))

def prunePathsOutsideRoot(root:str, paths:list):
	outPaths = []

	for path in paths:
		if not os.path.isabs(path):
			outPaths.append(path)
			continue

		relPath = os.path.relpath(path, root)

		if utils.isChildPath(root, path):
			outPaths.append(relPath)
			continue

		print(f"Ignoring {path} which is not a child of the input root directory.")

	return outPaths

def fileTypeIsSupported(path:str):
	return os.path.splitext(path)[1] in validation.ALL_MEDIA_FORMATS and not os.path.basename(path).startswith(".")

def findFilesInDirectory(absPath:str):
	if os.path.isfile(absPath):
		return [absPath]

	outFiles = []

	if os.path.isdir(absPath):
		for contents in os.listdir(absPath):
			fullPath = os.path.join(absPath, contents)

			if os.path.isfile(fullPath) and fileTypeIsSupported(contents):
				outFiles.append(fullPath)

	return outFiles

def findFilesResursively(absPath: str):
	if os.path.isfile(absPath):
		return [absPath]

	outFiles = []

	if os.path.isdir(absPath):
		for root, dirs, files in os.walk(absPath):
			for file in files:
				if fileTypeIsSupported(file):
					outFiles.append(os.path.join(root, file))

	return outFiles

def buildTargetFileList(root:str, paths:list, recursive:bool):
	filePaths = {}

	for path in paths:
		absPath = path if os.path.isabs(path) else os.path.abspath(os.path.join(root, path))

		if not os.path.isfile(absPath) and not os.path.isdir(absPath):
			print(f"Ignoring {path} which does not correspond to a file or directory.")

		if recursive:
			resolvedPaths = findFilesResursively(absPath)
		else:
			resolvedPaths = findFilesInDirectory(absPath)

		for resolvedPath in resolvedPaths:
			filePaths[os.path.relpath(resolvedPath, root)] = True

	return list(filePaths.keys())

def main():
	args = parseArgs()
	configFile = loadConfig()

	if not args.input_root:
		args.input_root = configFile.getPersonalDirPath()

	if not args.output_root:
		args.output_root = configFile.getDJDirPath()

	paths = prunePathsOutsideRoot(args.input_root, args.files)
	filesInInputRoot = buildTargetFileList(args.input_root, args.files, args.recursive)

	# TODO: Continue from here

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
