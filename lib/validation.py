import os

WELL_SUPPORTED_FORMATS = [
	".mp3",
	".flac",
	".wav",
	".aiff"
]

NOT_AN_MP3 = "Not an MP3"
UNSUPPORTED_FORMAT = "Unsupported file format"

def validateFile(filePath:str):
	validationErrors = []

	extension = os.path.splitext(filePath)[1]

	if extension not in WELL_SUPPORTED_FORMATS:
		validationErrors.append(UNSUPPORTED_FORMAT)

	if extension != ".mp3":
		validationErrors.append(NOT_AN_MP3)

	return validationErrors
