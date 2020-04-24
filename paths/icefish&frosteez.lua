-- Generated On Dofus-Map with Owl Scripts --
-- Nom : 
-- Zone : 
-- Type : 
-- Version : 1.0
-- Auteur : 

ELEMENTS_TO_GATHER = {}
AUTO_DELETE = {}

MAX_MONSTERS = 8
MIN_MONSTERS = 1

FORBIDDEN_MONSTERS = {}
MANDATORY_MONSTERS = {}

MAX_PODS = 90


function move()
	return {
		{map = "192415750", changeMap = "424"}, --Interieur banque Astrub vers Sortie--
		{map = "54534165", changeMap = "424"}, --Interieur banque Frigost vers Sortie--
		{map = "2883856", changeMap = "440"}, --Interieur banque Bonta vers Sortie--
		{map = "99095051", changeMap = "410"}, --Interieur banque Amakna vers Sortie--
		{map = "8912911", changeMap = "409"}, --Interieur banque Brakmar vers Sortie--
		{map = "91753985", changeMap = "396"}, --Interieur banque Sufokia vers Sortie--
		{map = "86511105", changeMap = "452"}, --Interieur banque Ottomaï vers Sortie--
		{map = "8129542", changeMap = "409"}, --Interieur banque Pandala vers Sortie--
		{map = "84935175", changeMap = "425"}, --Interieur banque Montagne Koalak vers Sortie--
		{map = "-78,-41", changeMap = "top", gather = true},
		{map = "-79,-39", changeMap = "top", gather = true},
		{map = "-82,-40", changeMap = "top", gather = true},
		{map = "-82,-39", changeMap = "top", gather = true},
		{map = "-84,-41", changeMap = "top", gather = true},
		{map = "-84,-40", changeMap = "top", gather = true},
		{map = "-78,-37", changeMap = "top", gather = true},
		{map = "-76,-33", changeMap = "top", gather = true},
		{map = "-72,-32", changeMap = "top", gather = true},
		{map = "-71,-33", changeMap = "top", gather = true},
		{map = "-71,-34", changeMap = "top", gather = true},
		{map = "-69,-35", changeMap = "top", gather = true},
		{map = "-70,-37", changeMap = "top", gather = true},
		{map = "-69,-37", changeMap = "top", gather = true},
		{map = "-69,-38", changeMap = "top", gather = true},
		{map = "-68,-39", changeMap = "top", gather = true},
		{map = "-68,-40", changeMap = "top", gather = true},
		{map = "-69,-40", changeMap = "top", gather = true},
		{map = "-70,-40", changeMap = "top", gather = true},
		{map = "-70,-39", changeMap = "top", gather = true},
		{map = "-70,-41", changeMap = "top", gather = true},
		{map = "-69,-42", changeMap = "top", gather = true},
		{map = "-71,-43", changeMap = "top", gather = true},
		{map = "-70,-45", changeMap = "top", gather = true},
		{map = "-71,-45", changeMap = "top", gather = true},
		{map = "-71,-46", changeMap = "top", gather = true},
		{map = "-71,-47", changeMap = "top", gather = true},
		{map = "-72,-47", changeMap = "top", gather = true},
		{map = "-72,-46", changeMap = "top", gather = true},
		{map = "-72,-45", changeMap = "top", gather = true},
		{map = "-72,-44", changeMap = "top", gather = true},
		{map = "-73,-44", changeMap = "top", gather = true},
		{map = "-73,-45", changeMap = "top", gather = true},
		{map = "-73,-46", changeMap = "top", gather = true},
		{map = "-74,-45", changeMap = "top", gather = true},
		{map = "-76,-47", changeMap = "top", gather = true},
		{map = "-77,-47", changeMap = "top", gather = true},
		{map = "-78,-47", changeMap = "top", gather = true},
		{map = "-82,-47", changeMap = "top", gather = true},
		{map = "-83,-47", changeMap = "top", gather = true},
		{map = "-84,-46", changeMap = "top", gather = true},
		{map = "-85,-45", changeMap = "top", gather = true},
	}
end

function bank()
	return {
		{map = "191104002", changeMap = "261"}, --Devant banque Astrub--
		{map = "192415750", changeMap = "409"}, --Banque Astrub--
		{map = "54172457", changeMap = "344"}, --Devant banque Frigost--
		{map = "54534165", changeMap = "424", npcBank = true}, --Banque Frigost--
		{map = "147254", changeMap = "283"}, --Devant banque Bonta--
		{map = "2883593", changeMap = "409", npcBank = true}, --Banque Bonta--
		{map = "88081177", changeMap = "203"}, --Devant banque Amakna--
		{map = "99095051", changeMap = "410", npcBank = true}, --Banque Amakna--
		{map = "144931", changeMap = "248"}, --Devant banque Brakmar--
		{map = "8912911", changeMap = "424", npcBank = true}, --Banque Brakmar--
		{map = "90703872", changeMap = "302"}, --Devant banque Sufokia --
		{map = "91753985", changeMap = "494", npcBank = true}, --Banque Sufokia--
		{map = "155157", changeMap = "342"}, --Devant banque Ottomaï--
		{map = "86511105", changeMap = "452", npcBank = true}, --Banque Ottomaï--
		{map = "12580", changeMap = "242"}, --Devant banque Pandala--
		{map = "8129542", changeMap = "409", npcBank = true}, --Banque Pandala--
		{map = "73400323", changeMap = "330"}, --Devant banque Montagne Koalak--
		{map = "84935175", changeMap = "425", npcBank = true}, --Banque Montagne Koalak--
	}
end


function phenix()
	return {
	}
end

function lost()
	global:printMessage("Careful, your bot got lost on "..map:currentPos().." / "..tostring(map:currentMapId()))
end