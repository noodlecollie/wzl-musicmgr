import mutagen.id3 as id3

FRAME_TRACK_TITLE = "TIT2"

def dump_tag_string_dict(filePath:str) -> dict:
	file = id3.ID3(filePath)

	outDict = {}

	for key in file:
		value = file[key]
		outDict[key] = "<binary data>" if type(value) is id3.APIC else str(value)

	return outDict
