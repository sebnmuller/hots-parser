__author__ = 'Rodrigo Duenas, Cristian Orellana'

from helpers import *
from data import *


class Team():
    def __init__(self):
        self.id = None
        self.level = 0
        self.memberList = list()
        self.isWinner = None
        self.isLoser = None
        self.periodicXPBreakdown = []
        self.totalXP = 0
        self.totalMinionXP = 0
        self.totalCreepXP = 0
        self.totalStructureXP = 0
        self.totalHeroXP = 0
        self.totalTrickleXP = 0
        self.wastedSoulGems = 0 # Totan number of gems no one took in Tomb of the Spider Queen map
        self.pickedSoulGems = 0
        self.summonedSpiderBosses = 0
        self.spiderBossesNorthTotalAliveTime = 0
        self.spiderBossesCenterTotalAliveTime = 0
        self.spiderBossesSouthTotalAliveTime = 0
        self.spiderBossesTotalAliveTime = 0
        self.totalBuildingsKilledDuringSpiders = 0
        self.totalUnitsKilledDuringSpiders = 0
        self.totalBuildingsKilledDuringNorthSpider = 0
        self.totalUnitsKilledDuringNorthSpider = 0
        self.totalBuildingsKilledDuringCenterSpider = 0
        self.totalUnitsKilledDuringCenterSpider = 0
        self.totalBuildingsKilledDuringSouthSpider = 0
        self.totalUnitsKilledDuringSouthSpider = 0
        self.missedRegenGlobes = 0  # regen globes no one took
        self.luxoriaTemplesCaptured = 0
        self.luxoriaTemplesCapturedSeconds = 0
        self.luxoriaTempleNorthCapturedSeconds = 0
        self.luxoriaTempleNorthCaptured = 0
        self.luxoriaTempleCenterCapturedSeconds = 0
        self.luxoriaTempleCenterCaptured = 0
        self.luxoriaTempleSouthCapturedSeconds = 0
        self.luxoriaTempleSouthCaptured = 0
        self.luxoriaTemplesPct = 0
        self.luxoriaTempleNorthPct = 0
        self.luxoriaTempleCenterPct = 0
        self.luxoriaTempleSouthPct = 0
        self.luxoriaTempleNorthShots = [] # Shots per event for the team. The index is the event number.
        self.luxoriaTempleCenterShots = [] # Shots per event for the team. The index is the event number.
        self.luxoriaTempleSouthShots = []  # Shots per event for the team. The index is the event number.
        self.luxoriaTempleNorthDmg = []
        self.luxoriaTempleCenterDmg = []
        self.luxoriaTempleSouthDmg = []
        self.watchTowersTaken = 0
        self.bossTaken = 0
        self.mercsTaken = 0
        self.siegeCampTaken = 0
        self.plantSumonedAt = []
        self.totalPlantsSummoned = 0
        self.totalPlantsDuration = 0
        self.plantDuration = []
        self.totalUnitsKilledByPlants = []
        self.totalBuildingsKilledByPlants = []
        self.totalBuildingsKilledDuringPlant = []
        self.totalUnitsKilledDuringPlant = []
        self.totalPlantPotsPlaced = 0
        self.plantEffectiveness = []
        self.totalPlantPotsKilled = 0
        self.totalDragonsSummoned = 0
        self.dragonCaptureTimes = [] # in seconds
        self.totalDragonsDuration = 0
        self.dragonDuration = []
        self.totalUnitsKilledBydragons = []
        self.totalBuildingsKilledBydragons = []
        self.dragonEffectiveness = []
        self.totalBuildingsKilledDuringdragon = []
        self.totalUnitsKilledDuringdragon = []
        self.wastedDragonTime = [] # How many seconds the dragon was available to be controlled but no one used it.
        self.totalGolemsSummoned = 0
        self.totalGolemDistanceTraveled = 0
        self.golemDistanceTraveled = []
        self.golemEffectiveness = []
        self.golemDuration = []
        self.totalUnitsKilledByGolem = 0
        self.unitsKilledByGolem = []
        self.totalBuildingsKilledByGolem = 0
        self.buildingsKilledByGolem = []
        self.totalUnitsKilledDuringGolem = 0
        self.unitsKilledDuringGolem = []
        self.totalBuildingsKilledDuringGolem = 0
        self.buildingsKilledDuringGolem = []
        self.totalGolemDuration = 0
        self.totalShipsControlled = 0
        self.totalUnitsKilledDuringShip = []
        self.shipDurations = []
        self.totalBuildingsDestroyedDuringShip = []
        self.ghostShipScore = []
        self.shipEffectiveness = []
        self.summonedPunishers = 0
        self.punisherSummonedAt = []
        self.punisherTotalAliveTime = []
        self.totalBuildingsKilledDuringPunisher = []
        self.totalUnitsKilledDuringPunisher = []
        self.punisherEfectiveness = []
        self.punisherHeroDmg = []
        self.punisherBuildingDmg = []
        self.punisherType = []
        self.levelEvents = []
        self.tributesCapturedAt = [] # When the tribute was captured
        self.totalTowersCaptured = 0 # for Towers of Doom Maps
        self.towersCapturedAtFire = []
        self.towersCapturedAt = []
        self.altarsCapturedAt = [] #When was the altar captured by the team?
        self.totalAltarsCaptured = 0
        self.totalImmortalsSummoned = 0
        self.immortalSummonedAt = []
        self.immortalFightDuration = []
        self.immortalDuration = []
        self.immortalPower = []
        self.immortalEffectiveness = []
        self.unitsKilledDuringImmortal = []
        self.totalUnitsKilledDuringImmortal = 0
        self.buildingsDestroyedDuringImmortal = []
        self.totalBuildingsDestroyedDuringImmortal = 0
        self.curseCaptures = [] #How many tributes the team captured for each curse. 3 = team won the curse
        self.curseActivatedAt = []
        self.totalCursesWon = 0
        self.shrineScore = []

    def add_member(self, hero, players):
        if hero.playerId is not None:
            self.memberList.append(hero.playerId)
            if self.isWinner is None:
                self.id = "Blue" if players[hero.playerId].team == 0 else "Red"
                self.isWinner = players[hero.playerId].is_winner()
                self.isLoser = players[hero.playerId].is_loser()

    def get_total_members(self):
        return len(self.memberList)

    def __str__(self):
        return "%15s\t%15s\t%15s\t%15s" % (self.id, self.level, self.isWinner, self.isLoser)



