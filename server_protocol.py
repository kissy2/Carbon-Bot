from data import Data
from time import strftime
from pathlib import Path
import pickle
import random
from functools import reduce
import json
import logging
prev=None

with (Path(__file__).parent / "protocol.pk").open("rb") as f:
	types = pickle.load(f)
	msg_from_id = pickle.load(f)
	types_from_id = pickle.load(f)
	primitives = pickle.load(f)
primitives = {
	name: (getattr(Data, "read" + name), getattr(Data, "write" + name))
	for name in primitives
}


useful = {
		  "resources": {},
		  "fight": {},
		  "lifepoints": 100,
		  "maxLifePoints": 100,
		  "my_level": 1,
		  "accountId": None,
		  "contextualId": None,
		  "jobupdated": False,
		  "leveledup": False,
		  'jobs': {},
		  'Harvesting': False,
		  'dialog': False,
		  "map_mobs": {},
		  "map_npc": {},
		  "energy" : 1,
		  "map_merchant": {},
		  "inventory_weight": 0,
		  "inventory_max": 1,
		  "infight": False,
		  "map_players": {},
		  "mypos": None,
		  "mapid": None,
		  "subAreaId": None,
		  "fightCount": None,
		  "full_inventory": False,
		  "backup":False,
		  'threat':None,
		  'name':None,
		  'reset':False,
		  'client_render_time':0,
		  'mount':{},
		  'relog':False,
		  'shortcuts':[],
		  'inventory':{},
		  'ready_to_sell':[],
		  'agro':[],
		  'disconnect':3,
		  'zaap':False,
		  'marketplace':False,
		  'w_l_f':True
		  }

def readVec(var, data):
	assert var["length"] is not None
	if isinstance(var["length"], int):
		n = var["length"]
	else:
		n = read(var["length"], data)
	ans = []
	for _ in range(n):
		ans.append(read(var["type"], data))
	return ans


def readBooleans(boolVars, data):
	ans = {}
	bvars = iter(boolVars)
	for _ in range(0, len(boolVars), 8):
		bits = format(data.readByte(), "08b")[::-1]
		for val, var in zip(bits, bvars):
			# be careful, you have to
			# put bits first in zip
			ans[var["name"]] = val == "1"
	return ans


