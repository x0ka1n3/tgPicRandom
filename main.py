import VKFuncs as vk
import glob
import time
import requests
import json

token = "" #Токен бота ТГ

sent = json.load(open("sent.json", "r"))
chat_id = 0

if __name__ == '__main__':
	for i in vk.GROUPSDATA:
		vk.offset = 0
		vk.wall = []
		vk.entered_id = 0
		vk.picNum = 0
		vk.downPicCount = 0
		
		print(i.split("/")[-1])
		vk.entered_id = i.split("/")[-1]
		vk.halfMain()
		print("\nDone!\n")
		time.sleep(3)

	files = glob.glob("content/*")

	for i in range(len(files)):
		files[i] = files[i][8:]


	for i in files:
		if i not in sent["sent"]:
			sent["sent"].append(i)
			json.dump(sent, open("sent.json", "w"), ensure_ascii = False, indent = 4)
			while True:
				R = requests.post(f"https://api.telegram.org/bot{token}/sendPhoto", data = {"chat_id":chat_id}, files = {"photo":open(f"./content/{i}", "rb").read()}).json()
				if "error_code" in R and R["error_code"] == 429 and "parameters" in R:
					time.sleep(int(R["parameters"]["retry_after"]))
				else:
					break
			time.sleep(1)
			

		vk.progressBar(files.index(i)+1, len(files), title = "Sending pics...")