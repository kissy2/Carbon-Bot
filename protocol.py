from data import Data
from pathlib import Path
import pickle
import random
from functools import reduce
import pprint
import json
import logging
from win10toast import ToastNotifier
toaster=ToastNotifier()

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='lol1.log', level=logging.DEBUG)

with (Path(__file__).parent / "protocol.pk").open("rb") as f:
	types = pickle.load(f)
	msg_from_id = pickle.load(f)
	types_from_id = pickle.load(f)
	primitives = pickle.load(f)

primitives = {
	name: (getattr(Data, "read" + name), getattr(Data, "write" + name))
	for name in primitives
}

useful = {"resources": {},
		  "fight": {},
		  "lifepoints": 100,
		  "maxLifePoints": 100,
		  "my_level": 1,
		  "accountId": 99834247,
		  "contextualId":130762735827,#1997340912,
		  "jobupdated": False,
		  "leveledup": False,
		  'jobs': {},
		  'Harvesting': False,
		  'zaap_dialog_open': False,
		  'zaap_destinations': None,
		  "map_mobs": {},
		  "map_npc": {},
		  "map_merchant": {},
		  "ap": None,
		  "inventory_weight": 0,
		  "inventory_max": 1,
		  "infight": False,
		  "map_players": {},
		  "mypos": 0,
		  "mapid": None,
		  "subAreaId": None,
		  "fightCount": None,
		  "full_inventory": False,
		  }