class Unit():

    def __init__(self):
        self.bornAtX = -1
        self.bornAtY = -1

    def unit_tag(self):
        return (self.unitTagIndex << 18) + self.unitTagRecycle


    def unit_tag_index(self):
        return (self.unitTag >> 18) & 0x00003fff


    def unit_tag_recycle(self):
        return (self.unitTag) & 0x0003ffff

    def is_hero(self):
        return False

class HeroUnit(Unit):

    def __init__(self, e, players):
        # General data
        self.isHuman = False
        self.pickedTalents = [] # list of dicts

            # if a new hero unit is born
        if e['_event'] == 'NNet.Replay.Tracker.SUnitBornEvent' and e['m_unitTypeName'].startswith('Hero'):
            playerId = e['m_upkeepPlayerId'] - 1

            self.playerId = playerId
            self.name = players[playerId].hero
            self.team = players[playerId].team
            self.userId = e['m_upkeepPlayerId'] - 1
            self.internalName = e['m_unitTypeName'][4:]
            self.unitTagIndex = e['m_unitTagIndex']
            self.unitTagRecycle = e['m_unitTagRecycle']
            self.unitTag = self.unit_tag()


        # Metrics
        self.deathCount = 0
        self.deaths = [] # At what point in game (in seconds) the hero died and who killed them
        self.secondsDead = 0 # How many seconds the hero was waiting to resurrect
        self.killCountNeutral = 0 # How many neutral npc units this hero killed?
        self.killCountBuildings = 0 # How many buildings this hero destroyed?
        self.killCountMinions = 0 # How many minions this hero killed?
        self.killCount = 0 # How many units this hero killed (normal minions + heroes + buildings + neutral npcs)
        self.fortsDestroyed = 0 # How many forts this player participated in destroying
        self.takedowns = 0 # How many heroes this hero killed?
        self.assists = 0 # How many assists?
        self.soloKills = 0 # How many solo kills?
        self.totalXP = 0 # XP contributed to the team
        self.totalOutHeal = 0 # How much heal this hero did?
        self.totalSelfHeal = 0 # How much this hero healed himself?
        self.totalIncDamage = 0 # How much damage this hero received
        self.totalSiegeDmg = 0
        self.totalStructureDmg = 0
        self.totalMinionDmg = 0
        self.totalHeroDmg = 0
        self.totalCreepDmg = 0
        self.totalSummonDmg = 0
        self.totalImmortalDmg = 0 # Total damage done to the immortals
        self.totalGemsTurnedIn = 0
        self.secondsCCOnEnemies = 0
        self.maxKillSpree = 0 # maximum number of heroes killed after (if ever) die
        self.capturedBeaconTowers = 0
        self.capturedTributes = 0 # Number of tributes captured by this hero in the Curse map
        self.clickedTributes = 0 # How many times the hero clicked a tribute in the Curse map
        self.gardensSeedsCollected = 0
        self.totalShrineMinionDmg = 0 # Damage inflicted to minions in punisher map
        self.totalSoulsTaken = 0 # How many times the hero collected soul shards on the tomb of the spider queen map
        self.capturedMercCamps = 0
        self.totaltimeInTemples = 0 # How many seconds was the hero holding the temples
        self.regenGlobesTaken = 0
        self.castedAbilities = OrderedDict() # key = gameloops when the ability was casted, value = ability instance
        self.totalPlantsControlled = 0
        self.unitsKilledAsPlant = []
        self.totalUnitsKilledAsPlant = 0
        self.buildingsKilledAsPlant = []
        self.totalBuildingsKilledAsPlant = 0
        self.polymorphedUnits = []
        self.totalPolymorphedUnits = 0
        self.plantPotsPlaced = 0
        self.plantDuration = []
        self.totalPlantPotsPlaced = 0
        self.totalPlantPotsKilled = 0
        self.totalDragonsControlled = 0
        self.totalShrinesCaptured = 0
        self.totalBuildingsKilledAsDragon = []
        self.totalUnitsKilledAsDragon = []
        self.levelEvents = []
        self.totalOutDamage = self.get_total_damage()
        self.coinsTurnedIn = 0
        self.coinsCollected = 0
        self.coinsEffectiveness = 0
        #self.killCount


    def get_total_damage(self):
        return self.totalSiegeDmg + self.totalStructureDmg + self.totalMinionDmg + self.totalHeroDmg + self.totalCreepDmg

    def __str__(self):
        return "%15s\t%15s\t%15s\t%15s\t%15s\t%15s\t%15s\t%15s\t%15s" % (self.name, self.internalName, self.isHuman, self.playerId, self.userId, self.team, self.unitTag, self.deathCount, self.get_total_casted_abilities())

    def get_total_casted_abilities(self):
        return len(self.castedAbilities)

    def get_total_picked_talents(self):
        return len(self.pickedTalents)

    def is_hero(self):
        return True


