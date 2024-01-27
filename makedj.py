import argparse
import os
import shutil
from lib import config, validation, utils, ffmpeg

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))

CATEGORY_TRANSFER_FAILED = "Transfer failed"
CATEGORY_TRANSCODE_FAILED = "Transcoding failed"
CATEGORY_COPY_FILE = "Copied"
CATEGORY_REPLACE_FILE = "Replaced"

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

	parser.add_argument(
		"--commit",
		action="store_true",
		help="Commits to transferring the discovered files. If not specified, file operations are printed but not "
		"performed, so that the results of running the command can be inspected."
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

def transferFile(args, sourcePath:str, destPath:str):
	if os.path.isdir(destPath):
		return (CATEGORY_TRANSFER_FAILED, None)
	elif os.path.isfile(destPath):
		if args.commit:
			shutil.copy(sourcePath, destPath)
		return (CATEGORY_REPLACE_FILE, destPath)
	else:
		if args.commit:
			shutil.copy(sourcePath, destPath)
		return (CATEGORY_COPY_FILE, destPath)

def transcodeFile(args, configFile:config.Config, sourcePath:str, destPath:str):
	try:
		existed = os.path.isfile(destPath)

		if args.commit:
			result = ffmpeg.to320kMP3(config, sourcePath, destPath)

			if result.returncode != 0:
				return (CATEGORY_TRANSCODE_FAILED, None)

		return (CATEGORY_REPLACE_FILE if existed else CATEGORY_COPY_FILE, destPath)
	except Exception:
		return (CATEGORY_TRANSCODE_FAILED, None)

def processFile(args, configFile:config.Config, sourcePath:str, destPath:str):
	try:
		validationErrors = validation.validateFile(sourcePath)

		if not validationErrors:
			return transferFile(args, sourcePath, destPath)

		if validationErrors == [validation.NOT_AN_MP3]:
			return transcodeFile(args, config, sourcePath, os.path.splitext(destPath)[0] + ".mp3")
	except Exception:
		pass

	return (CATEGORY_TRANSFER_FAILED, None)

def addToResults(results:dict, category:str, sourcePath:str, resultPath:str):
	if category not in results:
		results[category] = []

	if category == CATEGORY_COPY_FILE or category == CATEGORY_REPLACE_FILE:
		results[category].append((sourcePath, resultPath))
	else:
		results[category].append(sourcePath)

def main():
	args = parseArgs()
	configFile = loadConfig()

	if not args.input_root:
		args.input_root = configFile.getPersonalDirPath()

	if not args.output_root:
		args.output_root = configFile.getDJDirPath()

	paths = prunePathsOutsideRoot(args.input_root, args.files)
	filesInInputRoot = buildTargetFileList(args.input_root, args.files, args.recursive)

	results = {}

	for file in filesInInputRoot:
		sourcePath = os.path.join(args.input_root, file)
		destPath = os.path.join(args.output_root, file)
		category, resultPath = processFile(args, configFile, sourcePath, destPath)
		addToResults(results, category, sourcePath, resultPath)

	for category in results:
		filesInCategory = results[category]
		print(f"{category}: {len(filesInCategory)} files")

		for file in filesInCategory:
			if type(file) is tuple:
				link = " --> " if os.path.splitext(file[0])[1] == os.path.splitext(file[1])[1] else " ==> "
				print(f"  {link.join(file)}")
			else:
				print(f"  {file}")

		print()

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
