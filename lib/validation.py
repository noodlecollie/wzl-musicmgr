import os

WELL_SUPPORTED_FORMATS = [
	".mp3",
	".flac",
	".wav",
	".aiff"
]

ALL_MEDIA_FORMATS = WELL_SUPPORTED_FORMATS + [
	".ogg",
	".wma",
	".m4a"
]

DOES_NOT_EXIST = "File does not exist"
NOT_AN_MP3 = "Not an MP3"
UNSUPPORTED_FORMAT = "Unsupported file format"
OVER_TEN_MINUTES_LONG = "Over 10 minutes long"
MP3_LESS_THAN_320K = "MP3 bitrate less than 320k"
MISSING_BASIC_METADATA = "Missing basic metadata"

def validateFile(filePath:str):
	validationErrors = []

	if not os.path.isfile(filePath):
		validationErrors.append(DOES_NOT_EXIST)

	extension = os.path.splitext(filePath)[1]

	if extension not in WELL_SUPPORTED_FORMATS:
		validationErrors.append(UNSUPPORTED_FORMAT)

	if extension != ".mp3":
		validationErrors.append(NOT_AN_MP3)

	return validationErrors