class HeroReplay():
    def __init__(self, details):
        # General Data
        self.startTime = None # UTC
        self.gameLoops = None # duration of the game in gameloops
        self.speed = 0
        self.gameType = None
        self.gameVersion = None
        self.randomVal = None
        self.mapName = details['m_title']
        self.mapSize = {}
        self.startTime = win_timestamp_to_date(details['m_timeUTC'])
        self.gatesOpenedAt = None # seconds into the game when the gates open
        self.totalCurses = 0


    def duration_in_secs(self):
        if self.gameLoops:
            return self.gameLoops / 16
        else:
            return 0

    def __str__(self):
        return "Title: %s\nStarted at: %s\nDuration (min/gl): %d/%d\nSpeed: %s\nGame Type: %s" % (self.mapName,
        self.startTime,
        self.duration_in_secs()/60,
        self.gameLoops,
        self.speed,
        self.gameType
      )



class Player():

    def __init__(self, player):

        self.userId = None
        self.heroLevel = 1
        self.id = player['m_workingSetSlotId']
        self.team = player['m_teamId']
        self.hero = player['m_hero']
        self.name = player['m_name']
        self.isHuman = (player['m_toon']['m_region'] != 0)
        self.gameResult = int(player['m_result'])
        self.toonHandle = self.get_toon_handle(player)
        self.realm = player['m_toon']['m_realm']
        self.region = player['m_toon']['m_region']
        self.rank = None



    def get_toon_handle(self, player):
        return '-'.join([str(player['m_toon']['m_region']),player['m_toon']['m_programId'],str(player['m_toon']['m_realm']),str(player['m_toon']['m_id'])])

    def __str__(self):
      return "%10s\t%10s\t%10s\t%12s\t%10s\t%15s\t%15s" % (self.id,
        self.team,
        self.hero,
        self.name,
        self.heroLevel,
        self.is_winner(),
        self.toonHandle
      )

    def is_winner(self):
        return self.gameResult == 1

    def is_loser(self):
        return self.gameResult == 2


