import os
from . import config

MP3_QUALITY_STD = 320
MP3_QUALITY_DRAFT = 258

def isChildPath(parent:str, child:str) -> bool:
	try:
		return not os.path.relpath(child, parent).startswith("..")
	except ValueError:
		return False

def isDestNewer(sourcePath:str, destPath:str):
	return os.path.getmtime(sourcePath) < os.path.getmtime(destPath)

def indentLines(lines:str, indent:str):
	return indent + (("\n" + indent).join(lines.split("\n")))

def removeFileAndEmptyParentDirs(path:str, limit=None):
	os.unlink(path)
	path = os.path.dirname(path)

	realLimit = os.path.realpath(limit) if limit else None

	while True:
		if not path:
			return

		if realLimit and (not isChildPath(realLimit, path) or realLimit == os.path.realpath(path)):
			return

		if os.listdir(path):
			return

		os.rmdir(path)
		path = os.path.dirname(path)

def fileIsDraft(configFile:config.Config, path:str):
	return isChildPath(configFile.getDraftDirPath(), path)

def parseAllLinesFromFiles(files:list):
	outLines = []

	for path in files:
		with open(path) as inFile:
			for line in inFile.readlines():
				line = line.strip()

				if not line:
					continue

				outLines.append(line)

	return outLines

def convertRelativePathsToAbsolute(root:str, paths:list):
	return [(os.path.abspath(os.path.join(root, path)) if not os.path.isabs(path) else path) for path in paths]
