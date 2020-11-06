import vk_api
import requests
import sys
from time import sleep
from mutagen.mp3 import MP3

class Bot():
	HELP = """
	use: python3 main.py <access token> <login/id> <file name/path>
	"""

	secs = None
	to_user = None
	file_names = None
	vk = None
	audio_bytes = None

	def __init__(self, access_token, to_user, file_names):
		self.to_user = to_user
		self.file_names = file_names

		self.vk = vk_api.VkApi(token=access_token)
		self.vk.get_api()
		return

	def getAudioInfo(self, file_name):
		self.secs = MP3(file_name).info.length
		with open(file_name, "rb") as file:
			self.audio_bytes = file.read()
		return

	def getUserID(self, to_user):
		return self.vk.method("users.get", {"user_ids": to_user})[0]["id"]

	def getUploadServer(self, to_user):
		return self.vk.method("docs.getMessagesUploadServer", {"type": "audio_message", "peer_id": f"{to_user}"})["upload_url"]

	def uploadAudio(self, uploadURL, audio_bytes):
		return requests.post(uploadURL, files={"file": audio_bytes}).json()

	def saveAudio(self, uploadedFileResponse):
		return self.vk.method("docs.save", {"file": uploadedFileResponse["file"]})["audio_message"]

	def sendMessage(self, savedAudio, to_user):
		attachment = f"doc{str(savedAudio['owner_id'])}_{str(savedAudio['id'])}"
		self.vk.method("messages.send", {"peer_id": f"{to_user}", "attachment": attachment, "random_id": vk_api.utils.get_random_id()})
		return

	def setActivity(self, to_user):
		self.vk.method("messages.setActivity", {"peer_id": to_user, "type": "audiomessage"})
		return

	def do(self):
		for audio_file in self.file_names:
			self.getAudioInfo(audio_file)
			self.to_user = self.getUserID(self.to_user)
			self.setActivity(self.to_user)
			sleep(int(self.secs))
			uploadURL = self.getUploadServer(self.to_user)
			uploadedFileResponse = self.uploadAudio(uploadURL, self.audio_bytes)
			savedAudio = self.saveAudio(uploadedFileResponse)
			self.sendMessage(savedAudio, self.to_user)
		return



if __name__ == "__main__":
	file_names = []
	if (len(sys.argv)) == 1 or len(sys.argv) < 4:
		print(Bot.HELP)
		access_token = input("TOKEN: ")
		to_user = input("TO USER: ")
		file_names.append(input("FILENAME: "))
	else:
		access_token = sys.argv[1]
		to_user = sys.argv[2]
		for arg in sys.argv[3::]:
			file_names.append(arg)
	bot = Bot(access_token, to_user, file_names)
	try:
		bot.do()
	except Exception as e:
		print(e)
		pass