class GameUnit(Unit):


    def __init__(self, e):
        # General Data

        self.isDead = False
        self.diedAt = -1 # Seconds into the game when it was destroyed (-1 means never died)
        self.diedAtX = None
        self.diedAtY = None
        self.diedAtGameLoops = None
        self.gameLoopsAlive = -1 # -1 means never died.
        self.killerTeam = None
        self.killerTag = None
        self.killerTagIndex = None
        self.killerTagRecycle = None
        self.killerPlayerId = None
        self.ownerList = list() # owner, when, duration (None = forever)
        self.clickerList = OrderedDict() # key = gameloop , value = player id
        self.heroData = None
        self.unitsKilled = 0
        self.buildingsKilled = 0
        self.unitTagIndex = e['m_unitTagIndex']
        self.unitTagRecycle = e['m_unitTagRecycle']
        self.unitTag = self.unit_tag()
        self.bornAt = get_seconds_from_event_gameloop(e) # Seconds into the game when it was created
        self.bornAtGameLoops = get_gameloops(e)
        self.internalName = e['m_unitTypeName'] # Internal unit name
        self.team = e['m_upkeepPlayerId'] - 11 if e['m_upkeepPlayerId'] > 10 else e['m_upkeepPlayerId'] - 1 # Team this unit belongs to, or Hero controlling it at born time (if it's <= 10)
        self.bornAtX = e['m_x']
        self.bornAtY = e['m_y']
        self.positions = OrderedDict() # key seconds, val = dict {'x','y'}
        self.distanceFromKiller = -1;
        if not self.is_plant_vehicle():
            self.positions[self.bornAtGameLoops] = [self.bornAtX, self.bornAtY]


    def is_map_resource(self):
      return self.internalName in PICKUNITS

    def was_picked(self):
      if self.internalName in PICKUNITS:
        return self.gameLoopsAlive < PICKUNITS[self.internalName]
      else:
        return False

    def is_building(self):
        return self.internalName in BUILDINGS

    def is_regen_globe(self):
        return self.internalName in REGEN_GLOBES_PICKABLE

    def is_spider_summon(self):
        return self.internalName == 'SoulEater'

    def is_plant_pot(self):
        return self.internalName == 'PlantHorrorOvergrowthPlant'

    def is_mercenary(self):
        return self.internalName in MERCUNITSNPC or self.internalName in MERCUNITSTEAM

    def is_hired_mercenary(self):
        return self.internalName in MERCUNITSTEAM

    def is_army_unit(self):
        return self.internalName in NORMALUNIT and self.internalName not in PICKUNITS

    def is_pickable_unit(self):
        return self.internalName in PICKUNITS

    def is_tomb_of_the_spider_pickable(self):
        return self.internalName in TOMB_OF_THE_SPIDER_PICKABLE

    def is_seed_pickable(self):
        return self.internalName == 'ItemSeedPickup'

    def is_sky_temple_tower(self):
        return self.internalName in SKY_TEMPLE_TOWER

    def is_beacon(self):
        return self.internalName in BEACONUNIT

    def is_tribute(self):
        return self.internalName in TRIBUTEUNIT

    def is_advanced_unit(self):
        return self.internalName in ADVANCEDUNIT

    def get_death_time(self, total_time):
        return self.diedAt if (self.diedAt >= 0) else total_time

    def is_plant_vehicle(self):
        return self.internalName in PLANT_CONTROLLABLE

    def is_dragon_statue(self):
        return self.internalName in DRAGON_STATUE

    def is_golem(self):
        return self.internalName in GOLEM_UNIT

    def is_golem_body(self):
        return self.internalName in GOLEM_BODY

    def is_ghostship(self):
        return self.internalName in GHOST_SHIP

    def is_punisher(self):
        return self.internalName in PUNISHER_UNIT

    def get_strength(self):
        if self.is_hired_mercenary():
            return MERCUNITSTEAM[self.internalName]
        elif self.is_advanced_unit():
            return ADVANCEDUNIT[self.internalName]
        elif self.is_army_unit():
            return NORMALUNIT[self.internalName]
        elif self.is_building():
            return BUILDINGS[self.internalName]
        else:
            return 0

    def __str__(self):
        val = "%s\t%s\t(%s)\tcreated: %d s (%d,%d) \tdied: %s s\tlifespan: %s gls\tpicked? (%s)\tkilledby: %s" \
                  % (self.unitTag, self.internalName, self.team, self.bornAt, self.bornAtX, self.bornAtY, self.diedAt, self.gameLoopsAlive, self.was_picked(), self.killerPlayerId)
        if len(self.ownerList) > 0:
            val += "\tOwners: %s" % self.ownerList
        if len(self.clickerList) > 0:
            val += "\tTaken by: %s" % (self.get_tribute_controller())
        return val


