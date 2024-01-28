TRANSFER_TYPE_UNKNOWN = "Unknown"
TRANSFER_TYPE_COPY = "Copy"
TRANSFER_TYPE_TRANSCODE = "Transcode"

TRANSFER_ERROR_NONE = "No error"
TRANSFER_ERROR_UNHANDLED = "Unhandled error"
TRANSFER_ERROR_NOT_STARTED = "Not yet transferred"
TRANSFER_ERROR_TRANSCODING_FAILED = "Transcoding failed"
TRANSFER_ERROR_INVALID_DESTINATION = "Invalid destination"
TRANSFER_ERROR_VALIDATION_FAILED = "Validation failed"
TRANSFER_ERROR_DEST_FILE_EXISTED = "Destination file already existed"

class TransferResult():
	def __init__(self, transferType:str, sourcePath:str, destPath:str):
		self.__sourcePath = sourcePath
		self.__destPath = destPath
		self.__transferType = transferType
		self.__transferError = TRANSFER_ERROR_NOT_STARTED
		self.__transferErrorReason = ""
		self.__replacedTargetFile = False

	def getSourcePath(self) -> str:
		return self.__sourcePath

	def getDestPath(self) -> str:
		return self.__destPath

	def setDestPath(self, destPath:str):
		self.__destPath = destPath

	def getTransferType(self) -> str:
		return self.__transferType

	def setTransferType(self, transferType:str):
		self.__transferType = transferType

	def getTransferError(self) -> str:
		return self.__transferError

	def setTransferError(self, transferError:str):
		self.__transferError = transferError

	def getTransferErrorReason(self) -> str:
		return self.__transferErrorReason

	def setTransferErrorReason(self, reason:str):
		self.__transferErrorReason = reason

	def getReplacedTargetFile(self) -> bool:
		return self.__replacedTargetFile

	def setReplacedTargetFile(self, replaced:bool):
		self.__replacedTargetFile = replaced

	def getSuccessful(self):
		return self.__transferError == TRANSFER_ERROR_NONE
