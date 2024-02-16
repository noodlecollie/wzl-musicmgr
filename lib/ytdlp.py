import subprocess
import re
from . import config

RE_VIDEO_ID_ONLY = re.compile(r"^\w+$", re.ASCII)
RE_STANDARD_YOUTUBE_URL = re.compile(r"^(https://|www\.|https://www\.)youtube\.com/watch\?v=", re.ASCII)
RE_YOUTU_BE_SHORT_URL = re.compile(r"^(https://)?youtu\.be/", re.ASCII)
RE_VIDEO_ID_SEGMENT = re.compile(r"(\w+)(&|$)", re.ASCII)

RE_AUDIO_NAME_FROM_TRANSCODE = re.compile(r"^\[ExtractAudio\] Destination: (.+)$", re.MULTILINE)
RE_FILE_EXISTED = re.compile(r"^\[ExtractAudio\] Not converting audio (.+); file is already in target format", re.MULTILINE)

def runYTDLP(configFile:config.Config, args:list):
	ytdlp = configFile.getYTDLPOverridePath()
	args = [ytdlp if ytdlp else "yt-dlp"] + args
	return subprocess.run(args, shell=False, capture_output=True, text=True)

def downloadYouTubeVideo(configFile:config.Config, videoID:str, outputDir:str, quality:int=320):
	return runYTDLP(configFile, [
		"--no-overwrites",
		"--format", "bestaudio",
		"--extract-audio",
		"--audio-format", "mp3",
		"--audio-quality", f"{quality}K",
		"--paths", outputDir,
		"--output", r"%(title)s.%(ext)s",
		f"https://www.youtube.com/watch?v={videoID}"
	])

def extractVideoIDFromURL(url:str):
	if RE_VIDEO_ID_ONLY.match(url):
		# Definitely in video ID format, so just return it.
		return url

	prefixMatch = RE_STANDARD_YOUTUBE_URL.match(url)

	if not prefixMatch:
		prefixMatch = RE_YOUTU_BE_SHORT_URL.match(url)

	if prefixMatch:
		# The video ID will be straight after the prefix.
		idMatch = RE_VIDEO_ID_SEGMENT.match(url, prefixMatch.end())

		if idMatch:
			return idMatch.group(1)

		raise ValueError(f"Could not infer video ID from YouTube URL \"{url}\"")

	raise ValueError(f"Could not recognise YouTube URL \"{url}\"")

def extractAudioNameFromResult(result:subprocess.CompletedProcess):
	try:
		transcodeResult = RE_AUDIO_NAME_FROM_TRANSCODE.search(result.stdout)
	except Exception:
		transcodeResult = None

	if not transcodeResult:
		raise ValueError("Could not parse extracted audio file name from subprocess result")

	return transcodeResult.group(1)

def fileAlreadyExistedOnDisk(result:subprocess.CompletedProcess):
	match = RE_FILE_EXISTED.search(result.stdout)
	return (bool(match), match.group(1) if match else None)
