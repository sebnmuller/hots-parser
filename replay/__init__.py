__author__ = 'Rodrigo Duenas, Cristian Orellana'


from models import *
from hashlib import sha256



class Replay:

    EVENT_FILES = {
        'replay.tracker.events': 'decode_replay_tracker_events',
        'replay.game.events': 'decode_replay_game_events'
    }

    replayInfo = None
    unitsInGame = {}
    temp_indexes = {} # key = UnitTagIndex, UnitTag
    timeline = {} # key = when (in seconds), value = event {} key = team - value = description
    heroList = {} # key = playerId - content = hero instance
    upgrades = {} # key = gameloop - content = upgrade instance
    #TODO use a list instead of 2 different variables for the team
    teams = [Team(), Team()]
    abilityList = list()
    time = None
    players = []
    # stores NNet_Game_SCmdUpdateTargetPointEvent events
    utpe = {}
    utue = {}

    def __init__(self, protocol, replayFile):
      self.protocol = protocol
      self.replayFile = replayFile

    def get_replay_id(self):
        _id = list()
        for t in (0,1):
            for h in self.teams[t].memberList:
                _id.append(self.players[h].toonHandle)
        _id = '_'.join(_id)
        id = "%s_%s" % (self.replayInfo.randomVal,_id)
        return sha256(id).hexdigest()

    def process_replay_details(self):
        contents = self.replayFile.read_file('replay.details')
        details = self.protocol.decode_replay_details(contents)
        self.replayInfo = HeroReplay(details)
        self.players = {}
        totalPlayers = 0
        totalHumans = 0
        for player in details['m_playerList']:
            p = Player(player)
            if p.isHuman:
                p.userId = totalHumans
                totalHumans += 1
            else:
                p.userId = -1
            self.players[totalPlayers] = p

            totalPlayers += 1

    def process_replay_initdata(self):
        #return 0
        contents = self.replayFile.read_file('replay.initData')
        initdata = self.protocol.decode_replay_initdata(contents)
        self.replayInfo.randomVal = initdata['m_syncLobbyState']['m_gameDescription']['m_randomValue']
        self.replayInfo.speed = initdata['m_syncLobbyState']['m_gameDescription']['m_gameSpeed']


    def process_replay_header(self):
        contents = self.replayFile.header['user_data_header']['content']
        header = self.protocol.decode_replay_header(contents)
        self.replayInfo.gameLoops = header['m_elapsedGameLoops']
        self.replayInfo.gameVersion = header['m_dataBuildNum']

    def process_replay_attributes(self):
        contents = self.replayFile.read_file('replay.attributes.events')
        attributes = self.protocol.decode_replay_attributes_events(contents)

        # Get if players are human or not
        for playerId in attributes['scopes'].keys():
            # if playerId <= len(self.heroList):
            if self.heroList.get((playerId - 1), None) is not None:
                self.heroList[playerId - 1].isHuman = (attributes['scopes'][playerId][500][0]['value'] == 'Humn')

        # If player is human, get the level this player has for the selected hero
                if self.heroList[playerId - 1].isHuman:
                    self.players[playerId - 1].heroLevel = attributes['scopes'][playerId][4008][0]['value']

        # Get game type
        self.replayInfo.gameType = attributes['scopes'][16][3009][0]['value']


    def get_players_in_game(self):
      return self.players.itervalues()


    def process_replay(self):
      for meta in self.EVENT_FILES:
        contents = self.replayFile.read_file(meta)
        events = getattr(self.protocol, self.EVENT_FILES[meta])(contents)
        for event in events:
          self.process_event(event)

    def get_lifespan_time_in_gameloops(self, unitTag):
        return self.unitsInGame[unitTag].gameLoopsAlive if self.unitsInGame[unitTag].gameLoopsAlive >= 0 \
            else self.replayInfo.gameLoops - self.unitsInGame[unitTag].bornAtGameLoops

    def get_lifespan_time_in_seconds(self, unitTag):
        return get_seconds_from_int_gameloop(self.unitsInGame[unitTag].gameLoopsAlive) \
            if self.unitsInGame[unitTag].gameLoopsAlive >= 0 \
            else self.replayInfo.duration_in_secs() - self.unitsInGame[unitTag].bornAt

    def process_event(self, event):
        event_name = event['_event'].replace('.', '_')

        if hasattr(self, event_name):
          getattr(self, event_name)(event)

    def get_clicked_units(self):
        return [unit for unit in self.unitsInGame.itervalues() if len(unit.clickerList) > 0]

    def process_regen_globes_stats(self):
        """
        This function calculates how many regen globes were not picked up
        :return:
        """
        for capturedUnitTag in self.unitsInGame.keys():
            if self.unitsInGame[capturedUnitTag].is_regen_globe():
                if len(self.unitsInGame[capturedUnitTag].ownerList) == 0:
                        self.teams[self.unitsInGame[capturedUnitTag].team].missedRegenGlobes += 1

    def process_clicked_unit(self,e):
        if e['_event'] != 'NNet.Game.SCmdUpdateTargetUnitEvent':
            return None
        unitTag = e['m_target']['m_tag']
        if unitTag in self.unitsInGame.keys():
            # Process Tributes
            if self.unitsInGame[unitTag].is_tribute():
                playerId = e['_userid']['m_userId']
                self.unitsInGame[unitTag].clickerList[get_gameloops(e)] = playerId
                # Increment Hero clickedTributes attribute
                self.heroList[playerId].clickedTributes += 1


    def calculate_solo_deaths(self):
        """
        Calculates when a hero is dies away from its team mates
        :return:
        """
        weights = [0.10, 0.15, 0.20, 0.40, 0.10, 0.05]
        for hero in self.heroList:
            if self.heroList[hero].deathCount > 0:
                #kill = {'killers': killers, 'x': x, 'y': y, 'gameloops': gl, 'seconds': get_seconds_from_int_gameloop(gl)}
                team = self.heroList[hero].team
                # the idea with weights is that the most important distance is the one between the victim and the
                # allies at the exact moment the victim died (the 0.4)

                for death in self.heroList[hero].deaths:
                    #print "\nVictim %s" % self.heroList[hero].name
                    away_allies = 0 # How many allies were far away when the hero died, ideally should be 0
                    totalKillers = len(death['killers'])
                    seconds =  death['seconds']
                    victim_x = death['x']
                    victim_y = death['y']
                    allies = [player for player in self.teams[team].memberList if hero <> player]
                    allied_dist = {}
                    w_dist = None
                    for allied in allies:
                        allied_dist[allied] = []
                        alliedTag = self.heroList[allied].unitTag
                        duration = self.replayInfo.duration_in_secs()
                        # just calculate the position for the allied in a small vicinity of seconds
                        positions = get_position_by_second(self.unitsInGame[alliedTag],
                                                           duration,
                                                           seconds-15,
                                                           seconds+15)
                        # get the positions for the allied player in a window of 6 seconds
                        for s in xrange(seconds-3, seconds+3):
                            if positions.get(s):
                                allied_x = positions[s][0]
                                allied_y = positions[s][1]
                                allied_dist[allied].append(calculate_distance(victim_x, victim_y, allied_x, allied_y))
                        w_dist = calculate_weighted_average(allied_dist[allied], weights)
                        if w_dist >= 10:
                            away_allies += 1
                    if away_allies >= 3:
                        self.heroList[hero].soloDeathsCount += 1
                        death['soloDeath'] = True
                    else:
                        death['soloDeath'] = False






    def process_cursed_hollow(self):
        return None
         # for capturedUnitTag in self.unitsInGame.keys():
         #    candidates = {}
         #    if self.unitsInGame[capturedUnitTag].is_tribute():
         #        # Capturer is the last player that clicked the tribute before it "die"
         #        for loop in self.unitsInGame[capturedUnitTag].clickerList.keys():
         #            if self.unitsInGame[capturedUnitTag].diedAtGameLoops:
         #                if (int(self.unitsInGame[capturedUnitTag].diedAtGameLoops) - int(loop)) in xrange(97,120):
         #                    candidates[int(self.unitsInGame[capturedUnitTag].diedAtGameLoops) - int(loop)] = loop
         #
         #        if len(candidates) > 0:
         #            minloop = min(candidates.keys())
         #            capturerId = self.unitsInGame[capturedUnitTag].clickerList[candidates[minloop]]
         #        # if no click in the range, just take the last one (sometime happens)
         #        else:
         #            if self.unitsInGame[capturedUnitTag].diedAtGameLoops: # discard last clickers of
         #            non-taken tributes (i.e. the game ends while someone clicked a tribute)
         #                lastLoop = self.unitsInGame[capturedUnitTag].clickerList.keys()[-1]
         #                capturerId = self.unitsInGame[capturedUnitTag].clickerList[lastLoop]
         #                print "%s captured by %s at %s" % (i, self.heroList[capturerId].name, lastLoop)


    # TODO Add per spider stats
    def process_tomb_of_the_spider_queen(self):
        for unitTag in self.unitsInGame.keys():
            if self.unitsInGame[unitTag].is_tomb_of_the_spider_pickable():
                # process non-picked souls
                if self.unitsInGame[unitTag].gameLoopsAlive == PICKUNITS[self.unitsInGame[unitTag].internalName]:
                    team = self.unitsInGame[unitTag].team
                    self.teams[team].wastedSoulGems += 1
                # process picked souls
                else:
                    team = self.unitsInGame[unitTag].team
                    self.teams[team].pickedSoulGems += 1
            # process spider boss
            # get how many seconds each spider lived
            # get how many structures died in the lane the spider was
            elif self.unitsInGame[unitTag].is_spider_summon():
                duration = self.get_lifespan_time_in_seconds(unitTag)
                team = self.unitsInGame[unitTag].team
                self.teams[team].summonedSpiderBosses += 1
                self.teams[team].spiderBossesTotalAliveTime += duration
                self.teams[team].totalBuildingsKilledDuringSpiders +=  self.unitsInGame[unitTag].buildingsKilled
                self.teams[team].totalUnitsKilledDuringSpiders += self.unitsInGame[unitTag].unitsKilled
                # update the duration of each spider
                if SOUL_EATER_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'North':
                    self.teams[team].spiderBossesNorthTotalAliveTime += duration
                elif SOUL_EATER_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'Center':
                    self.teams[team].spiderBossesCenterTotalAliveTime += duration
                elif SOUL_EATER_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'South':
                    self.teams[team].spiderBossesSouthTotalAliveTime += duration

                for unit in self.unitsInGame.keys():
                    targetDiedAt = self.unitsInGame[unit].diedAtGameLoops
                    spiderY = self.unitsInGame[unitTag].bornAtY
                    targetDiedY = self.unitsInGame[unit].diedAtY
                    bornAt = self.unitsInGame[unitTag].bornAtGameLoops
                    diedAt = self.unitsInGame[unitTag].diedAtGameLoops if \
                        self.unitsInGame[unitTag].diedAtGameLoops is not None \
                        else self.replayInfo.gameLoops
                    if targetDiedAt in xrange(bornAt, diedAt + 1) and \
                                    targetDiedY in xrange(spiderY - 20, spiderY + 21) and \
                                    self.unitsInGame[unit].team != team:
                        if self.unitsInGame[unit].is_building():
                            self.teams[team].totalBuildingsKilledDuringSpiders += 1
                        elif self.unitsInGame[unit].is_hired_mercenary() or \
                                self.unitsInGame[unit].is_army_unit() or \
                                self.unitsInGame[unit].is_advanced_unit():
                            self.teams[team].totalUnitsKilledDuringSpiders += 1
                        if SOUL_EATER_POSITIONS[spiderY] == 'North':
                            if self.unitsInGame[unit].is_building():
                                self.teams[team].totalBuildingsKilledDuringNorthSpider += 1
                            elif self.unitsInGame[unit].is_hired_mercenary() or \
                                    self.unitsInGame[unit].is_army_unit() or \
                                    self.unitsInGame[unit].is_advanced_unit():
                                self.teams[team].totalUnitsKilledDuringNorthSpider += 1
                        if SOUL_EATER_POSITIONS[spiderY] == 'Center':
                            if self.unitsInGame[unit].is_building():
                                self.teams[team].totalBuildingsKilledDuringCenterSpider += 1
                            elif self.unitsInGame[unit].is_hired_mercenary() or \
                                    self.unitsInGame[unit].is_army_unit() or \
                                    self.unitsInGame[unit].is_advanced_unit():
                                self.teams[team].totalUnitsKilledDuringCenterSpider += 1
                        if SOUL_EATER_POSITIONS[spiderY] == 'South':
                            if self.unitsInGame[unit].is_building():
                                self.teams[team].totalBuildingsKilledDuringSouthSpider += 1
                            elif self.unitsInGame[unit].is_hired_mercenary() or \
                                    self.unitsInGame[unit].is_army_unit() or \
                                    self.unitsInGame[unit].is_advanced_unit():
                                self.teams[team].totalUnitsKilledDuringSouthSpider += 1

    def process_blackhearts_bay(self):
        for hero in self.heroList:
            turned = self.heroList[hero].coinsTurnedIn
            collected = self.heroList[hero].coinsCollected
            self.heroList[hero].coinsEffectiveness = 100*round((float(turned)/float(collected)),4) \
                if self.heroList[hero].coinsTurnedIn > 0 else 0
        for unitTag in self.unitsInGame.keys():
            unit = self.unitsInGame[unitTag]
            if unit.internalName == GHOST_SHIP:
                for team, when, duration in unit.ownerList:
                    if team in xrange(0, len(self.teams)):
                        effectiveness = 0
                        units_killed = 0
                        buildings_destroyed = 0
                        for u in self.unitsInGame.keys():
                            enemy = self.unitsInGame[u]
                            if enemy.diedAtGameLoops is not None:
                                    if enemy.team != unit.team and enemy != unit and \
                                        enemy.get_death_time(self.replayInfo.duration_in_secs()) in \
                                        xrange(when, when + duration + 1) and enemy.isDead:
                                        effectiveness += enemy.get_strength()
                                        if enemy.is_building():
                                            buildings_destroyed += 1
                                        else:
                                            units_killed += 1
                        self.teams[team].totalUnitsKilledDuringShip.append(units_killed)
                        self.teams[team].totalBuildingsDestroyedDuringShip.append(buildings_destroyed)
                        self.teams[team].shipEffectiveness.append(effectiveness)
                        self.teams[team].totalShipsControlled += 1
                        self.teams[team].shipDurations.append(duration)



    def process_infernal_shrines(self):
        for unitTag in self.unitsInGame.keys():
            if self.unitsInGame[unitTag].is_punisher():
                created_at = self.unitsInGame[unitTag].bornAt
                died_at = self.unitsInGame[unitTag].diedAt if self.unitsInGame[unitTag].diedAt > 0 \
                    else self.replayInfo.duration_in_secs()
                team = self.unitsInGame[unitTag].team
                punisher_efectiveness = 0
                buildings_killed_during = 0
                units_killed_during = 0
                positions = get_position_by_second(self.unitsInGame[unitTag], self.replayInfo.duration_in_secs())
                try:
                    for unit in self.unitsInGame.keys():
                        if self.unitsInGame[unit].diedAtGameLoops is not None:
                            if self.unitsInGame[unit].team != team and unit != unitTag and \
                                self.unitsInGame[unit].get_death_time(self.replayInfo.duration_in_secs()) in \
                                            xrange(created_at, died_at + 1) and self.unitsInGame[unit].isDead:
                                if self.unitsInGame[unit].is_hired_mercenary() or \
                                        self.unitsInGame[unit].is_army_unit() or \
                                        self.unitsInGame[unit].is_advanced_unit() or \
                                        self.unitsInGame[unit].is_building():
                                    targetDiedAt = self.unitsInGame[unit].diedAtGameLoops # when the unit died
                                    targetDiedY = self.unitsInGame[unit].diedAtY # Y coord when unit died
                                    targetDiedX = self.unitsInGame[unit].diedAtX # X coord when unit died
                                    punisher_x = positions[get_seconds_from_int_gameloop(targetDiedAt)][0]
                                    # X coord of punisher when unit died
                                    punisher_y = positions[get_seconds_from_int_gameloop(targetDiedAt)][1]
                                    # Y coord of punisher when unit died
                                    distance = calculate_distance(targetDiedX, targetDiedY, punisher_x, punisher_y)
                                    self.unitsInGame[unit].distanceFromKiller = distance
                                    if distance > 0:
                                        punisher_efectiveness += 10/distance * self.unitsInGame[unit].get_strength()
                                        # that 10 is just a made up number LOL
                                    if self.unitsInGame[unit].is_building():
                                        buildings_killed_during += 1
                                    else:
                                        units_killed_during += 1
                except Exception, e:
                    print e
                self.teams[team].totalBuildingsKilledDuringPunisher.append(buildings_killed_during)
                self.teams[team].totalUnitsKilledDuringPunisher.append(units_killed_during)
                self.teams[team].punisherEfectiveness.append(punisher_efectiveness)




    def process_dragon_shire(self):

        dragon_creation_time = {}

        for unitTag in self.unitsInGame.keys():
            if self.unitsInGame[unitTag].is_dragon_statue():
                # Populate list of dragons statues
                dragon_creation_time[self.unitsInGame[unitTag].bornAtGameLoops] = self.unitsInGame[unitTag]
        dragon_creation_time_sorted = sorted(dragon_creation_time.keys(), key=lambda s: s)


        for upgrade in self.upgrades.keys():

            if self.upgrades[upgrade].is_dragon_upgrade():
                dragon_effectiveness = 0
                units_killed_during = 0
                buildings_killed_during = 0
                dragon_unit = dragon_creation_time[max([gl for gl in dragon_creation_time_sorted if gl < upgrade])]
                contested_time = sum([(dur or 0) for team, when, dur in dragon_unit.ownerList if team == -1 and
                                      when not in dragon_creation_time])
                wasted_dragon_time_t0 = sum([(dur or 0) for team, when, dur in dragon_unit.ownerList if team == 0 and
                                             when not in dragon_creation_time])
                wasted_dragon_time_t1 = sum([(dur or 0)for team, when, dur in dragon_unit.ownerList if team == 1 and
                                             when not in dragon_creation_time])
                dragon_created_at = get_seconds_from_int_gameloop(self.upgrades[upgrade].gameloops)
                dragon_unit.positions[self.upgrades[upgrade].gameloops] = [dragon_unit.bornAtX, dragon_unit.bornAtY]
                dragon_unit.bornAtGameLoops = self.upgrades[upgrade].gameloops
                controller_of_dragon = self.upgrades[upgrade].upgradedPlayerId
                team = self.heroList[controller_of_dragon].team
                diedAt = dragon_unit.get_death_time(self.replayInfo.duration_in_secs())
                positions = get_position_by_second(dragon_unit, self.replayInfo.duration_in_secs())
                dragon_duration_in_secs = diedAt - dragon_created_at
                totalUnits =  dragon_unit.unitsKilled
                totalBuildings = dragon_unit.buildingsKilled
                # Calculate how many units were killed while the dragon was active
                # also calculate how far the unit was from the dragon at destruction time
                try:
                    for unit in self.unitsInGame.keys():
                        if self.unitsInGame[unit].diedAtGameLoops is not None:
                            victimTeam = self.unitsInGame[unit].team
                            dragonTeam = self.heroList[controller_of_dragon].team
                            victimDeathTime = self.unitsInGame[unit].get_death_time(self.replayInfo.duration_in_secs())
                            isMercenary = self.unitsInGame[unit].is_hired_mercenary()
                            isArmy = self.unitsInGame[unit].is_army_unit()
                            isAdvanced = self.unitsInGame[unit].is_advanced_unit()
                            isBuilding = self.unitsInGame[unit].is_building()
                            # if the unit died, it's not the dragon, it's not on the same team as the dragon
                            # and the victim's death time is between the time the dragon was active
                            # and if the unit is a mercenary, normal army, advanced unit or building, then calculate
                            if victimTeam != dragonTeam and unit != dragon_unit.unitTag \
                                    and victimDeathTime in xrange(dragon_created_at, diedAt + 1) \
                                    and self.unitsInGame[unit].isDead \
                                    and (isMercenary or isArmy or isAdvanced or isBuilding):
                                targetDiedAt = self.unitsInGame[unit].diedAtGameLoops # when the unit died
                                targetDiedY = self.unitsInGame[unit].diedAtY # Y coord when unit died
                                targetDiedX = self.unitsInGame[unit].diedAtX # X coord when unit died
                                dragon_x = positions[get_seconds_from_int_gameloop(targetDiedAt)][0] # X coord of dragon
                                dragon_y = positions[get_seconds_from_int_gameloop(targetDiedAt)][1] # Y coord of dragon
                                distance_from_dragon = calculate_distance(targetDiedX, targetDiedY, dragon_x, dragon_y)
                                if distance_from_dragon > 0:
                                    dragon_effectiveness +=10/distance_from_dragon*self.unitsInGame[unit].get_strength()
                                if self.unitsInGame[unit].is_building():
                                    buildings_killed_during += 1
                                else:
                                    units_killed_during += 1
                except Exception:
                    pass
                # Update team stats
                self.teams[0].wastedDragonTime.append(wasted_dragon_time_t0)
                self.teams[1].wastedDragonTime.append(wasted_dragon_time_t1)
                self.teams[team].dragonCaptureTimes.append(get_seconds_from_int_gameloop(dragon_unit.bornAtGameLoops))
                self.teams[team].dragonDuration.append(dragon_duration_in_secs)
                self.teams[team].totalDragonsDuration += dragon_duration_in_secs
                self.teams[team].totalUnitsKilledBydragons.append(totalUnits)
                self.teams[team].totalBuildingsKilledBydragons.append(totalBuildings)
                self.teams[team].dragonEffectiveness.append(round(dragon_effectiveness,2))
                self.teams[team].totalBuildingsKilledDuringdragon.append(buildings_killed_during)
                self.teams[team].totalUnitsKilledDuringdragon.append(units_killed_during)
                self.teams[team].totalDragonsSummoned += 1
                # Update Hero Stats
                self.heroList[controller_of_dragon].totalDragonsControlled += 1
                self.heroList[controller_of_dragon].totalUnitsKilledAsDragon.append(units_killed_during)
                self.heroList[controller_of_dragon].totalBuildingsKilledAsDragon.append(buildings_killed_during)
                self.heroList[controller_of_dragon].dragonEffectiveness.append(round(dragon_effectiveness,2))
                self.heroList[controller_of_dragon].dragonCaptureTimes.append(get_seconds_from_int_gameloop(dragon_unit.bornAtGameLoops))


    def process_garden_of_terror(self):
        for unitTag in self.unitsInGame.keys():

            if self.unitsInGame[unitTag].is_plant_vehicle():
                #print "Plant Count %s " % plant_count
                # When a hero clicks on the Overgrowth plant 2 things happen:
                # 1.- PlantHorrorOvergrowthPlant unit is created, the m_upkeepPlayerId of
                # this unit is the controller of the plant
                # 2.- VehiclePlantHorror unit is created, this is the actual unit the player controlls
                # After the unit dies (by time up or damage) two things happen:
                # 1.- There is a unitDie event for the unit, so we can get the diedAtGameLoop
                # 2.- there is a NNet.Replay.Tracker.SUnitOwnerChangeEvent event the m_upkeepPlayerId is the same as
                # the one who created the plant
                # Notes:
                # * There is also a NNet.Game.SCmdUpdateTargetUnitEvent in gameevent it doesn't add any new info.
                # Update hero count
                # Update Team Stats
                if len(self.unitsInGame[unitTag].ownerList) > 0: # if the unit was controlled
                    plant_effectiveness = 0
                    units_killed_during = 0
                    buildings_killed_during = 0
                    positions = get_position_by_second(self.unitsInGame[unitTag], self.replayInfo.duration_in_secs())
                    bornAt = self.unitsInGame[unitTag].ownerList[0][1]

                    diedAt = self.unitsInGame[unitTag].get_death_time(self.replayInfo.duration_in_secs())
                    plant_duration_in_secs = diedAt - self.unitsInGame[unitTag].ownerList[0][1]
                    controller_playerId = self.unitsInGame[unitTag].ownerList[0][0]
                    totalUnits =  self.unitsInGame[unitTag].unitsKilled
                    totalBuildings = self.unitsInGame[unitTag].buildingsKilled


                    # Get units that died while this plant was active. Include only those who were near the unit.
                    try:
                        for unit in self.unitsInGame.keys():
                            if self.unitsInGame[unit].diedAtGameLoops is not None:
                                if self.unitsInGame[unit].team != self.heroList[controller_playerId].team and \
                                        unit != unitTag and \
                                        self.unitsInGame[unit].get_death_time(self.replayInfo.duration_in_secs()) in\
                                        xrange(bornAt, diedAt + 1) and self.unitsInGame[unit].isDead:
                                    if self.unitsInGame[unit].is_hired_mercenary() or \
                                            self.unitsInGame[unit].is_army_unit() or \
                                            self.unitsInGame[unit].is_advanced_unit() or \
                                            self.unitsInGame[unit].is_building():
                                        duration = self.replayInfo.duration_in_secs()
                                        # when the unit died
                                        targetDiedAt = self.unitsInGame[unit].get_death_time(duration)
                                        diedY = self.unitsInGame[unit].diedAtY # Y coord when unit died
                                        diedX = self.unitsInGame[unit].diedAtX # X coord when unit died
                                        plant_x = positions[targetDiedAt][0] # X coord of plant when unit died
                                        plant_y = positions[targetDiedAt][1] # Y coord of plant when unit died
                                        distance_from_plant = calculate_distance(diedX, diedY, plant_x, plant_y)
                                        if distance_from_plant > 0:
                                            plant_effectiveness += 10/distance_from_plant * \
                                                                   self.unitsInGame[unit].get_strength()
                                            # that 10 is just a made up number LOL
                                        if self.unitsInGame[unit].is_building():
                                            buildings_killed_during += 1
                                        else:
                                            units_killed_during += 1
                    except Exception:
                        pass

                    team = self.unitsInGame[unitTag].team

                    # Update teams stats
                    if self.unitsInGame[unitTag].team in xrange(0,len(self.teams)):
                        self.teams[team].totalPlantsSummoned += 1
                        self.teams[team].totalPlantsDuration += plant_duration_in_secs
                        self.teams[team].plantDuration.append(plant_duration_in_secs)
                        self.teams[team].totalUnitsKilledByPlants.append(totalUnits)
                        self.teams[team].totalBuildingsKilledByPlants.append(totalBuildings)
                        self.teams[team].plantEffectiveness.append(round(plant_effectiveness,2))
                        self.teams[team].totalBuildingsKilledDuringPlant.append(buildings_killed_during)
                        self.teams[team].totalUnitsKilledDuringPlant.append(units_killed_during)
                    # Update Hero Stats
                    self.heroList[controller_playerId].totalPlantsControlled += 1
                    self.heroList[controller_playerId].unitsKilledAsPlant.append(units_killed_during)
                    self.heroList[controller_playerId].totalUnitsKilledAsPlant += units_killed_during
                    self.heroList[controller_playerId].buildingsKilledAsPlant.append(buildings_killed_during)
                    self.heroList[controller_playerId].totalBuildingsKilledAsPlant += buildings_killed_during
                    self.heroList[controller_playerId].plantDuration.append(plant_duration_in_secs)

            if self.unitsInGame[unitTag].is_plant_pot():
                pot = self.unitsInGame[unitTag]
                team = pot.team
                # get pot duration, if the pot never dies (ie the game ends with the pot alive) then calculate
                # the duration as end game time - birth time
                if team in xrange(0,len(self.teams)):
                    potDuration = pot.gameLoopsAlive if pot.gameLoopsAlive > -1 \
                        else (self.replayInfo.gameLoops - pot.bornAtGameLoops)
                    self.teams[team].totalPlantPotsPlaced += 1
                    self.teams[team].planPotDuration.append(get_seconds_from_int_gameloop(potDuration))
                    self.teams[team].totalPlantPotDuration += get_seconds_from_int_gameloop(potDuration)
                    if self.unitsInGame[unitTag].killerTag is not None:
                        self.teams[abs(team - 1)].totalPlantPotsKilled += 1 # abs(team - 1) because is rival team


    def process_haunted_mines(self):

        golem_body_positions = {}
        units_killed_during_golem = 0
        buildings_destroyed_during_golem = 0
        golem_effectiveness = 0
        golems = {}


        for unitTag in self.unitsInGame.keys():
            if self.unitsInGame[unitTag].is_golem_body():
                golem_body_positions[self.unitsInGame[unitTag].bornAtGameLoops] = self.unitsInGame[unitTag]


            elif self.unitsInGame[unitTag].is_golem():
                if self.unitsInGame[unitTag].bornAtX == 0 and self.unitsInGame[unitTag].bornAtY == 0:
                    position = [gl for gl in golem_body_positions.keys() if gl <= self.unitsInGame[unitTag].bornAtGameLoops]
                    if len(position) > 0:
                        self.unitsInGame[unitTag].bornAtX = golem_body_positions[position[-1]].bornAtX
                        self.unitsInGame[unitTag].bornAtY = golem_body_positions[position[-1]].bornAtY
                team = self.unitsInGame[unitTag].team
                golems[self.unitsInGame[unitTag].bornAtGameLoops] = self.unitsInGame[unitTag]
                bornAt = self.unitsInGame[unitTag].bornAt
                diedAt = self.unitsInGame[unitTag].get_death_time(self.replayInfo.duration_in_secs())
                # if the unit was alive at the end of the game, then update the positions.
                if diedAt == self.replayInfo.duration_in_secs():
                    self.unitsInGame[unitTag].diedAtGameLoops = self.replayInfo.gameLoops
                    # use last known position
                    last_known_position = self.unitsInGame[unitTag].positions.keys()[-1]
                    last_x = self.unitsInGame[unitTag].positions[last_known_position][0]
                    last_y = self.unitsInGame[unitTag].positions[last_known_position][1]
                    self.unitsInGame[unitTag].positions[self.replayInfo.gameLoops] = [last_x, last_y]

                positions = get_position_by_second(self.unitsInGame[unitTag], self.replayInfo.duration_in_secs())
                distance_traveled = calculate_distance(self.unitsInGame[unitTag].bornAtX,
                    self.unitsInGame[unitTag].positions[self.unitsInGame[unitTag].diedAtGameLoops][0],
                    self.unitsInGame[unitTag].bornAtY,
                    self.unitsInGame[unitTag].positions[self.unitsInGame[unitTag].diedAtGameLoops][1])


                golem_duration_in_secs = diedAt - bornAt
                units_killed_by_golem =  self.unitsInGame[unitTag].unitsKilled
                buildings_destroyed_by_golem = self.unitsInGame[unitTag].buildingsKilled
                for unit in self.unitsInGame.keys():
                    if self.unitsInGame[unit].team != team and \
                                    unit != unitTag and \
                                    self.unitsInGame[unit].get_death_time(self.replayInfo.duration_in_secs()) in \
                                    xrange(bornAt, diedAt + 1) and \
                            self.unitsInGame[unit].isDead:
                        if self.unitsInGame[unit].is_hired_mercenary() or \
                                self.unitsInGame[unit].is_army_unit() or \
                                self.unitsInGame[unit].is_advanced_unit() or \
                                self.unitsInGame[unit].is_building():
                            targetDiedAt = self.unitsInGame[unit].get_death_time(self.replayInfo.duration_in_secs())
                            # when the unit died
                            targetDiedY = self.unitsInGame[unit].diedAtY # Y coord when unit died
                            targetDiedX = self.unitsInGame[unit].diedAtX # X coord when unit died
                            golem_x = positions[targetDiedAt][0] # X coord of plant when unit died
                            golem_y = positions[targetDiedAt][1] # Y coord of plant when unit died
                            distance_from_golem = calculate_distance(targetDiedX, targetDiedY, golem_x, golem_y)
                            if distance_from_golem > 0:
                                golem_effectiveness += 10/distance_from_golem * self.unitsInGame[unit].get_strength()
                                # that 10 is just a made up number LOL
                            if self.unitsInGame[unit].is_building():
                                buildings_destroyed_during_golem += 1
                            else:
                                units_killed_during_golem += 1

                team = self.unitsInGame[unitTag].team
                self.teams[team].totalGolemsSummoned += 1
                self.teams[team].totalGolemDuration += golem_duration_in_secs
                self.teams[team].golemDuration.append(golem_duration_in_secs)
                self.teams[team].totalUnitsKilledByGolem += units_killed_by_golem
                self.teams[team].totalBuildingsKilledByGolem += buildings_destroyed_by_golem
                self.teams[team].totalUnitsKilledDuringGolem += units_killed_during_golem
                self.teams[team].totalGolemDistanceTraveled += distance_traveled
                self.teams[team].unitsKilledByGolem.append(units_killed_by_golem)
                self.teams[team].buildingsKilledByGolem.append(buildings_destroyed_by_golem)
                self.teams[team].unitsKilledDuringGolem.append(units_killed_during_golem)
                self.teams[team].golemDistanceTraveled.append(distance_traveled)

    def process_sky_temple(self):
        for unitTag in self.unitsInGame.keys():
            if self.unitsInGame[unitTag].internalName == 'LuxoriaTemple':
                for team, seconds, duration in self.unitsInGame[unitTag].ownerList:
                    if team in xrange(0,len(self.teams)):
                        self.teams[team].luxoriaTemplesCaptured += 1
                        self.teams[team].luxoriaTemplesCapturedSeconds += duration or \
                                                                        self.replayInfo.duration_in_secs() - seconds
                        if SKY_TEMPLE_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'North':
                            self.teams[team].luxoriaTempleNorthCaptured += 1
                            self.teams[team].luxoriaTempleNorthCapturedSeconds += duration or \
                                                                        self.replayInfo.duration_in_secs() - seconds
                        elif SKY_TEMPLE_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'Center':
                            self.teams[team].luxoriaTempleCenterCaptured += 1
                            self.teams[team].luxoriaTempleCenterCapturedSeconds += duration or \
                                                                        self.replayInfo.duration_in_secs() - seconds
                        elif SKY_TEMPLE_POSITIONS[self.unitsInGame[unitTag].bornAtY] == 'South':
                            self.teams[team].luxoriaTempleSouthCaptured += 1
                            self.teams[team].luxoriaTempleSouthCapturedSeconds += duration or \
                                                                        self.replayInfo.duration_in_secs() - seconds

    def process_map_events(self):
        # Run a custom logic for each map
        map_name = self.replayInfo.mapName.replace('\'','').replace(' ', '_').lower()
        process_name = 'process_' + map_name
        if hasattr(self, process_name):
            getattr(self, process_name)()

    def process_generic_events(self):
        self.process_regen_globes_stats()
        self.calculate_solo_deaths()

    def get_unit_destruction(self, e):
        """
        Gets information when a non-hero unit is destroyed
        """
        if e['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent':
            deadUnitTag = get_unit_tag(e)

            self.unitsInGame[deadUnitTag].diedAt = get_seconds_from_event_gameloop(e)
            self.unitsInGame[deadUnitTag].isDead = True
            self.unitsInGame[deadUnitTag].diedAtX = e['m_x']
            self.unitsInGame[deadUnitTag].diedAtY = e['m_y']
            self.unitsInGame[deadUnitTag].diedAtGameLoops = get_gameloops(e)
            self.unitsInGame[deadUnitTag].gameLoopsAlive = self.unitsInGame[deadUnitTag].diedAtGameLoops - \
                                                           self.unitsInGame[deadUnitTag].bornAtGameLoops
            self.unitsInGame[deadUnitTag].killerPlayerId = e['m_killerPlayerId']
            self.unitsInGame[deadUnitTag].positions[get_gameloops(e)] = [e['m_x'], e['m_y']]

            if self.unitsInGame[deadUnitTag].is_plant_vehicle():
                self.unitsInGame[deadUnitTag].ownerList[0][2] = self.unitsInGame[deadUnitTag].diedAt - \
                                                                self.unitsInGame[deadUnitTag].ownerList[0][1]

            if self.temp_indexes.get(deadUnitTag):
                del self.temp_indexes[deadUnitTag]


    def units_in_game(self):
      return self.unitsInGame.itervalues()

    def heroes_in_game(self):
      return self.heroList.itervalues()

    def calculate_army_strength(self):
        """
        Calculate the relative army strength of the team, that's it the accumulated sum of
        strengths of each unit belonging to the team, each second.
        """
        self.army_strength = [
        [[t, 0] for t in xrange(1, self.replayInfo.duration_in_secs() + 1)],
        [[t, 0] for t in xrange(1, self.replayInfo.duration_in_secs() + 1)]
      ]


        self.merc_strength = [
        [[t, 0] for t in xrange(1, self.replayInfo.duration_in_secs() + 1)],
        [[t, 0] for t in xrange(1, self.replayInfo.duration_in_secs() + 1)]
      ]

        for unit in self.units_in_game():
            if unit.team not in xrange(0,len(self.teams)) and \
                    (
                                    not unit.is_army_unit() or
                                    not unit.is_hired_mercenary()
                                    or not unit.is_advanced_unit()
                    ):
                continue

        end = unit.get_death_time(self.replayInfo.duration_in_secs())

        for second in xrange(unit.bornAt, end + 1):
            try:
                self.army_strength[unit.team][second][1] += unit.get_strength()

                if unit.is_mercenary():
                    self.merc_strength[unit.team][second][1] += unit.get_strength()
            except IndexError:
              # for some cosmic reason some events are happening after the game is over D:
              pass

    def NNet_Replay_Tracker_SUpgradeEvent(self, event):
        """
        Process an upgrade i.e. Dragon
        """
        if event['_event'] != 'NNet.Replay.Tracker.SUpgradeEvent':
            return None
        upgrade = UnitUpgrade(event)
        if upgrade:
            self.upgrades[upgrade.gameloops] = upgrade

    def NNet_Replay_Tracker_SUnitBornEvent(self, event):
        """
        This function process the events of the type NNet.Replay.Tracker.SUnitBornEvent
        """

        if event['_event'] != 'NNet.Replay.Tracker.SUnitBornEvent':
            return None

        # Populate Heroes
        isHero = False
        # TODO change this to use the new events
        if event['m_unitTypeName'].startswith('Hero') and event['m_unitTypeName'] not in \
                ('ChenFire', 'ChenStormConduit', 'ChenEarthConduit', 'ChenFireConduit'):
            hero = HeroUnit(event, self.players)
            if hero:
                isHero = True
                self.heroList[hero.playerId] = hero
                # create/update team
                if hero.playerId not in self.teams[hero.team].memberList:
                    self.teams[hero.team].add_member(hero, self.players)


        # Populate unitsInGame
        unit = GameUnit(event)
        if unit:
            self.unitsInGame[unit.unitTag] = unit
            self.unitsInGame[unit.unitTag].isHero = isHero
            self.temp_indexes[unit.unitTagIndex] = unit.unitTag

    def NNet_Replay_Tracker_SScoreResultEvent(self, event):
        # Sometimes there are several SScoreResultEvent so we just overwrite the values
        # and assume the last entry has the final values (maybe reconnects?)
        if len(self.heroList) > 0:
            for instance in event['m_instanceList']:
                name = instance['m_name']
                if name == 'Takedowns':
                    for hero in xrange(0,10): #There are 15 slots declared, maybe the other 5 are spectators?
                        self.heroList[hero].takedowns = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'SoloKill':
                    for hero in xrange(0,10):
                        self.heroList[hero].soloKills = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'Assists':
                    for hero in xrange(0,10):
                        self.heroList[hero].assists = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'ExperienceContribution':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalXP = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'Healing':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalOutHeal = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'SiegeDamage':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalSiegeDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalSiegeDmg
                elif name == 'StructureDamage':
                    for hero in xrange(0,10): #Get ratios xp/dmg
                        self.heroList[hero].totalStructureDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalStructureDmg
                elif name == 'MinionDamage':
                    for hero in xrange(0,10): #Get ratios xp/dmg
                        self.heroList[hero].totalMinionDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalMinionDmg
                elif name == 'HeroDamage':
                    for hero in xrange(0,10): #Get ratios xp/dmg
                        self.heroList[hero].totalHeroDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalHeroDmg
                elif name == 'MercCampCaptures':
                    for hero in xrange(0,10): #Get ratios xp/dmg
                        self.heroList[hero].capturedMercCamps = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'WatchTowerCaptures':
                    for hero in xrange(0,10):
                        self.heroList[hero].capturedBeaconTowers = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'SelfHealing':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalSelfHeal = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'TimeCCdEnemyHeroes':
                    for hero in xrange(0,10):
                        self.heroList[hero].secondsCCOnEnemies = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])/4096
                elif name == 'CreepDamage':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalCreepDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalCreepDmg
                elif name == 'SummonDamage':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalSummonDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                        self.heroList[hero].totalOutDmg += self.heroList[hero].totalSummonDmg
                elif name == 'DamageTaken':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalIncDamage = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'GemsTurnedIn':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalGemsTurnedIn = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'RavenTributesCollected':
                    for hero in xrange(0,10):
                        self.heroList[hero].capturedTributes = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'DragonShrinesCaptured':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalShrinesCaptured = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'DamageDoneToImmortal':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalImmortalDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'GardensSeedsCollected':
                    for hero in xrange(0,10):
                        self.heroList[hero].gardensSeedsCollected = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'DamageDoneToShrineMinions':
                    for hero in xrange(0,10):
                        self.heroList[hero].totalShrineMinionDmg = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'TimeInTemple':
                    for hero in xrange(0,10):
                        self.heroList[hero].totaltimeInTemples = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'BlackheartDoubloonsCollected':
                    for hero in xrange(0,10):
                        self.heroList[hero].coinsCollected = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])
                elif name == 'BlackheartDoubloonsTurnedIn':
                    for hero in xrange(0,10):
                        self.heroList[hero].coinsTurnedIn = int(instance['m_values'][self.heroList[hero].id][0]['m_value'])

    def NNet_Replay_Tracker_SStatGameEvent(self, event):
        eventName = event['m_eventName']
        if eventName == 'RegenGlobePickedUp':
            self.process_regen_globes(event)

        elif eventName == 'PlayerDeath':
            self.process_hero_death(event)

        elif eventName == 'EndOfGameTimeSpentDead':
            self.process_hero_dead_time(event)

        elif eventName == 'JungleCampCapture':
            self.process_camp_capture(event)

        elif eventName == 'GatesOpen':
            self.process_gates_open(event)

        elif eventName == 'PeriodicXPBreakdown':
            self.process_periodic_xp_breakdown(event)

        elif eventName == 'SoulEatersSpawned':
            self.process_soul_eater_spawn(event)

        elif eventName == 'EndOfGameXPBreakdown':
            self.process_team_xp_breakdown(event)

        elif eventName == 'LevelUp':
            self.process_level_event(event)

        elif eventName == 'GameStart':
            self.process_game_start(event)

        elif eventName == 'TownStructureDeath':
            self.process_structure_destruction(event)

        elif eventName == 'TalentChosen':
            self.process_talent_chosen(event)

        elif eventName == 'TributeCollected':
            self.process_tribute_collected(event)

        elif eventName == 'Town Captured':
           self.process_town_captured(event)

        elif eventName == 'Punisher Killed':
            self.process_punisher_killed(event)

        elif eventName == 'Altar Captured':
            self.process_altar_captured(event)

        elif eventName == 'GardenTerrorActivated':
            self.process_garden_terror_activated(event)

        elif eventName == 'DragonKnightActivated':
            pass

        elif eventName == 'Boss Duel Started':
            pass

        elif eventName == 'JungleCampInit':
            pass

        elif eventName == 'SkyTempleCaptured':
            pass

        elif eventName == 'Immortal Defeated':
            self.process_immortal_defeated(event)

        elif eventName == 'SkyTempleActivated':
            #pass
            self.process_sky_temple_activated(event)

        elif eventName == 'RavenCurseActivated':
            self.process_raven_curse_activated(event)

        elif eventName == 'Infernal Shrine Captured':
            self.process_infernal_shrine_captured(event)

        elif eventName == 'PlayerSpawned':
            pass

        elif eventName == 'SkyTempleShotsFired':
            #pass
            self.process_temple_shots_fired(event)

        elif eventName == 'TownStructureInit':
            pass

        elif eventName == 'GhostShipCaptured':
            self.process_ghost_ship_captured(event)

    def process_temple_shots_fired(self, event):
        for data in event['m_intData']:
            if data['m_key'] == 'TempleID':
                temple = data['m_value']
            elif data['m_key'] == 'TeamID':
                team = int(data['m_value']) - 1
            elif data['m_key'] == 'Event':
                eventNumber = int(data['m_value'])-1

        for data in event['m_fixedData']:
            if data['m_key'] == 'SkyTempleShotsDamage':
                shotsDamage = round(float(data['m_value'])/4096)

            self.teams[team].luxoriaTempleDmg[eventNumber] += shotsDamage
            self.teams[team].luxoriaTempleShots[eventNumber] += 1


    def process_sky_temple_activated(self, event):
        for data in event['m_intData']:
            if data['m_key'] == 'TempleID':
                temple = data['m_value']
            elif data['m_key'] == 'Event':
                eventNumber = int(data['m_value'])
        #initialize variables

        for team in xrange(0, len(self.teams)):
            if len(self.teams[team].luxoriaTempleDmg) < eventNumber:
                self.teams[team].luxoriaTempleDmg.append(0)
                self.teams[team].luxoriaTempleShots.append(0)


    def process_ghost_ship_captured(self, event):
        eventData = {}
        for data in event['m_intData']:
            if data['m_key'] == 'TeamScore':
                winScore = data['m_value']
            elif data['m_key'] == 'OpponentScore':
                losingScore = data['m_value']
        for data in event['m_fixedData']:
            if data['m_key'] == 'TeamID':
                team = int(data['m_value']/4096) - 1
        eventData['teamScore'] = winScore
        eventData['opponentScore'] = losingScore
        self.teams[team].ghostShipScore.append(eventData)

    def process_infernal_shrine_captured(self, event):
        eventData = {}
        for data in event['m_intData']:
            if data['m_key'] == 'Winning Team':
                team = int(data['m_value']) - 1
            elif data['m_key'] == 'Winning Score':
                winScore = data['m_value']
            elif data['m_key'] == 'Losing Score':
                losingScore = data['m_value']
        eventData['teamScore'] = winScore
        eventData['opponentScore'] = losingScore
        self.teams[team].shrineScore.append(eventData)

    def process_raven_curse_activated(self, event):
        eventData = {}
        team = int(event['m_fixedData'][0]['m_value']/4096) -1
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        for data in event['m_intData']:
            if data['m_key'] == 'TeamScore':
                teamGems = data['m_value']
            elif data['m_key'] == 'OpponentScore':
                opponentCaptures = data['m_value']
            elif data['m_key'] == 'Event':
                eventNumber = data['m_value']
        eventData['teamScore'] = teamGems
        eventData['opponentScore'] = opponentCaptures
        self.teams[team].curseActivatedAt.append(seconds)
        self.teams[team].totalCursesWon += 1
        self.teams[team].curseCaptures.append(eventData)
        self.replayInfo.totalCurses += 1



    def process_immortal_defeated(self, event):
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        for data in event['m_intData']:
            if data['m_key'] == 'Winning Team':
                team = int(data['m_value']) - 1
            elif  data['m_key'] == 'Immortal Fight Duration':
                fightDuration = int(data['m_value'])
        for data in event['m_fixedData']:
            if data['m_key'] == 'Immortal Power Percent':
                immortalPower = round(data['m_value'] / 4096 ,2)

        self.teams[team].totalImmortalsSummoned += 1
        self.teams[team].immortalSummonedAt.append(seconds)
        self.teams[team].immortalFightDuration.append(fightDuration)
        self.teams[team].immortalPower.append(immortalPower)
        #self.teams[team].immortalDuration # calculate separatelly

    def process_garden_terror_activated(self, event):
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        for data in event['m_fixedData']:
            if data['m_key'] == 'TeamID':
                team = int(data['m_value']/4096) - 1
        self.teams[team].plantSumonedAt.append(seconds)


    def process_altar_captured(self, event):
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        for data in event['m_intData']:
            if data['m_key'] == 'Firing Team':
                team = int(data['m_value']) - 1
            elif data['m_key'] == 'Towns Owned':
                towersCaptured = int(data['m_value'])
        self.teams[team].altarsCapturedAt.append(seconds)
        self.teams[team].towersCapturedAtFire.append(towersCaptured)
        self.teams[team].totalAltarsCaptured += 1

    def process_punisher_killed(self, event):
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        for data in event['m_intData']:
            if data['m_key'] == 'Owning Team of Punisher':
                team = int(data['m_value']) - 1
            elif data['m_key'] == 'Duration':
                duration = int(data['m_value'])
            elif data['m_key'] == 'Event':
                number = int(data['m_value'])
        for data in event['m_stringData']:
            if data['m_key'] == 'Punisher Type':
                type = data['m_value'].split('Shrine')[0]
        for data in event['m_fixedData']:
            if data['m_key'] == 'Siege Damage Done':
                siegeDmg = data['m_value']/4096
            elif data['m_key'] == 'Hero Damage Done':
                heroDmg = data['m_value']/4096
        self.teams[team].punisherSummonedAt.append(seconds)
        self.teams[team].punisherTotalAliveTime.append(duration)
        self.teams[team].punisherType.append(type)
        self.teams[team].punisherHeroDmg.append(heroDmg)
        self.teams[team].punisherBuildingDmg.append(siegeDmg)
        self.teams[team].summonedPunishers += 1

    def process_town_captured(self,event):
        for data in event['m_intData']:
            if data['m_key'] == 'New Owner':
                team = int(data['m_value']) - 11
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        self.teams[team].totalTowersCaptured += 1
        self.teams[team].towersCapturedAt.append(seconds)

    def process_tribute_collected(self, event):
        for data in event['m_fixedData']:
            if data['m_key'] == 'TeamID':
                team = int(data['m_value']/4096) - 1
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        self.teams[team].tributesCapturedAt.append(seconds)

    def process_talent_chosen(self, event):
        talentEvent = {}
        for talent in event['m_stringData']:
            if talent['m_key'] == 'PurchaseName':
                talentEvent['talent_name'] = talent['m_value']
        for data in event['m_intData']:
            if data['m_key'] == 'PlayerID':
                playerId = int(data['m_value']) - 1
        seconds = get_seconds_from_int_gameloop(get_gameloops(event))
        talentEvent['seconds'] = seconds
        self.heroList[playerId].pickedTalents.append(talentEvent)

    def process_structure_destruction(self, event):
        for data in event['m_intData']:
            # We are not tracking what structure was destroyed for now, don't know if makes sense.
            if data['m_key'] == 'KillingPlayer':
                playerId = int(data['m_value']) - 1
                self.heroList[playerId].fortsDestroyed += 1
    def process_game_start(self, event):
        for data in event['m_fixedData']:
            if data['m_key'] == 'MapSizeX':
                mapSizeX = data['m_value']/4096
            elif data['m_key'] == 'MapSizeY':
                mapSizeY = data['m_value']/4096
        self.replayInfo.mapSize['x'] = mapSizeX
        self.replayInfo.mapSize['y'] = mapSizeY

    def process_level_event(self, event):
        levelUpEvent = {}
        for data in event['m_intData']:
            if data['m_key'] == 'PlayerID':
                player = int(data['m_value']) - 1
            elif data['m_key'] == 'Level':
                level = int(data['m_value'])
        gl = get_gameloops(event)
        seconds = get_seconds_from_int_gameloop(gl)
        levelUpEvent['level'] = level
        levelUpEvent['seconds'] = seconds
        self.heroList[player].levelEvents.append(levelUpEvent)
        totalEvents = len(self.heroList[player].levelEvents)
        team = self.heroList[player].team
        totalTeamEvents = len(self.teams[team].levelEvents)
        # Insert the event in the team too. Don't add if the event is already there
        if totalEvents > totalTeamEvents:
            self.teams[team].levelEvents.append(levelUpEvent)

        self.teams[team].level = level #set the level

    def process_team_xp_breakdown(self, event):
        player = int(event['m_intData'][0]['m_value']) - 1
        team = 0 if player < 5 else 1
        for data in event['m_fixedData']:
            if data['m_key'] == 'MinionXP':
                minionXP =  data['m_value']/4096
            elif data['m_key'] == 'CreepXP':
                creepXP = data['m_value']/4096
            elif data['m_key'] == 'StructureXP':
                structureXP = data['m_value']/4096
            elif data['m_key'] == 'HeroXP':
                heroXP = data['m_value']/4096
            elif data['m_key'] == 'TrickleXP':
                trickleXP = data['m_value']/4096
        self.teams[team].totalMinionXP = minionXP
        self.teams[team].totalCreepXP = creepXP
        self.teams[team].totalHeroXP = heroXP
        self.teams[team].totalTrickleXP = trickleXP
        self.teams[team].totalStructureXP = structureXP
        self.teams[team].totalXP = minionXP + creepXP + heroXP + trickleXP + structureXP

    def process_soul_eater_spawn(self, event):
        team = event['m_fixedData'][0]['m_value']/4096
        for data in event['m_intData']:
            if data['m_key'] == 'TeamScore':
                teamGems = data['m_value']
            elif data['m_key'] == 'OpponentScore':
                opponentGems = data['m_value']
            elif data['m_key'] == 'Event':
                eventNumber = data['m_value']


    def process_periodic_xp_breakdown(self, event):
        xp_report = {}
        xp_breakdown = []
        for data in event['m_intData']:
            if data['m_key'] == 'Team':
                team = int(data['m_value']) -1
            elif data['m_key'] == 'TeamLevel':
                level = data['m_value']
        xp_report['team'] = team
        xp_report['level'] = level
        for fixedData in event['m_fixedData']:
            if fixedData['m_key'] == 'GameTime':
                reportTime = fixedData['m_value']/4096 # in seconds
                xp_report['seconds'] = reportTime
            elif fixedData['m_key'].endswith('XP'):
                xp_report[fixedData['m_key']] = fixedData['m_value']/4096
        self.teams[team].periodicXPBreakdown.append(xp_report)

    def process_gates_open(self, event):
        self.replayInfo.gatesOpenedAt = get_seconds_from_int_gameloop(get_gameloops(event))

    def process_camp_capture(self, event):
        gl = get_gameloops(event)
        seconds = get_seconds_from_int_gameloop(gl)
        campType = event['m_stringData'][0]['m_value'] if event['m_stringData'][0]['m_key'] == 'CampType' else None
        campId = event['m_intData'][0]['m_value']
        team = (int(event['m_fixedData'][0]['m_value']) / 4096) - 1

        if 'Boss' in campType:
            self.teams[team].bossTaken += 1
        elif 'Bruiser' in campType:
            self.teams[team].mercsTaken += 1
        elif 'Siege' in campType:
            self.teams[team].siegeCampTaken += 1

    def process_hero_dead_time(self, event):
        # Not getting gameloop nor seconds because this is supossed to be only at end of game
        playerId = int(event['m_intData'][0]['m_value']) - 1 #assuming always only 1 player per line
        secondsDead = int(event['m_fixedData'][0]['m_value']) / 4096 # assuming seconds is the only value reported
        self.heroList[playerId].secondsDead = secondsDead

    def process_hero_death(self, event):
        # Get all relevant fields
        gl = get_gameloops(event)
        killers = []
        for actors in event['m_intData']:
            if actors['m_key'] == 'PlayerID':
                victim = int(actors['m_value']) - 1
            elif actors['m_key'] == 'KillingPlayer':
                killers.append(actors['m_value'])
        for position in event['m_fixedData']:
            if position['m_key'] == 'PositionX':
                x = int(position['m_value'])/4096
            elif position['m_key'] == 'PositionY':
                y = int(position['m_value'])/4096
        # create the dict with the info
        kill = {'killers': killers, 'x': x, 'y': y, 'gameloops': gl, 'seconds': get_seconds_from_int_gameloop(gl)}
        # Append the dict to the list of deaths of this hero
        self.heroList[victim].deaths.append(kill)
        self.heroList[victim].deathCount += 1


    def process_regen_globes(self, event):
        if event['m_intData'][0]['m_key'] == 'PlayerID':
            #print event['m_intData'][0]['m_value']
            heroIndex = event['m_intData'][0]['m_value'] - 1
            self.heroList[heroIndex].regenGlobesTaken += 1


    def NNet_Replay_Tracker_SUnitDiedEvent(self, event):
        # Populate Hero Death events
        if event['_event'] != 'NNet.Replay.Tracker.SUnitDiedEvent':
            return None
        self.get_unit_destruction(event)

    def NNet_Replay_Tracker_SUnitOwnerChangeEvent(self, event):
        if event['_event'] != 'NNet.Replay.Tracker.SUnitOwnerChangeEvent':
            return None

        get_unit_owners(event, self.unitsInGame, self.replayInfo.duration_in_secs())

    def NNet_Game_SCmdUpdateTargetUnitEvent(self, event):
        if event['_event'] != 'NNet.Game.SCmdUpdateTargetUnitEvent':
            return None
        self.utue[event['_gameloop']] = event
        self.process_clicked_unit(event)

    def NNet_Game_SCmdEvent(self, event):
        if event['_event'] != 'NNet.Game.SCmdEvent':
            return None

        ability = None

        if event['m_abil']: # If this is an actual user available ability
            if event['m_data'].get('TargetPoint'):
                ability = TargetPointAbility(event)

            elif event['m_data'].get('TargetUnit'):
                ability = TargetUnitAbility(event)

            else: # e['m_data'].get('None'):
                ability = BaseAbility(event)


        if ability:
            # update hero stat
            playerId = find_player_key_from_user_id(self.players, ability.userId)

            self.heroList[playerId].castedAbilities[ability.castedAtGameLoops] = ability

    def NNet_Game_SCmdUpdateTargetPointEvent(self, event):
        self.utpe[event['_gameloop']] = event


    def NNet_Replay_Tracker_SUnitPositionsEvent(self, event):
        if event['_event'] != 'NNet.Replay.Tracker.SUnitPositionsEvent':
            return None

        unitIndex = event['m_firstUnitIndex']
        for i in xrange(0, len(event['m_items']), 3):
            unitIndex += event['m_items'][i + 0]
            x = event['m_items'][i + 1] #* 4
            y = event['m_items'][i + 2] #* 4
            unitTag = self.temp_indexes.get(unitIndex,None)
            if unitTag:
                self.unitsInGame[unitTag].positions[get_seconds_from_int_gameloop(event['_gameloop'])] = [x, y]

    def NNet_Game_SCommandManagerStateEvent(self, event):
        if event['_event'] != 'NNet.Game.SCommandManagerStateEvent':
            return None

        # Get the _gameloops, find the accompanying NNet.Game.SCmdUpdateTargetPointEvent (if any) and get data

        try:
            if event['m_state'] == 1:
                if self.utpe.get(event['_gameloop']):
                    if self.utpe[event['_gameloop']]['_userid']['m_userId'] == event['_userid']['m_userId']:
                        playerId = find_player_key_from_user_id(self.players, event['_userid']['m_userId'])
                        abilities = self.heroList[playerId].castedAbilities
                        if len(abilities) > 0:
                            self.utpe.get(event['_gameloop'])['m_abilityTag'] = \
                                abilities[abilities.keys()[-1]].abilityTag # use last known ability (it's a repetition)
                            ability = TargetPointAbility(self.utpe.get(event['_gameloop']))
                            if ability:
                                self.heroList[playerId].castedAbilities[ability.castedAtGameLoops] = ability

                elif self.utue.get(event['_gameloop']):
                    playerId = find_player_key_from_user_id(self.players, event['_userid']['m_userId'])
                    abilities = self.heroList[playerId].castedAbilities
                    if len(abilities) > 0:
                        self.utue.get(event['_gameloop'])['m_abilityTag'] = abilities[abilities.keys()[-1]].abilityTag
                        ability = TargetUnitAbility(self.utue.get(event['_gameloop']))
                        if ability:
                            self.heroList[playerId].castedAbilities[ability.castedAtGameLoops] = ability
                            seconds = get_seconds_from_int_gameloop(ability.castedAtGameLoops)
                            self.unitsInGame[ability.targetUnitTag].positions[seconds] = [int(ability.x),
                                                                                          int(ability.y)]

                else:
                # This was not a targeted skill
                    playerId = find_player_key_from_user_id(self.players, event['_userid']['m_userId'])
                    abilities = self.heroList[playerId].castedAbilities
                    if len(abilities) > 0:
                        event['m_abilityTag'] = abilities[abilities.keys()[-1]].abilityTag
                        ability = BaseAbility(event)
                        if ability:
                            self.heroList[playerId].castedAbilities[ability.castedAtGameLoops] = ability
        except Exception, e:
            print e
