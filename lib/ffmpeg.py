import subprocess
from . import config

def runFFMPEG(configFile:config.Config, args:list):
	ffmpeg = configFile.getFFMPEGOverridePath()
	args = [ffmpeg if ffmpeg else "ffmpeg"] + args
	return subprocess.run(args, shell=False)

def toMP3(configFile:config.Config, inputFile:str, outputFile:str, quality:int=320):
	return runFFMPEG(configFile, [
		"-i", inputFile,
		"-ab", f"{quality}k",
		"-map_metadata", "0",
		"-id3v2_version", "3",
		outputFile,
		"-nostdin"
	])
