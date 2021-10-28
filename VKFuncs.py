import vk, json, time, sys, requests, os

v = 5.21
offset = 0
wall = []
entered_id = 0
picNum = 0
access_token = ""
downPicCount = 0
userBool = 0

js = json.load(open("dataVK.json", "r"))
access_token = js["token"]
GROUPSDATA = js["groups"]

api = vk.API(vk.Session(access_token = access_token))

postId = 0
nomedia = 0

def progressBar(done, length, barLen = 20, title = ""):
	barFillNum = int(round(barLen*done/float(length)))
	barFill = barFillNum*"*"
	barRemain = (barLen - barFillNum)*"-"

	if len(title):
		title = "| " + title

	bar = barFill+barRemain
	barPerc = round((done/length)*100)
	sys.stdout.write("\r[%s] %d%s | %d/%d %s" % (bar, barPerc, "%", done, length, title))
	sys.stdout.flush()

def getId(id = entered_id):
	global entered_id
	entered_id = -1*int(api.groups.getById(group_id = entered_id, v = v)[0]["id"])

def getWall(owner_id = entered_id):
	global offset
	global wall
	count = int(round(int(api.wall.get(owner_id = entered_id, v = v)["count"])/2500+0.5))
	Try = 1
	while Try <= count:
		try:

			code = 'var offset = '+str(offset)+'; var wallArr = []; var i = 0; while(i<25){wallArr.push(API.wall.get({"owner_id":"'+str(entered_id)+'", "v":"'+str(v)+'", "count":100, "offset":offset})); i=i%2B1; offset = offset%2B100;}; return [wallArr, offset];'
			response = requests.get("https://api.vk.com/method/execute?v={1}&access_token={0}&code=".format(access_token, v)+code, timeout = 100).json()["response"]
			progressBar(Try, count, title = "Parsing wall")
			offset = response[1]
			wall.append(response[0])
			if Try % 3 == 0:
				time.sleep(1.3)
			Try+=1
		except:
			pass

	print("\nOk!\n")
	wallJson = []
	for arr in wall[:]:
		for response in arr[:]:
			if response["items"] != []:				
				for item in response["items"][:]:
					for key in list(item):
						if key != "id" and key != "attachments":
							item.pop(key, None)
					if "attachments" in item:				
						for attach in item["attachments"][:]:
							if attach["type"] != "photo":
								item["attachments"].remove(attach)
							else:
								if "photo" in attach:
									sizesArr = []
									for key in list(attach["photo"]):
										try:
											if key.split("_")[0] == "photo":
												sizesArr.append(int(key.split("_")[1]))
										except:
											pass
									max_size = max(sizesArr)
								wallJson.append({"id":item["id"], "url":attach["photo"]["photo_"+str(max_size)]})
	global picNum
	picNum = len(wallJson)
	if not userBool:
		toBeWritten = {"entered_info":{"id":entered_id, "name":api.groups.getById(group_id = -1*entered_id, v = v)[0]["name"], "picNum":picNum}, "wall":wallJson}
	else:
		user = api.users.get(user_ids = entered_id, v = v)
		toBeWritten = {"entered_info":{"id":entered_id, "name":user[0]["first_name"]+" "+user[0]["last_name"], "picNum":picNum}, "wall":wallJson}
	json.dump(toBeWritten, open("wall.json", "w"), ensure_ascii = False, indent = 10)


def downloadManager():
	global postId
	global downPicCount
	data = json.load(open("wall.json", "r"))
	picProcess = 1
	entered_info = data["entered_info"]
	grName = entered_info["name"].replace("/", "?")
	if not len(data["wall"]):
		print("No photos found")
	else:
		for item in data["wall"]:
			if int(postId) != 0:
				postId = item["id"]
			downloadPhoto(item["url"], item["url"].split("/")[-1], os.path.abspath(os.path.dirname(sys.argv[0])), postId, grName)
			if nomedia:
				open("{0}/{1}/.nomedia".format(os.path.abspath(os.path.dirname(sys.argv[0])), grName), "w")
			if downPicCount:
				progressBar(picProcess, entered_info["picNum"], title = "Donwloading photos...")
			else:
				progressBar(picProcess, entered_info["picNum"], title = "Checking photos...")
			picProcess+=1

def downloadPhoto(url, fn, fp, iD = 0, grName = ""):
	global downPicCount
	data = json.load(open("wall.json", "r"))
	entered_info = data["entered_info"]

	absPath = str(fp)+f"/content/{str(fn)}"

	if not os.path.exists(absPath) or int(os.path.getsize(absPath)) == 0:
		with open(absPath, "wb") as image:
			downPicCount = 1
			image.write(requests.get(url).content)

def halfMain():
		getId()
		getWall()
		downloadManager()