def addMapComplementaryInformationsDataMessage(ans):
	try:
		logging.info(f'map changed : {ans["mapId"]}')
		useful["resources"] = {}
		useful["map_mobs"] = {}
		useful["map_merchant"] = {}
		useful["map_npc"] = {}
		useful["map_players"] = {}
		useful["mapid"] = ans["mapId"]
		useful["subAreaId"] = ans["subAreaId"]
		tmp={}
		for actor in ans["actors"]:
			if (not useful['contextualId'] or not useful['accountId']) and 'name' in actor and actor['name'] == useful['name']:
				useful['accountId'],useful['contextualId']=actor['accountId'],actor['contextualId']

			elif actor["__type__"] == "GameRolePlayMerchantInformations":
				useful["map_merchant"][actor["contextualId"]] = {}
				useful["map_merchant"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

			elif actor["__type__"] == "GameRolePlayNpcInformations":
				useful["map_npc"][actor["contextualId"]] = {}
				useful["map_npc"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

			elif actor["__type__"] == "GameRolePlayTreasureHintInformations":
				useful["map_npc"][actor["npcId"]] = actor["disposition"]["cellId"]

			elif actor["__type__"] == "GameRolePlayCharacterInformations":
				if actor["contextualId"] == useful["contextualId"]:
					useful["mypos"] = actor["disposition"]["cellId"]
				else:
					if actor["name"] and "["  == actor["name"][0]:
						useful["threat"]="high"
						logging.critical("MODERATOR PRESENCE OF THIS MAP")
					useful["map_players"][actor["contextualId"]] = {"name":actor["name"]}
					useful["map_players"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

			elif actor["__type__"] == "GameRolePlayGroupMonsterInformations":
				# logging.info("Adding mob", actor)
				useful["map_mobs"][actor["contextualId"]] = {}
				useful["map_mobs"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]
				useful["map_mobs"][actor["contextualId"]]["info"] = []
				useful["map_mobs"][actor["contextualId"]]["alllevel"] = int(
					actor["staticInfos"]["mainCreatureLightInfos"]["level"])
				useful["map_mobs"][actor["contextualId"]]["info"].append(
					(actor["staticInfos"]["mainCreatureLightInfos"]["genericId"],
					 actor["staticInfos"]["mainCreatureLightInfos"]["level"]))
				for under in actor["staticInfos"]["underlings"]:
					useful["map_mobs"][actor["contextualId"]]["info"].append((under["genericId"], under["level"]))
					useful["map_mobs"][actor["contextualId"]]["alllevel"] += int(under["level"])

		for elemnt2 in ans["statedElements"]:
			# logging.info("adding element")
			if elemnt2["onCurrentMap"]:
				elmentid = elemnt2["elementId"]
				tmp[elmentid] = {}
				tmp[elmentid]["elementCellId"] = elemnt2["elementCellId"]
				tmp[elmentid]["elementState"] = elemnt2["elementState"]

		useful["client_render_time"]=len(tmp)
		useful['zaap']=False
		useful['marketplace']=False
		for element in ans["interactiveElements"]:
			if element["enabledSkills"]:	
				try:
					elmentid = element["elementId"]
					if elmentid in tmp and tmp[elmentid]["elementCellId"] \
							and element["onCurrentMap"] \
							and element["enabledSkills"][0]["skillId"] != 114:
						useful["resources"][elmentid] = {}
						useful["resources"][elmentid]["elementCellId"] = tmp[elmentid]["elementCellId"]
						useful["resources"][elmentid]["enabledSkill"] = element["enabledSkills"][0]["skillId"]
						useful["resources"][elmentid]["elementTypeId"] = element["elementTypeId"]
						useful["resources"][elmentid]["elementState"] = tmp[elmentid]["elementState"]
						for imap in mapinfo:
							if imap["id"] == ans["mapId"]:
								useful["resources"][elmentid]["offset"] = imap['interactives']['2'][str(elmentid)]["offset"]
					elif element["enabledSkills"][0]["skillId"] == 114 and element["onCurrentMap"]:	useful['zaap']=True
					elif element["enabledSkills"][0]["skillId"] == 355 and element["onCurrentMap"]: useful['marketplace']=str(elmentid)
					elif element["enabledSkills"][0]["skillId"]==211:	useful['phenix_id']=str(elmentid)
				except:
					pass
			
	except:
		logging.error(f'proto error {ans}',exc_info=1)
def addGameMapMovementMessage(ans):
	if ans["actorId"] == useful["contextualId"]:
		useful["mypos"] = ans["keyMovements"][-1]
		if useful["infight"]:
			useful["fight"]["mypos"] = ans["keyMovements"][-1]
	else:
		if ans["actorId"] < 0:
			if useful["infight"]:
				try:
					useful["fight"]["enemyteamMembers"][ans["actorId"]]["cellid"] = ans["keyMovements"][-1]
				except:
					pass
			if useful["infight"] == False:
				try:
					useful["map_mobs"][int(ans["actorId"])]["cellId"] = ans["keyMovements"][-1]
				except:
					useful["map_mobs"][int(ans["actorId"])] = {}
					useful["map_mobs"][int(ans["actorId"])]["cellId"] = ans["keyMovements"][-1]
		else:
			try:
				useful["map_players"][int(ans["actorId"])]["cellId"] = ans["keyMovements"][-1]
			except:
				useful["map_players"][int(ans["actorId"])] = {}
				useful["map_players"][int(ans["actorId"])]["cellId"] = ans["keyMovements"][-1]



# def addObjectQuantityMessage(ans):
#     useful["inventory"][ans['objectUID']] = ans['quantity']


def addInventoryWeightMessage(ans):
	inventory_weight = ans["inventoryWeight"]
	inventory_max = ans["weightMax"]
	useful["inventory_weight"] = inventory_weight
	if inventory_max != 0:
		useful["inventory_max"] = inventory_max


def addGameFightMonsterInformations(ans):
	id = int(ans["contextualId"])
	if ans["spawnInfo"]["alive"]:
		if id not in useful["fight"]["mysummons"]:
			useful["fight"]["enemyteamMembers"][id] = {}
			useful["fight"]["enemyteamMembers"][id]["cellid"] = ans["disposition"]["cellId"]
			for x in ans["stats"]["characteristics"]["characteristics"]:
				if x["characteristicId"]==0:
					useful["fight"]["enemyteamMembers"][id]["lifepoints"]=x["total"]
			# useful["fight"]["enemyteamMembers"][id]["lifepoints"] = ans["stats"]["lifePoints"]
			useful["fight"]["enemyteamMembers"][id]["summoned"] = ans["stats"]["summoned"]
			try:
				useful["fight"]["enemyteamMembers"][id]["level"] = ans["creatureLevel"]
			except:
				pass

def addGameFightCharacterInformations(ans):
	if not useful["contextualId"] and useful['name']==ans['name']:	useful['contextualId']=ans['contextualId']
	id = int(ans["contextualId"])
	if id == useful["contextualId"]:
		useful["mypos"] = ans["disposition"]["cellId"]
		useful["fight"]["mypos"] = useful["mypos"]
		useful["fight"]["my_teamid"] = ans["spawnInfo"]["teamId"]
		useful["my_level"] = ans["level"]
		useful["maxLifePoints"]=0
		for x in ans["stats"]["characteristics"]["characteristics"]:
			if x["characteristicId"]==1:
				useful["fight"]["ap"]=x["base"]+x["objectsAndMountBonus"]
			elif x["characteristicId"]==23:
				useful["fight"]["mp"]=x["base"]+x["objectsAndMountBonus"]
			elif x["characteristicId"]==0 or x["characteristicId"]==11:
				useful["maxLifePoints"]+=x["base"]+x["objectsAndMountBonus"]

	else:
		useful["fight"]["teamMembers"][id]["status"] = ans["status"]["__type__"]
		useful["fight"]["teamMembers"][id]["previousPositions"] = ans["previousPositions"]
		useful["fight"]["teamMembers"][id]["level"] = ans["level"]



def addInteractiveElementUpdatedMessage(ans):
	global resourcetmp
	elemid = ans["interactiveElement"]["elementId"]
	try:
		resourcetmp[elemid]["enabledSkill"] = ans["interactiveElement"]["enabledSkills"][0]["skillId"]
		resourcetmp[elemid]["elementTypeId"] = ans["interactiveElement"]["elementTypeId"]
		for map in mapinfo:
			if map["id"] == useful["mapid"]:
				resourcetmp[elemid]["offset"] = map['interactives']['2'][str(elemid)]["offset"]
	except:
		pass

	if ans["interactiveElement"]["disabledSkills"] or not ans["interactiveElement"]["onCurrentMap"]:
		try:
			del useful["resources"][elemid]
		except:
			pass
	else:
		try:
			useful["resources"][elemid] = resourcetmp[elemid]
		except:
			pass

def addStatedElementUpdatedMessage(ans):
	global resourcetmp
	resourcetmp = {}
	elemid = ans["statedElement"]["elementId"]
	resourcetmp[elemid] = {}
	resourcetmp[elemid]["elementCellId"] = ans["statedElement"]["elementCellId"]
	resourcetmp[elemid]["elementState"] = ans["statedElement"]["elementState"]

def read(type, data: Data):
	try:
		global prev
		try:
			if type is None:
				return
			if type is False:
				type = types_from_id[data.readUnsignedShort()]
			elif isinstance(type, str):
				if type in primitives:
					return primitives[type][0](data)
				type = types[type]
			if type["parent"] is not None:
				ans = read(type["parent"], data)
				ans["__type__"] = type["name"]
			else:
				ans = dict(__type__=type["name"])
			ans.update(readBooleans(type["boolVars"], data))
			for var in type["vars"]:
				if var["optional"]:
					if not data.readByte():
						continue
				if var["length"] is not None:
					ans[var["name"]] = readVec(var, data)
				else:
					ans[var["name"]] = read(var["type"], data)

			if type["hash_function"] and data.remaining() == 48:
				ans["hash_function"] = data.read(48)
		except:
			useful['reset']=True
			return {}

		# logging.info(f' {ans}')



		if ans["__type__"] == "GameFightOptionStateUpdateMessage":
			if useful["infight"] == ans["fightId"]:
				if ans['option'] == 0:
					useful['fight']['spectator']=ans['state']
				elif ans['option'] == 2:
					useful['fight']['lock']=ans['state']

		elif ans["__type__"] == "ShortcutBarContentMessage":
			if ans['barType'] == 0:
				useful['shortcuts'] = [(x['slot']+1)%10 for x in ans['shortcuts'] if x['slot']<10 and x['itemUID']]
			# elif ans['barType'] == 1:
			# 	useful['spells'] = {x['spellId']:x['slot'] for x in ans['shortcuts']}

		elif ans["__type__"] == "ShortcutBarRefreshMessage":
			if ans['barType'] == 0 and ans['shortcut']['slot']<10:
				calc=(ans['shortcut']['slot']+1)%10
				if ans['shortcut']['itemUID'] and calc not in useful['shortcuts']:
					useful['shortcuts'].append(calc)
				elif calc in useful['shortcuts']:
					useful['shortcuts'].remove(calc)
				else:
					print('weird shortcut',calc,useful['shortcuts'],ans)

		elif ans["__type__"] == "InventoryContentMessage":
			for x in ans['objects']:
				if x['position'] == 63 and len(x['effects'])<10:
					useful['inventory'][x['objectGID']]={'objectUID':x['objectUID'],'quantity':x['quantity']}

		elif ans["__type__"] == "ObjectQuantityMessage":
			for x in useful['inventory'].values():
				if x['objectUID'] == ans['objectUID']:
					x['quantity']=ans['quantity']
					break

		elif ans["__type__"] == "ObjectAddedMessage":
			useful['inventory'][ans['object']['objectGID']] = {'objectUID':ans['object']['objectUID'],'quantity':ans['object']['quantity']}

		elif ans["__type__"] == "ExchangeBidPriceForSellerMessage":	
			if ans['genericId'] in useful['inventory']:
				useful['inventory'][ans['genericId']]['averagePrice'] = ans['averagePrice']
				useful['inventory'][ans['genericId']]['minimalPrices'] = ans['minimalPrices']
				useful['inventory'][ans['genericId']]['type'] = 'r' if useful['mapid']==73400322 else 'c'
				useful['ready_to_sell'].append({'genericId':ans['genericId'],'minimalPrices':ans['minimalPrices'],'averagePrice':ans['averagePrice'],'quantity':useful['inventory'][ans['genericId']]['quantity'],'type':'r' if useful['mapid']==73400322 else 'c'})

		elif ans["__type__"] == "ReloginTokenStatusMessage":
			useful['relog']=True

		elif ans["__type__"] == "ExchangeStartedBidBuyerMessage":
			useful['dialog']=True

		elif ans["__type__"] == "MountClientData":
			useful['mount']['lvl'] = ans['level']
			useful['mount']['energy'] = ans['energy']
			for x in ans['effectList']:
				if x['actionId']==125:
					useful['mount']['bonus']=x['value']
					break

		elif ans["__type__"] == "MountRidingMessage":
			useful['mount']['riding'] = ans['isRiding']
			if ans['isRiding']:
				useful['lifepoints']+=useful['mount']['bonus']

		elif ans["__type__"] == "GameFightNewRoundMessage":
			if useful['infight']:
				useful["fight"]["round"] = ans["roundNumber"]

		elif ans["__type__"] == "GameActionFightLifePointsLostMessage":
			if useful['infight']:
				if useful['contextualId']==ans['targetId']:
					useful['lifepoints']-=ans['loss']
					useful['maxLifePoints']-=ans['permanentDamages']
					if not ans['loss'] and ans['permanentDamages']:
						useful['lifepoints']-=ans['permanentDamages']
					# logging.info(f"{useful['lifepoints'],useful['maxLifePoints'],ans}")
				elif ans['targetId'] in useful['fight']['enemyteamMembers']: useful['fight']['enemyteamMembers'][ans['targetId']]['lifepoints']-=ans['loss']

		elif ans["__type__"] in ("NpcDialogCreationMessage","LockableShowCodeDialogMessage","ZaapDestinationsMessage"):
			useful["dialog"]=True

		elif ans["__type__"] == "LeaveDialogMessage" :
			useful['dialog'],useful['Harvesting'] = False,False

		elif ans["__type__"]== "GameRolePlayMonsterAngryAtPlayerMessage" and useful['contextualId']==ans['playerId']:
			if ans['monsterGroupId'] not in useful['agro']:
				useful['agro'].append(ans['monsterGroupId'])
			# print('add',ans,useful['agro'])
		elif ans["__type__"]=="GameRolePlayMonsterNotAngryAtPlayerMessage" and useful['contextualId']==ans['playerId']:
			if ans['monsterGroupId'] in useful['agro']:
				useful['agro'].remove(ans['monsterGroupId'])
			# print('remove',ans,useful['agro'])

		elif ans["__type__"] == "GameRolePlayHumanoidInformations":
			try:
				if "["  == ans["name"][0]:
					useful["threat"]="medium"
					logging.critical(f"MODERATOR PRESENCE OF THIS MAP {ans}")
				if useful['contextualId']!= ans['contextualId']:
					useful["map_players"][ans["contextualId"]]={"name":ans["name"],"cellid":ans["disposition"]["cellId"]}
				else:
					useful["mypos"] = ans["disposition"]["cellId"]
			except:
				logging.error(f'ok bb {ans}')

		elif ans["__type__"] == "GameContextActorPositionInformations" or ans["__type__"]=="GameContextActorInformations" or ans["__type__"]=="GameRolePlayNamedActorInformations":
			if not useful['contextualId'] and  ans["__type__"]=="GameRolePlayNamedActorInformations" and useful["name"]== ans["name"]:
				useful["contextualId"]=ans["contextualId"]
			if useful['contextualId']== ans['contextualId']:
				useful["mypos"] = ans["disposition"]["cellId"]

		elif ans["__type__"] == "ChatServerMessage":
			if '[' == ans["senderName"][0]:
				useful['threat']='medium'
				logging.critical(f"MODERATOR MESSAGE RECEIVED {ans['senderName']}\n{ans}")
			if ans['channel'] == 8:
				useful['threat']='high'
				logging.critical(f'MODERATOR MESSAGE : {ans}\nmap : {useful["mapid"]}')
			elif ans['channel'] == 9:
				useful['threat']='medium'
				logging.warning(f'Sender : {ans["senderName"]}\nContent : {str(ans["content"])}\nChannel : {ans["channel"]}')
			# elif ans['channel'] == 0:
				# if 'bot' in (s:=str(ans["content"])):
					# useful['threat']='low'
			# logging.warning(f'Sender : {ans["senderName"]}\nContent : {str(ans["content"])}\nChannel : {ans["channel"]}')


		elif ans["__type__"] == "PopupWarningMessage":
			useful['threat']='high'
			logging.critical(f'MODERATOR MESSAGE : {ans}\nmap : {useful["mapid"]}')


		elif ans["__type__"] in ("ChatAdminServerMessage","AdminCommandMessage"):
			logging.warning(f'ADMIN SERVER MESSAGE : {ans}map : {useful["mapid"]}')
			# useful['threat']='high'
			useful['mod']=True

		elif ans["__type__"] == "ExchangeStartOkHumanVendorMessage":
			useful['dialog']=True

		elif ans["__type__"] in ("ExchangeRequestedMessage","ExchangeShopStockStartedMessage","GameRolePlayPlayerFightRequestMessage","ExchangeRequestedTradeMessage","PartyInvitationMessage","GuildInvitedMessage","InviteInHavenBagOfferMessage","ExchangeReplyTaxVendorMessage"):
			useful["dialog"],useful['threat']=True if ans["__type__"] not in ("ExchangeReplyTaxVendorMessage","PartyInvitationMessage") else 2,'low'
			logging.warning(f'dialog : {ans["__type__"]}\nmap : {useful["mapid"]}')

		elif ans["__type__"] == "InventoryWeightMessage":
			id = 3009
			addInventoryWeightMessage(ans)

		elif ans['__type__'] in ['MapComplementaryInformationsDataMessage',
								 'MapComplementaryInformationsDataInHavenBagMessage']:
			addMapComplementaryInformationsDataMessage(ans)

		elif ans["__type__"] == "GameMapMovementMessage":
			addGameMapMovementMessage(ans)

		elif ans["__type__"] == "StatedElementUpdatedMessage":
			addStatedElementUpdatedMessage(ans)

		elif ans["__type__"] == "InteractiveElementUpdatedMessage":
			addInteractiveElementUpdatedMessage(ans)

		elif ans["__type__"] == "CharacterSelectedSuccessMessage":
			useful['my_level'] = ans['infos']['level']
			useful['contextualId'] = ans['infos']['id']

		elif ans["__type__"] == "CharacterLevelUpMessage":
			useful["leveledup"] = True
			useful["my_level"] += 1

		elif ans["__type__"] == "CharacterStatsListMessage":

			if ans["stats"] and 'characteristicId' in ans['stats']:
				useful["kamas"] = ans["stats"]["kamas"]
				useful["maxLifePoints"]=0
				for x in ans["stats"]["characteristics"]:
					if x["characteristicId"]==29:
						useful["energy"]=x["total"]
					elif x["characteristicId"]==19:
						useful['fight']['range']=x["objectsAndMountBonus"]
					elif x["characteristicId"]==144:
						useful["fight"]["ap"]=x["total"]
					elif x["characteristicId"]==145:
						useful["fight"]["mp"]=x["total"]
					elif x["characteristicId"]==0 or x["characteristicId"]==11:
						useful["maxLifePoints"]+=x["base"]+x["objectsAndMountBonus"]


		elif ans["__type__"] == 'FighterStatsListMessage':
			useful['fight']["range"],prev = 0,None
			for x in [*ans['stats']['range'].values()][1:]:
				useful['fight']['range']+=x

		elif ans["__type__"] == 'FightTemporaryBoostEffect':
			if ans['targetId']==useful['contextualId']:
				if ans['spellId'] in (13058,13047) and prev != ans['spellId']:#change hardcoded spell id may change
					useful['fight']['range']+=ans['delta']
					prev=ans['spellId']
				if ans['spellId'] == 4677:
					useful['fight']['mp']-= ans['delta']
					useful['fight']['mplost'].append(1)


		elif ans["__type__"] == "GameActionFightPointsVariationMessage":
			target = ans["targetId"]
			howmuch = ans["delta"]
			if target == useful["contextualId"]: 
				if ans["actionId"] == 102:
					useful["fight"]["ap"] = int(useful["fight"]["ap"]) + int(howmuch)
				elif ans["actionId"] == 129:
					useful["fight"]["mp"] = int(useful["fight"]["mp"]) + int(howmuch)


		elif ans["__type__"] == "LifePointsRegenEndMessage":
			useful["maxLifePoints"] = ans["maxLifePoints"]
			useful["lifepoints"] = ans["lifePoints"]
			# logging.info(f"{useful['lifepoints'],useful['maxLifePoints'],ans}")

		elif ans["__type__"] == "GameActionFightLifePointsGainMessage":
			# useful["lifepoints"] += ans["delta"]
			useful['lifepoints']=useful['maxLifePoints']
			# logging.info(f"{useful['lifepoints'],useful['maxLifePoints'],ans}")

		elif ans["__type__"] == "GameActionFightTeleportOnSameMapMessage":
			target  = ans["targetId"]
			cellid = ans["cellId"]
			if target == useful["contextualId"]:
				useful["mypos"] = cellid
				useful["fight"]["mypos"]
		#     Handle each fighter
		elif ans["__type__"] == "CharacterCharacteristicsInformations":
			useful["maxLifePoints"]=0
			for x in ans["characteristics"]:
				if 'characteristicId' in x:
					if x["characteristicId"]==29:
						useful["energy"]=x["total"]
					elif x["characteristicId"]==144:
						useful["ap"]=x["total"]
					elif x["characteristicId"]==145:
						useful["mp"]=x["total"]
					elif x["characteristicId"]==0 or x["characteristicId"]==11:
						useful["maxLifePoints"]+=x["base"]+x["objectsAndMountBonus"]


		elif ans["__type__"] == "GameRolePlayPlayerLifeStatusMessage":
			useful["phenix"] = ans["phenixMapId"]


		elif ans["__type__"] == "TreasureHuntDigRequestAnswerMessage" and 'hunt' in useful:
			useful['hunt']['questType'] = ans['questType']
			useful['hunt']['result'] = ans['result']

		elif ans["__type__"]=="TreasureHuntRequestAnswerMessage" and ans['result']==3 and 'hunt' not in useful:
			useful['retake']=1


		elif ans["__type__"] == "TreasureHuntMessage":
			useful['hunt'] = {}
			useful['hunt']['questType'] = ans['questType']
			useful['hunt']['startMapId'] = ans['startMapId']
			useful['hunt']['knownStepsList'] = ans['knownStepsList']
			useful['hunt']['currentstep'] = ans['knownStepsList'][-1]
			useful['hunt']['totalStepCount'] = ans['totalStepCount']
			useful['hunt']['checkPointCurrent'] = ans['checkPointCurrent']
			useful['hunt']['checkPointTotal'] = ans['checkPointTotal']
			useful['hunt']['availableRetryCount'] = ans['availableRetryCount']
			useful['hunt']['flags'] = ans['flags']

		elif ans["__type__"]=="TreasureHuntFinishedMessage":
			logging.info('hunt finished')
			print(f'Hunt finished : {useful["server"]} - {useful["name"]} {strftime("%A, %d %B %Y %I:%M %p")}')
			if "hunt" in useful:	del useful["hunt"]

		elif ans["__type__"] == "GameFightShowFighterMessage":
			id = int(ans["informations"]["contextualId"])
			if id == useful["contextualId"]:
				useful["mypos"] = ans["informations"]["disposition"]["cellId"]
				useful["fight"]["my_teamid"] = ans["informations"]["spawnInfo"]["teamId"]
				useful["my_level"] = ans["informations"]["level"]

				# useful["fight"]["ap"] = ans["informations"]["stats"]["actionPoints"]

			elif id < 0 and id not in useful["fight"]["mysummons"]:
				useful["fight"]["enemyteamMembers"][id]["cellid"] = ans["informations"]["disposition"]["cellId"]
				for x in ans["informations"]["stats"]["characteristics"]["characteristics"]:
					if x["characteristicId"]==0:
						useful["fight"]["enemyteamMembers"][id]["lifepoints"]=x["total"]
				# useful["fight"]["enemyteamMembers"][id]["lifepoints"] = ans["informations"]["stats"]["lifePoints"]
				useful["fight"]["enemyteamMembers"][id]["summoned"] = ans["informations"]["stats"]["summoned"]
				try:
					useful["fight"]["enemyteamMembers"][id]["level"] = ans["informations"]["creatureLevel"]
				except:
					pass
			else:
				useful["fight"]["teamMembers"][id]["status"] = ans["informations"]["status"]["__type__"]
				useful["fight"]["teamMembers"][id]["previousPositions"] = ans["informations"]["previousPositions"]
				useful["fight"]["teamMembers"][id]["level"] = ans["informations"]["level"]

		elif ans["__type__"] == "GameFightFighterNamedInformations":
			if not useful["contextualId"] and useful["name"]==ans["name"]:
				useful["contextualId"]=ans["contextualId"]
			if useful["contextualId"]==ans["contextualId"]:
				useful["mypos"]=ans["disposition"]["cellId"]
				if useful['infight']:
					useful["maxLifePoints"]=0
					for x in ans["stats"]["characteristics"]["characteristics"]:
						if x["characteristicId"]==19:
							useful['fight']['range']=x["objectsAndMountBonus"]
						elif x["characteristicId"]==1:
							useful["fight"]["ap"]=x["base"]+x["objectsAndMountBonus"]
						elif x["characteristicId"]==23:
							useful["fight"]["mp"]=x["base"]+x["objectsAndMountBonus"]
						elif x["characteristicId"]==0 or x["characteristicId"]==11:
							useful["maxLifePoints"]+=x["base"]+x["objectsAndMountBonus"]

		elif ans["__type__"] == "GameFightSynchronizeMessage":
			useful["fight"]["enemyteamMembers"] = {}
			for fighter in ans["fighters"]:
				if fighter["__type__"] == "GameFightMonsterInformations":
					addGameFightMonsterInformations(fighter)
				if fighter["__type__"] == "GameFightCharacterInformations":
					addGameFightCharacterInformations(fighter)

		elif ans["__type__"] == "GameEntitiesDispositionMessage":
			for disposition in ans["dispositions"]:
				id = int(disposition["id"])
				cellid = disposition["cellId"]
				if id == useful["contextualId"]:
					useful["mypos"] = cellid
					useful["fight"]["mypos"] = cellid
				if useful['infight']:
					if id < 0:
						# if id in useful["fight"]["mysummons"]:
							# useful["fight"]["mysummons"][id]["cellid"] = cellid
						# else:
						try:
							useful["fight"]["enemyteamMembers"][id]["cellid"] = cellid
						except:
							useful["fight"]["enemyteamMembers"][id] = {}
							useful["fight"]["enemyteamMembers"][id]["cellid"] = cellid
					else:
						try:
							useful["fight"]["teamMembers"][id]["cellid"] = cellid
						except:
							useful["fight"]["teamMembers"][id] = {}
							useful["fight"]["teamMembers"][id]["cellid"] = cellid


		elif ans["__type__"] == "GameActionFightSlideMessage":
			try:
				if useful['contextualId']==ans["targetId"]:
					useful['mypos']=ans["endCellId"]
				else:
					useful["fight"]["enemyteamMembers"][ans["targetId"]]["cellid"] = ans["endCellId"]
			except:
				logging.error('fight slide message error')

		elif ans["__type__"] == "GameFightTurnEndMessage":
			if ans["id"]==useful['contextualId']:
				useful["fight"]["turn"] = False

		elif ans["__type__"] == "GameFightTurnStartMessage":
			logging.info(f'new turn {ans}')
			if ans["id"]==useful['contextualId']:
				useful["fight"]["turn"] = True

		elif ans["__type__"] == "GameFightStartMessage":
			logging.info("fight start msg!!!!!")
			useful["fight"]["fight_state"] = "Started"
			if "positionsForDefenders" in useful["fight"]:	del useful["fight"]["positionsForDefenders"]
			if "positionsForChallengers" in useful["fight"]:	del useful["fight"]["positionsForChallengers"]

		elif ans["__type__"] == "FightStartingPositions":
			useful["fight"]["positionsForChallengers"] = ans["positionsForChallengers"]
			useful["fight"]["positionsForDefenders"] = ans["positionsForDefenders"]
		
		elif ans["__type__"] == "GameFightTurnListMessage":
			useful["fight"]["turn_list"] = ans["ids"]
			try:
				for id in ans["deadsIds"]:
					if id < 0 and id not in useful["fight"]["mysummons"]:
						del useful["fight"]["enemyteamMembers"][id]
					elif id in useful["fight"]["mysummons"]:
						del useful["fight"]["mysummons"][id]
					else:
						del useful["fight"]["teamMembers"][id]
			except:
				pass

		elif ans["__type__"] == "GameActionFightDeathMessage":
			tagetid = ans["targetId"]
			sourceid = ans["sourceId"]
			if useful['infight'] and tagetid in useful["fight"]["enemyteamMembers"]:
				del useful["fight"]["enemyteamMembers"][tagetid]

		elif ans["__type__"] == "GameFightStartingMessage":
			useful["infight"] = ans["fightId"]
			useful["fight"] = {}
			useful["fight"]["round"] = None
			useful["fight"]["markedcells"] = []
			useful["fight"]["turn"] = None
			useful["fight"]["fight_state"] = "Starting"
			useful["fight"]["fightId"] = ans["fightId"]
			useful["fight"]["enemyteamMembers"] = {}
			useful["fight"]["teamMembers"] = {}
			useful["fight"]["attackerId"] = ans['attackerId']
			useful["fight"]["defenderId"] = ans['defenderId']
			useful["fight"]['afk'] = False,
			useful["fight"]["mysummons"] = {}
			useful["fight"]["outofsight"] = None
			useful["fight"]["ap"] = 6
			useful["fight"]["lifepoints"] = None
			useful["fight"]["mp"] = 3
			useful["fight"]["range"] = 0
			useful["fight"]["mypos"] = useful["mypos"]
			useful["fight"]['alive'] = True
			useful["fight"]['lock'] = False
			useful["fight"]['spectator'] = False
			useful["fight"]['mplost'] = []



		elif ans["__type__"] == "GameFightPlacementPossiblePositionsMessage":
			useful["fight"]["positionsForChallengers"] = ans["positionsForChallengers"]
			useful["fight"]["positionsForDefenders"] = ans["positionsForDefenders"]
			useful["fight"]["my_teamid"] = ans["teamNumber"]

		elif ans["__type__"] == "UpdateLifePointsMessage":
			useful["lifepoints"] = ans["lifePoints"]
			useful["maxLifePoints"] = ans["maxLifePoints"]

		elif ans["__type__"] == "GameFightFighterInformations":
			# id = not message
			id = int(ans["contextualId"])
			if ans["contextualId"] == useful["contextualId"]:
				useful["mypos"] = ans["disposition"]["cellId"]
				useful["fight"]["mypos"] = ans["disposition"]["cellId"]
				useful["maxLifePoints"]=0
				for x in ans["stats"]["characteristics"]["characteristics"]:
					if x["characteristicId"]==19:
						useful['fight']['range']=x["objectsAndMountBonus"]
					elif x["characteristicId"]==1:
						useful["fight"]["ap"]=x["base"]+x["objectsAndMountBonus"]
					elif x["characteristicId"]==23:
						useful["fight"]["mp"]=x["base"]+x["objectsAndMountBonus"]
					elif x["characteristicId"]==0 or x["characteristicId"]==11:
						useful["maxLifePoints"]+=x["base"]+x["objectsAndMountBonus"]
			elif id <0:
				useful["fight"]["enemyteamMembers"][id] = {}
				useful["fight"]["enemyteamMembers"][id]["cellid"] = ans["disposition"]["cellId"]
				useful["fight"]["enemyteamMembers"][id]["alive"] = ans["spawnInfo"]["alive"]
				for x in ans["stats"]["characteristics"]["characteristics"]:
					if x["characteristicId"]==0:
						useful["fight"]["enemyteamMembers"][id]["lifepoints"] = x["total"]
						break
		elif ans["__type__"] == "CharacterSelectionMessage":
			useful["contextualId"] = ans["id"]

		elif ans["__type__"] == "AccountCapabilitiesMessage":
			useful["accountId"] = ans["accountId"]

		elif ans["__type__"] == "GameFightUpdateTeamMessage":
			id = 5572
			if useful["infight"]:
				if ans["fightId"] == useful["fight"]["fightId"]:
					if ans["team"]["leaderId"] == useful["contextualId"]:
						useful["fight"]["teamMembers"] = {}
						for member in ans["team"]["teamMembers"]:
							try:
								useful["fight"]["teamMembers"][int(member["id"])]["level"] = member["level"]
							except:
								useful["fight"]["teamMembers"][int(member["id"])] = {}
								useful["fight"]["teamMembers"][int(member["id"])]["level"] = member["level"]
					else:
						if not useful["fight"]["enemyteamMembers"]:
							useful["fight"]["enemyteamMembers"] = {}
						for member in ans["team"]["teamMembers"]:
							if 'grade' in member:
								try:
									useful["fight"]["enemyteamMembers"][int(member["id"])]["grade"] = member["grade"]
									useful["fight"]["enemyteamMembers"][int(member["id"])]["monsterId"] = member["monsterId"]
								except:
									useful["fight"]["enemyteamMembers"][int(member["id"])] = {}
									useful["fight"]["enemyteamMembers"][int(member["id"])]["grade"] = member["grade"]
									useful["fight"]["enemyteamMembers"][int(member["id"])]["monsterId"] = member["monsterId"]

		elif ans["__type__"] == "GameActionFightNoSpellCastMessage":
			useful["fight"]["outofsight"] = True

		elif ans["__type__"] == "TextInformationMessage":
			if ans["msgId"] in (436,437):
				useful["wait"]=int(ans["parameters"][0])

		elif ans["__type__"] == "InventoryContentMessage":
			useful["kamas"] = ans["kamas"]

		elif ans["__type__"] == "KamasUpdateMessage":
			useful["kamas"] = ans["kamasTotal"]

		elif ans["__type__"] == 'JobExperienceMultiUpdateMessage':
			jobs_dict = {str(job['jobId']): job for job in ans['experiencesUpdate']}
			for key, value in jobs_dict.items():
				if key in useful['jobs'].keys():
					useful['jobs'][key].update(
						{"jobLevel": value["jobLevel"], "jobXpNextLevelFloor": value["jobXpNextLevelFloor"]})
				else:
					useful['jobs'][key] = {"jobLevel": value["jobLevel"],
										   "jobXpNextLevelFloor": value["jobXpNextLevelFloor"]}

		elif ans["__type__"] == 'JobExperienceUpdateMessage':
			useful['Harvesting'] = False
			if ans["experiencesUpdate"]["jobId"] in useful["jobs"].keys():
				if ans["experiencesUpdate"]["jobLevel"] > useful["jobs"][ans["experiencesUpdate"]["jobId"]]["jobLevel"]:
					useful["jobupdated"] = True

			jobs_dict = {str(ans['experiencesUpdate']['jobId']): ans['experiencesUpdate']}
			for key, value in jobs_dict.items():
				if key in useful['jobs'].keys():
					useful['jobs'][key].update(value)
				else:
					useful['jobs'][key] = value

		elif ans["__type__"] == "CurrentServerStatusUpdateMessage":
			if ans['status'] == 5:
				useful['backup']=True
				logging.warning('Server backup')
			if ans['status'] == 3:
				useful['backup']=False
				logging.warning('Server backup finished')


		elif ans["__type__"] == "GameFightEndMessage":
			useful["infight"] = False
			for x in ans['results']:
				if x['id']==useful['contextualId']:
					useful['w_l_f']=x['outcome']==2
					break
		elif ans["__type__"] == "InteractiveUsedMessage" and ans["entityId"] == useful["contextualId"]:
			useful['Harvesting'] = ans["elemId"]

		elif ans["__type__"] == "InteractiveUseEndedMessage" and useful['Harvesting'] == ans["elemId"]:
			useful['Harvesting'] = False

		elif ans["__type__"] == "NotificationByServerMessage":
			id = ans["id"]
			# parameters = ans["parameters"]
			# forceopen = ans["forceOpen"]
			# if id == 10:
				# print("CharacterLevelUp")
			# elif id in [13, 12]:
				# print("PlayerIsDead")
			if id == 37:
				useful["full_inventory"] = True
				logging.info("Full inventory")
			# elif id == 14:
				# print("turned to a ghost")

		elif ans["__type__"] == "GameContextRemoveElementMessage":
			try:
				if int(ans["id"]) < 0:
					del useful["map_mobs"][ans["id"]]
				else:
					del useful["map_players"][ans["id"]]
			except:
				pass

		return ans
	except:
		logging.error(f'Error in protocol {ans}',exc_info=1)
		useful['reset']=True



def writeBooleans(boolVars, el, data):
	bits = []
	for var in boolVars:
		bits.append(el[var["name"]])
		if len(bits) == 8:
			data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))
			bits = []
	if bits:
		data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))


def writeVec(var, el, data):
	assert var["length"] is not None
	n = len(el)
	if isinstance(var["length"], int):
		assert n == var["length"]
	else:
		write(var["length"], n, data)
	for it in el:
		write(var["type"], it, data)


def write(type, json, data=None, random_hash=True) -> Data:
	if data is None:
		data = Data()
	if type is False:
		type = types[json["__type__"]]
		data.writeUnsignedShort(type["protocolId"])
	elif isinstance(type, str):
		if type in primitives:
			primitives[type][1](data, json)
			return data
		type = types[type]
	parent = type["parent"]
	if parent is not None:
		write(parent, json, data)
	writeBooleans(type["boolVars"], json, data)
	for var in type["vars"]:
		if var["optional"]:
			if var["name"] in json:
				data.writeByte(1)
			else:
				data.writeByte(0)
				continue
		if var["length"] is not None:
			writeVec(var, json[var["name"]], data)
		else:
			write(var["type"], json[var["name"]], data)
	if "hash_function" in json:
		data.write(json["hash_function"])
	elif type["hash_function"] and random_hash:
		hash = bytes(random.getrandbits(8) for _ in range(48))
		data.write(hash)
	return data