class BaseAbility():
    """
    Base class for all abilities, has all the common attributes
    """

    def __init__(self, event):
        self.abilityName = None
        self.abilityTag = get_ability_tag(event)
        self.castedAtGameLoops = event['_gameloop']
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']

    def __str__(self):
        return "%s" % self.abilityTag


class TargetPointAbility(BaseAbility):

    def __init__(self, event):

        self.abilityTag = get_ability_tag(event)
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']
        self.castedAtGameLoops = event['_gameloop']
        if event.get('m_data'):
            self.x = event['m_data']['TargetPoint']['x']/4096.0
            self.y = event['m_data']['TargetPoint']['y']/4096.0
            self.z = event['m_data']['TargetPoint']['z']/4096.0
        elif event.get('m_target'):
            self.x = event['m_target']['x']/4096.0
            self.y = event['m_target']['y']/4096.0
            self.z = event['m_target']['z']/4096.0

    def __str__(self):
        return "Skill: %s\tCoords: (%s,%s,%s)" % (self.abilityTag, self.x, self.y, self.z)


class UnitUpgrade():
    def __init__(self, event):
        self.gameloops = event['_gameloop']
        self.upgradedPlayerId = event['m_playerId'] - 1
        self.internalName = event['m_upgradeTypeName']

    def is_dragon_upgrade(self):
        return self.internalName in DRAGON_CONTROLLABLE

class TargetUnitAbility(BaseAbility):

    def __init__(self, event):
        self.abilityTag = get_ability_tag(event)
        self.castedAt = get_seconds_from_event_gameloop(event)
        self.userId = event['_userid']['m_userId']
        self.castedAtGameLoops = event['_gameloop']
        if event.get('m_data'):
            self.x = event['m_data']['TargetUnit']['m_snapshotPoint']['x']/4096.0
            self.y = event['m_data']['TargetUnit']['m_snapshotPoint']['y']/4096.0
            self.z = event['m_data']['TargetUnit']['m_snapshotPoint']['z']/4096.0
            self.targetPlayerId = event['m_data']['TargetUnit']['m_snapshotControlPlayerId']
            self.targetTeamId = event['m_data']['TargetUnit']['m_snapshotUpkeepPlayerId']
            self.targetUnitTag = event['m_data']['TargetUnit']['m_tag']
        elif event.get('m_target'):
            self.x = event['m_target']['m_snapshotPoint']['x']/4096.0
            self.y = event['m_target']['m_snapshotPoint']['y']/4096.0
            self.z = event['m_target']['m_snapshotPoint']['z']/4096.0
            self.targetPlayerId = event['m_target']['m_snapshotControlPlayerId']
            self.targetTeamId = event['m_target']['m_snapshotUpkeepPlayerId']
            self.targetUnitTag = event['m_target']['m_tag']

    def __str__(self):
        return "Skill: %s\tCoords: (%s,%s,%s)\tTarget: %s" % (self.abilityTag, self.x, self.y, self.z, self.targetUnitTag)

