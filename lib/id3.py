try:
	import mutagen.id3 as id3
except ModuleNotFoundError:
	print("Mutagen was not found - run `python3 -m pip install mutagen`")
	raise

def dump_tag_string_dict(filePath:str) -> dict:
	file = id3.ID3(filePath)

	outDict = {}

	for key in file:
		value = file[key]
		outDict[key] = "<binary data>" if type(value) is id3.APIC else str(value)

	return outDict
