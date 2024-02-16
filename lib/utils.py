import os

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
