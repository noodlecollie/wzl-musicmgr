import os

def isChildPath(parent:str, child:str) -> bool:
	try:
		return not os.path.relpath(child, parent).startswith("..")
	except ValueError:
		return False
