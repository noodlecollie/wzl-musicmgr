import argparse
import os
import shutil
from lib import config, validation, utils, ffmpeg
from lib.transfer_result import *

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

def transferFile(args, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_COPY, sourcePath, destPath)
	result.setTransferError(TRANSFER_ERROR_NONE)

	if os.path.isdir(destPath):
		result.setTransferError(TRANSFER_ERROR_INVALID_DESTINATION)
		result.setTransferErrorReason("Target path already existed as a directory")
		return result

	existed = os.path.isfile(destPath)

	if existed and utils.isDestNewer(sourcePath, destPath):
		result.setTransferError(TRANSFER_ERROR_DEST_FILE_NEWER)
		return result

	try:
		if args.commit:
			shutil.copy(sourcePath, destPath)
	except Exception as ex:
		result.setTransferError(TRANSFER_ERROR_UNHANDLED)
		result.setTransferErrorReason(str(ex))

	result.setReplacedTargetFile(existed)
	return result

def transcodeFile(args, configFile:config.Config, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_TRANSCODE, sourcePath, destPath)
	result.setTransferError(TRANSFER_ERROR_NONE)

	existed = os.path.isfile(destPath)

	if existed and utils.isDestNewer(sourcePath, destPath):
		result.setTransferError(TRANSFER_ERROR_DEST_FILE_NEWER)
		return result

	if args.commit:
		try:
			os.makedirs(os.path.dirname(destPath), exist_ok=True)
			transcodeResult = ffmpeg.to320kMP3(configFile, sourcePath, destPath)
		except Exception as ex:
			result.setTransferError(TRANSFER_ERROR_TRANSCODING_FAILED)
			result.setTransferErrorReason(str(ex))
			return result

		if transcodeResult.returncode != 0:
			result.setTransferError(TRANSFER_ERROR_TRANSCODING_FAILED)
			result.setTransferErrorReason(f"Transcode operation returned error code {transcodeResult.returncode}")
			return result

	result.setReplacedTargetFile(existed)
	return result

def processFile(args, configFile:config.Config, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_UNKNOWN, sourcePath, destPath)

	try:
		validationErrors = validation.validateFile(sourcePath)

		if not validationErrors:
			result = transferFile(args, sourcePath, destPath)
		elif validationErrors == [validation.NOT_AN_MP3]:
			result = transcodeFile(args, configFile, sourcePath, os.path.splitext(destPath)[0] + ".mp3")
		else:
			result.setTransferError(TRANSFER_ERROR_VALIDATION_FAILED)
			result.setTransferErrorReason("; ".join(validationErrors))
	except Exception as ex:
		result.setTransferError(TRANSFER_ERROR_UNHANDLED)
		result.setTransferErrorReason(f"An exception was encountered: {ex}")

	return result

def addToResults(success:dict, failure:dict, result:TransferResult):
	error = result.getTransferError()
	category = "Unknown error"

	if error == TRANSFER_ERROR_NONE:
		target = success

		if result.getTransferType() == TRANSFER_TYPE_TRANSCODE:
			category = "Transcoded (overwritten)" if result.getReplacedTargetFile() else "Transcoded"
		else:
			category = "Overwritten" if result.getReplacedTargetFile() else "Copied"
	else:
		target = failure
		category = error

	if category not in target:
		target[category] = []

	target[category].append(result)

def printSuccessfulResult(result:TransferResult):
	sourcePath = result.getSourcePath()
	destPath = result.getDestPath()
	print(f"  {sourcePath}")
	print(f"    ---> {destPath}")

def printUnsuccessfulResult(result:TransferResult):
	sourcePath = result.getSourcePath()
	print(f"  {sourcePath}")

	reason = result.getTransferErrorReason()

	if reason:
		print(f"    {reason}")

def printResults(results:dict):
	for category in results:
		resultsInCategory = results[category]
		print(f"{category}: {len(resultsInCategory)} files")

		for result in resultsInCategory:
			if result.getSuccessful():
				printSuccessfulResult(result)
			else:
				printUnsuccessfulResult(result)

		print()

def main():
	args = parseArgs()
	configFile = loadConfig()

	if not args.input_root:
		args.input_root = configFile.getPersonalDirPath()

	if not args.output_root:
		args.output_root = configFile.getDJDirPath()

	paths = prunePathsOutsideRoot(args.input_root, args.files)
	filesInInputRoot = buildTargetFileList(args.input_root, paths, args.recursive)

	successfulTransfers = {}
	failedTransfers = {}

	for file in filesInInputRoot:
		sourcePath = os.path.join(args.input_root, file)
		destPath = os.path.join(args.output_root, file)
		result = processFile(args, configFile, sourcePath, destPath)
		addToResults(successfulTransfers, failedTransfers, result)

	printResults(successfulTransfers)
	printResults(failedTransfers)

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
