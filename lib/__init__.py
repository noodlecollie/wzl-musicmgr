def __ensureInstalled(pkg:str, minVersion:str):
	from pkg_resources import WorkingSet , DistributionNotFound

	try:
		WorkingSet().require(pkg)
	except DistributionNotFound:
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print(f"Dependency {pkg} {minVersion} was not found - run `python3 -m pip install {pkg}`")
		print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		print()
		raise

__ensureInstalled("mutagen", "1.47.0")
__ensureInstalled("python-ffmpeg", "2.0.10")