tmp = {}


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
	useful["resources"] = {}
	useful["map_mobs"] = {}
	useful["map_merchant"] = {}
	useful["map_npc"] = {}
	useful["map_players"] = {}
	useful["mapid"] = ans["mapId"]
	useful["subAreaId"] = ans["subAreaId"]
	for actor in ans["actors"]:
		# This if was commented, why?
		if actor["__type__"] == "GameRolePlayMerchantInformations":
			useful["map_merchant"][actor["contextualId"]] = {}
			useful["map_merchant"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

		if actor["__type__"] == "GameRolePlayNpcInformations":
			useful["map_npc"][actor["contextualId"]] = {}
			useful["map_npc"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

		if actor["__type__"] == "GameRolePlayCharacterInformations":
			if actor["accountId"] == useful["accountId"]:
				useful["mypos"] = actor["disposition"]["cellId"]
			else:
				useful["map_players"][actor["contextualId"]] = {}
				useful["map_players"][actor["contextualId"]]["cellId"] = actor["disposition"]["cellId"]

		if actor["__type__"] == "GameRolePlayGroupMonsterInformations":
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
		# logging.info("added element")
		# logging.info(elemnt2)

	for element in ans["interactiveElements"]:
		if element["enabledSkills"]:
			try:
				elmentid = element["elementId"]
				if tmp[elmentid]["elementCellId"] \
						and element["onCurrentMap"] \
						and element["enabledSkills"][0]["skillId"] != 114:
					useful["resources"][elmentid] = {}
					useful["resources"][elmentid]["elementCellId"] = tmp[elmentid]["elementCellId"]
					useful["resources"][elmentid]["enabledSkill"] = element["enabledSkills"][0]["skillId"]
					useful["resources"][elmentid]["elementTypeId"] = element["elementTypeId"]
					useful["resources"][elmentid]["elementState"] = tmp[elmentid]["elementState"]
					for map in mapinfo:
						if map["id"] == ans["mapId"]:
							useful["resources"][elmentid]["offset"] = map['interactives']['2'][str(elmentid)]["offset"]
			except:
				# logging.info("resource does not exist")
				pass

def addGameMapMovementMessage(ans):
	if ans["actorId"] == useful["contextualId"]:
		useful["mypos"] = ans["keyMovements"][-1]
		if useful["infight"]:
			useful["fight"]["mypos"] = ans["keyMovements"][-1]
	else:
		if ans["actorId"] < 0:
			if useful["infight"]:
				if ans["actorId"] in useful["fight"]["mysummons"]:
					useful["fight"]["mysummons"][ans["actorId"]]["cellid"] = ans["keyMovements"][-1]
				else:
					useful["fight"]["enemyteamMembers"][ans["actorId"]]["cellid"] = ans["keyMovements"][-1]
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
			useful["fight"]["enemyteamMembers"][id]["lifepoints"] = ans["stats"]["lifePoints"]
			useful["fight"]["enemyteamMembers"][id]["summoned"] = ans["stats"]["summoned"]
			try:
				useful["fight"]["enemyteamMembers"][id]["level"] = ans["creatureLevel"]
			except:
				pass
		else:
			useful["fight"]["mysummons"][id] = {}
			useful["fight"]["mysummons"][id]["cellid"] = ans["disposition"]["cellId"]
			useful["fight"]["mysummons"][id]["lifepoints"] = ans["stats"]["lifePoints"]
			useful["fight"]["mysummons"][id]["summoned"] = ans["stats"]["summoned"]
			try:
				useful["fight"]["mysummons"][id]["level"] = ans["creatureLevel"]
			except:
				pass

def addGameFightCharacterInformations(ans):
	id = int(ans["contextualId"])
	if id == useful["contextualId"]:
		useful["mypos"] = ans["disposition"]["cellId"]
		useful["fight"]["mypos"] = useful["mypos"]
		useful["fight"]["my_teamid"] = ans["spawnInfo"]["teamId"]
		useful["my_level"] = ans["level"]
		useful["fight"]["ap"] = ans["stats"]["actionPoints"]
		useful["fight"]["mp"] = ans["stats"]["movementPoints"]
		useful["lifepoints"] = ans["stats"]["lifePoints"]
		

	else:
		useful["fight"]["teamMembers"][id]["status"] = ans["status"]["__type__"]
		useful["fight"]["teamMembers"][id]["previousPositions"] = ans["previousPositions"]
		useful["fight"]["teamMembers"][id]["level"] = ans["level"]



def addInteractiveElementUpdatedMessage(ans):
	global resourcetmp
	# logging.info("updating interactive")
	elemid = ans["interactiveElement"]["elementId"]
	try:
		# logging.info("trying to add")
		# logging.info(ans)
		# logging.info(useful["resources"])
		resourcetmp[elemid]["enabledSkill"] = ans["interactiveElement"]["enabledSkills"][0]["skillId"]
		resourcetmp[elemid]["elementTypeId"] = ans["interactiveElement"]["elementTypeId"]
		# logging.info("added interactive")
		for map in mapinfo:
			if map["id"] == useful["mapid"]:
				resourcetmp[elemid]["offset"] = map['interactives']['2'][str(elemid)]["offset"]
		# logging.info("added interactive offset")

	except:
		# logging.info("exception while trying to update")
		# logging.info(ans)
		# logging.info(useful["resources"])
		pass

	if ans["interactiveElement"]["disabledSkills"] or not ans["interactiveElement"]["onCurrentMap"]:
		try:
			# logging.info("trying to delete element")
			del useful["resources"][elemid]
		except:
			# logging.info("could not delete element")
			# logging.info(ans)
			pass
	else:
		try:
			useful["resources"][elemid] = resourcetmp[elemid]
		except:
			# logging.info('huh?')
			# logging.info(elemid)
			# logging.info(ans)
			pass

def addStatedElementUpdatedMessage(ans):
	global resourcetmp
	resourcetmp = {}
	# logging.info("updating element")
	elemid = ans["statedElement"]["elementId"]
	resourcetmp[elemid] = {}
	resourcetmp[elemid]["elementCellId"] = ans["statedElement"]["elementCellId"]
	resourcetmp[elemid]["elementState"] = ans["statedElement"]["elementState"]
	# logging.info("updated element")
	# logging.info(ans)
	# logging.info(useful["resources"])



def read(type, data: Data):
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
	pp = pprint.PrettyPrinter(indent=4)

	if type["hash_function"] and data.remaining() == 48:
		ans["hash_function"] = data.read(48)
	flag = True
	# logging.warning(str(ans))
	# logging.warning(str(useful))
	# if ans["__type__"] == "ObjectQuantityMessage":
	#     id = 3023
	#     addObjectQuantityMessage(ans)

	# elif ans["__type__"] == "ObjectDeletedMessage":
	#     for index, item in enumerate(useful['inventory']):
	#         if item == ans['objectUID']:
	#             del useful['inventory'][index]
	#             break

	# elif ans["__type__"] == "ObjectsDeletedMessage":
	#     for uid in ans['objectUID']:
	#         for index, item in enumerate(useful['inventory']):
	#             if item['objectUID'] == uid:
	#                 del useful['inventory'][index]
	#                 break

	# elif ans["__type__"] == "ObjectsQuantityMessage":
	#     for new_item in ans['objectsUIDAndQty']:
	#         useful['inventory']['objectUID'] = new_item['quantity']
	#
	# elif ans["__type__"] == "ObjectsQuantityMessage":
	#     useful['inventory'].append(ans['object'])

	if ans["__type__"] == "GameFightNewRoundMessage":
		useful["fight"]["round"] = ans["roundNumber"]


	elif ans["__type__"] == "ChatServerMessage":
		if ans['channel'] == 9:
			msg = ans['content']
			sender = ans['senderName']
			toaster.show_toast(sender + ': '+msg, "Alert!", threaded=True, duration=15)

	elif ans["__type__"] == "InventoryWeightMessage":
		id = 3009
		addInventoryWeightMessage(ans)

	elif ans['__type__'] in ['MapComplementaryInformationsDataMessage',
							 'MapComplementaryInformationsDataInHavenBagMessage']:
		if ans['__type__'] == 'MapComplementaryInformationsDataInHavenBagMessage':
			useful['in_haven_bag'] = True
		else:
			useful['in_haven_bag'] = False
		addMapComplementaryInformationsDataMessage(ans)

	elif ans["__type__"] == "GameMapMovementMessage":
		addGameMapMovementMessage(ans)

	elif ans["__type__"] == "StatedElementUpdatedMessage":
		id = 5709
		addStatedElementUpdatedMessage(ans)

	elif ans["__type__"] == "InteractiveElementUpdatedMessage":
		id = 5708
		addInteractiveElementUpdatedMessage(ans)

	elif ans["__type__"] == "CharacterSelectedSuccessMessage":
		useful['my_level'] = ans['infos']['level']
		useful['contextualId'] = ans['infos']['id']

	elif ans["__type__"] == "CharacterLevelUpMessage":
		useful["leveledup"] = True
		useful["my_level"] += 1

	elif ans["__type__"] == "CharacterStatsListMessage":
		id = 500
		useful["kamas"] = ans["stats"]["kamas"]
		useful['fight']["range"] = 0
		for x in ans["stats"]["range"]:
			if x!='__type__':
				useful['fight']['range']+=int(ans["stats"]["range"][x])
		useful["lifepoints"] = ans["stats"]["lifePoints"]

		useful["fight"]["lifepoints"] = ans["stats"]["lifePoints"]
		useful["fight"]["ap"] = int(ans["stats"]["actionPointsCurrent"])
		useful["fight"]["mp"] = int(ans["stats"]["movementPointsCurrent"])

	elif ans["__type__"] == "GameFightJoinMessage":
		pass
		# {'__type__': 'GameFightJoinMessage', 'isTeamPhase': True, 'canBeCancelled': False, 'canSayReady': True, 'isFightStarted': False, 'timeMaxBeforeFightStart': 450, 'fightType': 4}


	elif ans["__type__"] == "GameActionFightPointsVariationMessage":
		target = ans["targetId"]
		howmuch = ans["delta"]
		if target == useful["contextualId"]: 
			if ans["actionId"] == 102:
				useful["fight"]["ap"] = int(useful["fight"]["ap"]) + int(howmuch)
			elif ans["actionId"] == 129:
				useful["fight"]["mp"] = int(useful["fight"]["mp"]) + int(howmuch)

	# elif ans["__type__"]=="FightTemporaryBoostEffect":
	#     target = ans["targetId"]
	#     howmuch = int(ans["delta"])
	#     if ans["spellId"]==13058 and target == useful["contextualId"]:
	#         useful['fight']['range']+=howmuch

	# elif ans["__type__"] == "GameFightOptionStateUpdateMessage":
	#     try:
	#         if ans["fightId"] == useful["fight"]["fightId"]:
	#             logging.warning(ans)
	#     except:
	#         logging.error("well, why?")
	#         logging.error(ans)

	# elif ans["__type__"] == "ShortcutBarContentMessage":

	#     for short in ans["shortcuts"]:
	#         useful["SpellList"][short["spellId"]]["slot"] = short["slot"]

	# elif ans["__type__"] == "SpellListMessage":
	#     useful["SpellList"] = {}
	#     for spell in ans["spells"]:
	#         useful["SpellList"][spell["spellId"]] = {"level": spell["spellLevel"]}

	elif ans["__type__"] == "GameActionFightMultipleSummonMessage":
		source = ans["sourceId"]
		# logging.error(ans)
		if source == useful["contextualId"]:
			for summon in ans["summons"]:
				if summon["__type__"] == "GameContextSummonsInformation":
					for summoned in summon["summons"]:
						id = summoned["informations"]["contextualId"]
						id = int(id)
						useful["fight"]["mysummons"][id] = {}
						useful["fight"]["mysummons"][id]["cellid"] = summoned["informations"]["disposition"]["cellId"]
		else:
			for summon in ans["summons"]:
				if summon["__type__"] == "GameContextSummonsInformation":
					for summoned in summon["summons"]:
						if summoned["teamId"] != useful["fight"]["my_teamid"]:
							id = summoned["informations"]["contextualId"]
							id = int(id)
							useful["fight"]["enemyteamMembers"][id] = {}
							useful["fight"]["enemyteamMembers"][id]["cellid"] = summoned["informations"]["disposition"][
								"cellId"]
							useful["fight"]["enemyteamMembers"][id]["summoned"] = True

	elif ans["__type__"] == "GameActionFightSpellCastMessage":
		# logging.warning("spell used")
		source = ans["sourceId"]
		targetid = ans["targetId"]
		targetcell = ans["destinationCellId"]
		# spelllevel = ans["spellId"]
		# useful["SpellList"]

	elif ans["__type__"] == "LifePointsRegenEndMessage":
		useful["maxLifePoints"] = ans["maxLifePoints"]
		useful["lifepoints"] = ans["lifePoints"]

		useful["fight"]["maxLifePoints"] = ans["maxLifePoints"]
		useful["fight"]["lifepoints"] = ans["lifePoints"]


	elif ans["__type__"] == "GameActionFightTeleportOnSameMapMessage":
		target  = ans["targetId"]
		cellid = ans["cellId"]
		if target == useful["contextualId"]:
			useful["mypos"] = cellid
			useful["fight"]["mypos"]
	#     Handle each fighter

	# elif ans["__type__"] == "GameActionFightMarkCellsMessage":
	#     cells = []
	#     if ans["mark"]["active"]:
	#         for cell in ans["mark"]["cells"]:
	#             cells.append(cell)
	#         useful["fight"]["markedcells"].append(ans["sourceId"], cells)

	elif ans["__type__"] == "GameFightTurnStartPlayingMessage":
		#     my turn i think
		pass

	elif ans["__type__"] == "TreasureHuntDigRequestAnswerMessage":
		useful['hunt']['questType'] = ans['questType']
		useful['hunt']['result'] = ans['result']
	#     Result 3 = fail, 1 first?, okay?


	elif ans["__type__"] == "TreasureHuntMessage":
		# direction. Up: 6, Left: 4
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

	elif ans["__type__"] == "GameFightShowFighterMessage":
		id = int(ans["informations"]["contextualId"])
		if id == useful["contextualId"]:
			useful["mypos"] = ans["informations"]["disposition"]["cellId"]
			useful["fight"]["my_teamid"] = ans["informations"]["spawnInfo"]["teamId"]
			useful["my_level"] = ans["informations"]["level"]
			useful["fight"]["ap"] = ans["informations"]["stats"]["actionPoints"]
		elif id < 0 and id not in useful["fight"]["mysummons"]:
			useful["fight"]["enemyteamMembers"][id]["cellid"] = ans["informations"]["disposition"]["cellId"]
			useful["fight"]["enemyteamMembers"][id]["lifepoints"] = ans["informations"]["stats"]["lifePoints"]
			useful["fight"]["enemyteamMembers"][id]["summoned"] = ans["informations"]["stats"]["summoned"]
			try:
				useful["fight"]["enemyteamMembers"][id]["level"] = ans["informations"]["creatureLevel"]
			except:
				pass
		else:
			useful["fight"]["teamMembers"][id]["status"] = ans["informations"]["status"]["__type__"]
			useful["fight"]["teamMembers"][id]["previousPositions"] = ans["informations"]["previousPositions"]
			useful["fight"]["teamMembers"][id]["level"] = ans["informations"]["level"]

	elif ans["__type__"] == "GameActionFightLifePointsLostMessage":
		if ans["targetId"] < 0 and ans["targetId"] not in useful["fight"]["mysummons"]:
			old = int(useful["fight"]["enemyteamMembers"][int(ans["targetId"])]["lifepoints"])
			useful["fight"]["enemyteamMembers"][int(ans["targetId"])]["lifepoints"] = old - int(ans["loss"])

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
			elif id < 0:
				if id in useful["fight"]["mysummons"]:
					useful["fight"]["mysummons"][id]["cellid"] = cellid
				else:
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

	elif ans["__type__"] == "GameFightHumanReadyStateMessage":
		useful["fight"]["fight_state"] = "Ready"

	# elif ans["__type__"] == "ChallengeInfoMessage":
	#     logging.info(ans)

	elif ans["__type__"] == "SequenceStartMessage":
		useful["fight"]["sequence"] = (ans["authorId"], ans["sequenceType"])

	elif ans["__type__"] == "SequenceEndMessage":
		actiontaken = ans["actionId"]
		# if actiontaken == 5:
		#     logging.info("fighter moved")
		#     logging.info(ans["authorId"])
		useful["fight"]["sequence"] = ("sequence", useful["fight"]["sequence"])

	elif ans["__type__"] == "GameFightTurnFinishMessage":
		useful["fight"]['afk'] = True

	elif ans["__type__"] == "GameFightTurnReadyMessage":
		id = useful["fight"]["TurnReadyRequest"]
		useful["fight"]["TurnReadyRequest"] = (id, "Ready")

	elif ans["__type__"] == "GameActionFightSlideMessage":
		if ans["targetId"] < 0 and ans["targetId"] not in useful["fight"]["mysummons"]:
			useful["fight"]["enemyteamMembers"][int(ans["targetId"])]["cellid"] = ans["endCellId"]

	elif ans["__type__"] == "GameFightTurnReadyRequestMessage":
		useful["fight"]["TurnReadyRequest"] = ans["id"]

	elif ans["__type__"] == "GameFightTurnEndMessage":
		if ans["id"]==useful['contextualId']:
			useful["fight"]["turn"] = False

	elif ans["__type__"] == "GameFightTurnStartMessage":
		if ans["id"]==useful['contextualId']:
			useful["fight"]["turn"] = True

	elif ans["__type__"] == "GameFightStartMessage":
		useful["fight"]["fight_state"] = "Started"
		del useful["fight"]["positionsForDefenders"]
		del useful["fight"]["positionsForChallengers"]

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
			print("dead id already deleted")

	# elif ans["__type__"] == "GameActionFightExchangePositionsMessage":
		# pass
		# clone

	# elif ans["__type__"] == "GameActionFightKillMessage":
		# tagetid = ans["targetId"]
		# sourceid = ans["sourceId"]
		# logging.warn(str(sourceid) + " killed ", str(tagetid))

	elif ans["__type__"] == "GameActionFightDeathMessage":
		tagetid = ans["targetId"]
		sourceid = ans["sourceId"]
		if tagetid in useful["fight"]["enemyteamMembers"]:
			del useful["fight"]["enemyteamMembers"][tagetid]
		# logging.warning(str(tagetid) + " died ")

	elif ans["__type__"] == "GameFightStartingMessage":
		id = 700
		useful["infight"] = True
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
		useful["fight"]["ap"] = 7
		useful["fight"]["lifepoints"] = None
		useful["fight"]["mp"] = 3
		useful["fight"]["range"] = 1
		useful["fight"]["mypos"] = useful["mypos"]


	elif ans["__type__"] == "GameFightPlacementPossiblePositionsMessage":
		id = 703
		useful["fight"]["positionsForChallengers"] = ans["positionsForChallengers"]
		useful["fight"]["positionsForDefenders"] = ans["positionsForDefenders"]
		useful["fight"]["my_teamid"] = ans["teamNumber"]

	elif ans["__type__"] == "UpdateLifePointsMessage":
		id = 5658
		useful["lifepoints"] = ans["lifePoints"]


		useful["maxLifePoints"] = ans["maxLifePoints"]
		try:
			useful["fight"]["lifepoints"] = ans["lifePoints"]
			useful["fight"]["maxLifePoints"] = ans["maxLifePoints"]
		except:
			pass

	elif ans["__type__"] == "GameFightFighterInformations":
		# id = not message
		id = int(ans["contextualId"])
		if ans["contextualId"] == useful["contextualId"]:
			useful["mypos"] = ans["disposition"]["cellId"]
			useful["fight"]["mypos"] = ans["disposition"]["cellId"]
			useful["lifepoints"] = ans["stats"]["lifePoints"]
			
			useful["maxLifePoints"] = ans["stats"]["maxLifePoints"]
			useful["fight"]["lifepoints"] = ans["stats"]["lifePoints"]
			useful["fight"]["maxLifePoints"] = ans["stats"]["maxLifePoints"]
			useful["fight"]["ap"] = ans["stats"]["actionPoints"]
		else:
			useful["fight"]["enemyteamMembers"][id] = {}
			useful["fight"]["enemyteamMembers"][id]["cellid"] = ans["disposition"]["cellId"]
			useful["fight"]["enemyteamMembers"][id]["alive"] = ans["spawnInfo"]["alive"]
			useful["fight"]["enemyteamMembers"][id]["lifepoints"] = ans["stats"]["lifePoints"]

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
						try:
							useful["fight"]["enemyteamMembers"][int(member["id"])]["grade"] = member["grade"]
							useful["fight"]["enemyteamMembers"][int(member["id"])]["monsterId"] = member["monsterId"]
						except:
							useful["fight"]["enemyteamMembers"][int(member["id"])] = {}
							useful["fight"]["enemyteamMembers"][int(member["id"])]["grade"] = member["grade"]
							useful["fight"]["enemyteamMembers"][int(member["id"])]["monsterId"] = member["monsterId"]

	elif ans["__type__"] == "GameActionFightNoSpellCastMessage":
		useful["fight"]["outofsight"] = True

	elif ans["__type__"] == "GameRolePlayMonsterAngryAtPlayerMessage":
		# Run  {'__type__': 'GameRolePlayMonsterAngryAtPlayerMessage', 'playerId': useful["contextualId"], 'monsterGroupId': -20002.0, 'angryStartTime': 1581617218215.0, 'attackTime': 1581617227403.0}
		pass
	elif ans["__type__"] == "GameRolePlayMonsterNotAngryAtPlayerMessage":
		#  {'__type__': 'GameRolePlayMonsterNotAngryAtPlayerMessage', 'playerId': useful["contextualId"], 'monsterGroupId': -20002.0}
		pass
	# elif ans["__type__"] == "PopupWarningMessage":
	#     id = 6134
	#     logging.warning(ans)
	# elif ans["__type__"] == "TextInformationMessage":
	#     id = 780
	#     logging.warning(ans)

	elif ans["__type__"] == "InventoryContentMessage":
		useful["kamas"] = ans["kamas"]
		# for obj in ans["objects"]:
		#     useful["inventory"][obj["objectGID"]] = obj["quantity"]

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

	elif ans["__type__"] == "JobDescriptionMessage":
		# for desc in ans['jobsDescription']:
		#     if str(desc['jobId']) in useful['jobs'].keys():
		#         useful['jobs'][str(desc['jobId'])]['skills'] = desc['skills']
		#     else:
		#         useful['jobs'][str(desc['jobId'])] = {'skills': desc['skills']}
		pass

	elif ans["__type__"] == "JobLevelUpMessage":
		pass
		# TODO     useful['jobs'][str(ans['jobsDescription']['jobId'])]['level'] = ans['newLevel']
		#          KeyError: '26'
		# useful['jobs'][str(ans['jobsDescription']['jobId'])]['level'] = ans['newLevel']
		# useful['jobs'][str(ans['jobsDescription']['jobId'])]['skills'] = ans['jobsDescription']['skills']

	# elif ans["__type__"] == "SystemMessageDisplayMessage":
	#     logging.warning("SystemMessageDisplayMessage ", ans)

	elif ans["__type__"] == "ZaapDestinationsMessage":
		useful['zaap_dialog_open'] = True
		useful['zaap_destinations'] = ans['destinations']

	elif ans["__type__"] == "LeaveDialogMessage":
		useful['zaap_dialog_open'] = False
		useful['zaap_destinations'] = None

	elif ans["__type__"] == "GameFightEndMessage":
		for result in ans["results"]:
			if result["__type__"] == "FightResultPlayerListEntry":
				if result["id"] == useful["contextualId"]:
					# logging.warning(" Lost fight")
					# logging.warning(ans)
					useful["fight"] = {'alive': result['alive']}

		useful["infight"] = False

	# elif ans["__type__"] == "ChallengeResultMessage":
	#     logging.info("fight ended?")
	#     if ans["success"]:
	#         logging.info("fight ended succes?")

	elif ans["__type__"] == "InteractiveUsedMessage" and ans["entityId"] == useful["contextualId"]:
		if ans["elemId"] in useful["resources"]:
			useful['Harvesting'] = ans["elemId"]

	elif ans["__type__"] == "InteractiveUseEndedMessage" and useful['Harvesting'] == ans["elemId"]:
		useful['Harvesting'] = False


	elif ans["__type__"] == "BasicNoOperationMessage":
		pass

	elif ans["__type__"] == "BasicTimeMessage":
		pass

	elif ans["__type__"] == "MapFightCountMessage":
		useful["fightCount"] = ans["fightCount"]

	elif ans["__type__"] == "NotificationByServerMessage":
		# TODO check what the fuck is this
		id = ans["id"]
		# logging.warning(ans)
		parameters = ans["parameters"]
		forceopen = ans["forceOpen"]
		if id == 10:
			print("CharacterLevelUp")
		elif id in [13, 12]:
			print("PlayerIsDead")
		elif id == 37:
			useful["full_inventory"] = True
			logging.critical("Full inventory")
		elif id == 14:
			print("turned to a ghost")

	elif ans["__type__"] == "GameContextRemoveElementMessage":
		# logging.critical(ans)
		try:
			if int(ans["id"]) < 0:
				del useful["map_mobs"][ans["id"]]
			else:
				del useful["map_players"][ans["id"]]
		except:
			# logging.error("deleting unixisting actor")
			pass
	elif ans["__type__"] == "AnomalySubareaInformation":
		pass

	else:
		flag = False
	# todo if enventory is full
	# else:
	#     pp = pprint.PrettyPrinter(indent=4)
	#     print("\n\n\n\n\n")
	#     pp.pprint(ans)
	# print("\n\n")
	# # pp.pprint(useful["current_map"]["mapid"])
	# pp.pprint(useful)
	# if type["parent"] is None:
	#     logging.info(ans)
	# print(useful)
	return ans


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
