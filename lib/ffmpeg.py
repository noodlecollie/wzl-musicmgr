import subprocess
from . import config

# TODO: Upgrade this to use the python-ffmpeg package
def runFFMPEG(configFile:config.Config, args:list):
	ffmpeg = configFile.getFFMPEGOverridePath()
	useShell = not ffmpeg

	args = ["ffmpeg" if useShell else ffmpeg] + args
	return subprocess.run(args, shell=useShell)

def to320kMP3(configFile:config.Config, inputFile:str, outputFile:str):
	return runFFMPEG(configFile, [
		"-i", inputFile,
		"-ab", "320k",
		"-map_metadata", "0",
		"-id3v2_version", "3",
		outputFile,
		"-nostdin"
	])
