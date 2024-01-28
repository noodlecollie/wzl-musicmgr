import json
import os

class Config:
	def __init__(self, configFilePath:str) -> None:
		self.__baseDirPath:str = os.path.dirname(configFilePath)
		self.__personalDir:str = ""
		self.__djDir:str = ""
		self.__draftDir:str = ""
		self.__ffmpeg = None

		self.__loadJSON(configFilePath)

	def getBaseDirPath(self) -> str:
		return self.__baseDirPath

	def getPersonalDir(self) -> str:
		return self.__personalDir

	def getPersonalDirPath(self) -> str:
		return self.__makePath(self.__personalDir)

	def getDJDir(self) -> str:
		return self.__djDir

	def getDJDirPath(self) -> str:
		return self.__makePath(self.__djDir)

	def getDraftDir(self) -> str:
		return self.__draftDir

	def getDraftDirPath(self) -> str:
		return self.__makePath(self.__draftDir)

	def getFFMPEGOverridePath(self):
		return self.__ffmpeg

	def __makePath(self, path:str):
		return path if os.path.isabs(path) else os.path.join(self.getBaseDirPath(), path)

	def __loadJSON(self, configFilePath:str) -> None:
		with open(configFilePath, "r") as inFile:
			contents = json.load(inFile)

			self.__personalDir = self.__tryRead(contents, "personal", str)
			self.__djDir = self.__tryRead(contents, "dj", str)
			self.__draftDir = self.__tryRead(contents, "draft", str)
			self.__ffmpeg = self.__tryRead(contents, "ffmpeg", str, optional=True)

	def __tryRead(self, jsonObj:dict, prop:str, valueType:type, optional:bool=False):
		if prop not in jsonObj:
			if optional:
				return None

			raise KeyError(f'Config JSON did not contain required property "{prop}"')

		value = jsonObj[prop]

		if type(value) is not valueType:
			raise TypeError(f'Expected config JSON property "{prop}" to be {valueType.__name__}, but provided value was {type(value).__name__}')

		return value
