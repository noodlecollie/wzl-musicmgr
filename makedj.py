import argparse
import os
import shutil
import traceback
from lib import config, validation, utils, ffmpeg, id3
from lib.transfer_result import *
from mutagen import id3 as mutID3

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

	parser.add_argument(
		"--allow-overwrite",
		action="store_true",
		help="If set, allows overwriting destination files when copying or transcoding."
	)

	parser.add_argument(
		"--allow-low-bitrate",
		action="store_true",
		help="If set, allows copying MP3s with a bitrate < 320K."
	)

	parser.add_argument(
		"--allow-missing-metadata",
		action="store_true",
		help="If set, allows copying/transcoding MP3s with missing metadata."
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

def getExcludedFiles(dirPath:str):
	if os.path.isfile(dirPath):
		return []

	try:
		with open(os.path.join(dirPath, ".exclude"), "r") as inFile:
			return [line.strip() for line in inFile.readlines()]
	except Exception:
		return []

def findFilesInDirectory(absPath:str):
	if os.path.isfile(absPath):
		return [absPath]

	excludedFiles = getExcludedFiles(absPath)
	outFiles = []

	if os.path.isdir(absPath):
		for contents in os.listdir(absPath):
			fullPath = os.path.join(absPath, contents)

			if os.path.isfile(fullPath) and fileTypeIsSupported(contents) and contents not in excludedFiles:
				outFiles.append(fullPath)

	return outFiles

def findFilesResursively(absPath: str):
	if os.path.isfile(absPath):
		return [absPath]

	outFiles = []

	if os.path.isdir(absPath):
		for root, dirs, files in os.walk(absPath):
			excludedFiles = getExcludedFiles(root)

			for file in files:
				if fileTypeIsSupported(file) and file not in excludedFiles:
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

def validateFile(args, configFile:config.Config, path:str, sourcePath:str=None):
	validationErrors = validation.validateFile(path)

	if utils.fileIsDraft(configFile, sourcePath if sourcePath is not None else path):
		# File is a draft, so restrictions are more lax.
		restrictionsToRemove = set([
			validation.MISSING_BASIC_METADATA,
			validation.MP3_LESS_THAN_320K
		])

		validationErrors = list(set(validationErrors) - restrictionsToRemove)

	if args.allow_low_bitrate:
		validationErrors = list(set(validationErrors) - set([validation.MP3_LESS_THAN_320K]))

	if args.allow_missing_metadata:
		validationErrors = list(set(validationErrors) - set([validation.MISSING_BASIC_METADATA]))

	return validationErrors

def performPostTransferFixups(configFile:config.Config, sourcePath:str, destPath:str):
	if utils.fileIsDraft(configFile, sourcePath):
		id3tags = mutID3.ID3(destPath)

		if id3.FRAME_TRACK_TITLE in id3tags:
			title = id3tags[id3.FRAME_TRACK_TITLE]
		else:
			title = os.path.splitext(os.path.basename(sourcePath))[0]

		id3tags.delall(id3.FRAME_TRACK_TITLE)
		id3tags.add(mutID3.TIT2(encoding=3, text=f"DRAFT {title}"))
		id3tags.save()

def transferFile(args, configFile, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_COPY, sourcePath, destPath)
	result.setTransferError(TRANSFER_ERROR_NONE)

	if os.path.isdir(destPath):
		result.setTransferError(TRANSFER_ERROR_INVALID_DESTINATION)
		result.setTransferErrorReason("Target path already existed as a directory")
		return result

	existed = os.path.isfile(destPath)

	if existed:
		if args.allow_overwrite:
			if args.commit:
				os.unlink(destPath)
		else:
			result.setTransferError(TRANSFER_ERROR_DEST_FILE_EXISTED)
			return result

	try:
		if args.commit:
			os.makedirs(os.path.dirname(destPath), exist_ok=True)
			shutil.copy(sourcePath, destPath)
			performPostTransferFixups(configFile, sourcePath, destPath)
	except Exception:
		result.setTransferError(TRANSFER_ERROR_UNHANDLED)
		result.setTransferErrorReason(traceback.format_exc())

	result.setReplacedTargetFile(existed)
	return result

def transcodeFile(args, configFile:config.Config, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_TRANSCODE, sourcePath, destPath)
	result.setTransferError(TRANSFER_ERROR_NONE)

	existed = os.path.isfile(destPath)

	if existed:
		if args.allow_overwrite:
			if args.commit:
				os.unlink(destPath)
		else:
			result.setTransferError(TRANSFER_ERROR_DEST_FILE_EXISTED)
			return result

	validationErrors = []

	if args.commit:
		try:
			os.makedirs(os.path.dirname(destPath), exist_ok=True)
			quality = utils.MP3_QUALITY_DRAFT if utils.fileIsDraft(configFile, sourcePath) else utils.MP3_QUALITY_STD
			transcodeResult = ffmpeg.toMP3(configFile, sourcePath, destPath, quality)
			performPostTransferFixups(configFile, sourcePath, destPath)

			try:
				# Re-validate the MP3 to check that it has the required ID3 tags.
				# It's easier to do this than to write separate tag validation
				# for the different file formats we may encounter before transcoding.
				validationErrors = validateFile(args, configFile, destPath, sourcePath)
			except Exception:
				utils.removeFileAndEmptyParentDirs(destPath, args.output_root)
				raise

			if validationErrors:
					# Don't leave the MP3 lying around.
					utils.removeFileAndEmptyParentDirs(destPath, args.output_root)
		except FileNotFoundError:
			result.setTransferError(TRANSFER_ERROR_TRANSCODING_FAILED)

			result.setTransferErrorReason(
				"Failed to invoke ffmpeg - check the executable is present in the system "
				"path, or set an \"ffmpeg\" override path in config.json"
			)

			return result
		except Exception as ex:
			result.setTransferError(TRANSFER_ERROR_TRANSCODING_FAILED)
			result.setTransferErrorReason(str(ex))
			return result

		if transcodeResult.returncode != 0:
			result.setTransferError(TRANSFER_ERROR_TRANSCODING_FAILED)
			result.setTransferErrorReason(f"Transcode operation returned error code {transcodeResult.returncode}")
			return result

	result.setReplacedTargetFile(existed)

	if validationErrors:
		result.setTransferError(TRANSFER_ERROR_VALIDATION_FAILED_POST_TRANSACODE)
		result.setTransferErrorReason("; ".join(validationErrors))

	return result

def processFile(args, configFile:config.Config, sourcePath:str, destPath:str) -> TransferResult:
	result = TransferResult(TRANSFER_TYPE_UNKNOWN, sourcePath, destPath)

	try:
		validationErrors = validateFile(args, configFile, sourcePath)

		if not validationErrors:
			result = transferFile(args, configFile, sourcePath, destPath)
		elif validationErrors == [validation.NOT_AN_MP3]:
			result = transcodeFile(args, configFile, sourcePath, os.path.splitext(destPath)[0] + ".mp3")
		else:
			result.setTransferError(TRANSFER_ERROR_VALIDATION_FAILED)
			result.setTransferErrorReason("; ".join(validationErrors))
	except Exception:
		result.setTransferError(TRANSFER_ERROR_UNHANDLED)
		result.setTransferErrorReason(f"An exception was encountered: {traceback.format_exc()}")

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
	print(f"    {sourcePath}")
	print(f"      ---> {destPath}")

def printUnsuccessfulResult(result:TransferResult):
	sourcePath = result.getSourcePath()
	print(f"    {sourcePath}")

	reason = result.getTransferErrorReason()

	if reason:
		indentedReason = utils.indentLines(reason, "  ")
		print(f"    {indentedReason}")

def printResults(title:str, results:dict):
	print(f"{title}:")

	if results:
		for category in results:
			resultsInCategory = results[category]
			print(f"  {category}: {len(resultsInCategory)} files")

			for result in resultsInCategory:
				if result.getSuccessful():
					printSuccessfulResult(result)
				else:
					printUnsuccessfulResult(result)

			print()
	else:
		print("  0 files")

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

		if utils.fileIsDraft(configFile, sourcePath):
			destPath = os.path.join(args.output_root, "_Draft", file)
		else:
			destPath = os.path.join(args.output_root, file)

		result = processFile(args, configFile, sourcePath, destPath)
		addToResults(successfulTransfers, failedTransfers, result)

	if not args.commit:
		print("####################################################################")
		print("# Dry run, no operations performed. Prospective results are below. #")
		print("####################################################################")
		print()

	printResults("Successful", successfulTransfers)
	printResults("Failed", failedTransfers)

	if not args.commit:
		print("####################################################################")
		print("# Dry run, no operations performed. Prospective results are above. #")
		print("####################################################################")
		print()

if __name__ != "__main__":
	raise RuntimeError("Expected file to be run as a script")

main()
