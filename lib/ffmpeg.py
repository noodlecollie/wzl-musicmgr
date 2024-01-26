import subprocess
import config

def runFFMPEG(configFile:config.Config, args:list):
	ffmpeg = configFile.getFFMPEGOverridePath()
	useShell = not ffmpeg

	args = ["ffmpeg" if useShell else ffmpeg] + args
	return subprocess.run(args, shell=useShell)
