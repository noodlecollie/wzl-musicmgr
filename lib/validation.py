import os
from . import id3

try:
	from mutagen import id3 as mutID3, mp3, File
except ModuleNotFoundError:
	print("Mutagen was not found - run `python3 -m pip install mutagen`")
	raise

MEDIA_FORMAT_LOSSLESS = [
	".flac",
	".wav",
	".alac"
]

MEDIA_FORMAT_ALLOWED = MEDIA_FORMAT_LOSSLESS + [".mp3"]

ALL_MEDIA_FORMATS = MEDIA_FORMAT_ALLOWED + [
	".ogg",
	".wma",
	".m4a",
	".aiff"
]

DOES_NOT_EXIST = "File does not exist"
NOT_AN_MP3 = "Not an MP3"
UNSUPPORTED_FORMAT = "Unsupported file format"
OVER_TEN_MINUTES_LONG = "Over 10 minutes long"
MP3_LESS_THAN_320K = "MP3 bitrate less than 320k"
MISSING_BASIC_METADATA = "Missing basic metadata"
INVALID_METADATA_CHARACTERS = "Invalid metadata characters"
INVALID_DATA = "File data was not valid"
UNEXPECTED_ERROR = "Unexpected error during validation"

BASIC_METADATA_FRAMES = {
	"TALB": "Album title",
	"TPE1": "Artist",
	"TIT2": "Track title"
}

def __fileIsMissingBasicTags(tags:dict) -> bool:
	minTags = set(BASIC_METADATA_FRAMES.keys())
	return bool(set(minTags - set(tags)))

def __anyTagsHaveNonPrintableCharacters(tags:dict):
	for key in BASIC_METADATA_FRAMES.keys():
		if key in tags and not tags[key].isprintable():
			return True

	return False

def __performChecksOnFileContents(filePath:str, extension:str) -> list:
	validationErrors = []

	if extension in MEDIA_FORMAT_ALLOWED:
		if File(filePath).info.length > 10 * 60:
			validationErrors.append(OVER_TEN_MINUTES_LONG)

	if extension == ".mp3":
		if mp3.MP3(filePath).info.bitrate < 320000:
			validationErrors.append(MP3_LESS_THAN_320K)

		# TODO: Do this for all supported files, not just MP3s?
		tagDict = id3.dump_tag_string_dict(filePath)

		if __fileIsMissingBasicTags(tagDict):
			validationErrors.append(MISSING_BASIC_METADATA)

		if __anyTagsHaveNonPrintableCharacters(tagDict):
			validationErrors.append(INVALID_METADATA_CHARACTERS)

	return validationErrors

def validateFile(filePath:str, logExceptions=True) -> list:
	validationErrors = []

	# Catch exceptions so that we don't crash an entire script
	# mid way through
	try:
		exists = os.path.isfile(filePath)

		extension = os.path.splitext(filePath)[1].lower()

		if extension not in MEDIA_FORMAT_ALLOWED:
			validationErrors.append(UNSUPPORTED_FORMAT)

		if extension != ".mp3":
			validationErrors.append(NOT_AN_MP3)

		if not exists:
			validationErrors.append(DOES_NOT_EXIST)

			# Checks below all require the file to exist,
			# so quit here if it does not.
			return validationErrors

		validationErrors += __performChecksOnFileContents(filePath, extension)

	except mutID3.ID3NoHeaderError:
		validationErrors.append(INVALID_DATA)
	except Exception as ex:
		if logExceptions:
			print(f'validate_file(): Unexpected exception when validating "{filePath}": {ex}')

		validationErrors.append(UNEXPECTED_ERROR)

	return validationErrors
