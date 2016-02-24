__author__ = 'Rodrigo Duenas, Cristian Orellana'

import argparse
from heroprotocol import protocol40431 as protocol
from heroprotocol.mpyq import mpyq
from os import path
from parser import processEvents
import json
import datetime
import jsonpickle



def save_to_db(replayData, path):
    """
    The original intent of this function is to store all the metrics to a database
    but at this moment it's just printing basic stats directly from the variables
    just to give an idea of what is being calculated
    """
    if replayData:

        print "=== MAP: %s (%s by %s) ===" % (replayData.replayInfo.mapName, replayData.replayInfo.mapSize['x'],  replayData.replayInfo.mapSize['y'])
        mapName = replayData.replayInfo.mapName
        print "Duration: %s secs (%s gl)" % (replayData.replayInfo.duration_in_secs(), replayData.replayInfo.gameLoops)
        print "TEAMS INFORMATION ____________________________________"
        for team in replayData.teams:
            print "Team %s reached level %s (%s)" % (team.id, team.level, 'Winner' if team.isWinner else 'Loser')
            for metric, value in team.__dict__.iteritems():
                print "%s: %s" % (metric, value)
            print sorted(team.army_strength)
            print [value for (key, value) in sorted(team.army_strength.items())]
        print "\n\nHEROES INFORMATION ___________________________________"
        for hero in replayData.heroList:
            print "[%s] Hero: %s (%s) played by %s " % ("Human" if replayData.heroList[hero].isHuman else "AI", replayData.heroList[hero].name, replayData.heroList[hero].playerId, replayData.players[replayData.heroList[hero].playerId].name)

            for metric, value in replayData.heroList[hero].__dict__.iteritems():
                if metric not in ('castedAbilities'):
                    if type(value) is list:
                        print "\t%s:" % metric
                        for v in value:
                            print "\t\t%s" % v
                    else:
                        print "\t%s: %s" % (metric, value)

        # Todo standardize team name treatment
        if mapName.strip() == 'Cursed Hollow':
            for team in xrange(0,len(replayData.teams)):
                print "Team %s took %s tributes at %s and won %s curse event(s)" % \
                      (replayData.teams[team].id,
                       len(replayData.teams[team].tributesCapturedAt),
                       replayData.teams[team].tributesCapturedAt,
                       replayData.teams[team].totalCursesWon)
                for event in xrange(0, replayData.teams[team].totalCursesWon):
                    print "\tIn curse %s (activated at %s) team captured %s tributes, opponent team captured %s" %  \
                        (event + 1,
                         replayData.teams[team].curseActivatedAt[event],
                         replayData.teams[team].curseCaptures[event]['teamScore'],
                         replayData.teams[team].curseCaptures[event]['opponentScore'],
                         )

        if mapName.strip() == 'Tomb of the Spider Queen':
            for team in xrange(0,len(replayData.teams)):
                print "Team %s took %s gems and missed %s - Summoned %s spiders in %s waves" % (team, replayData.teams[team].pickedSoulGems, replayData.teams[team].wastedSoulGems, replayData.teams[team].summonedSpiderBosses, replayData.teams[team].summonedSpiderBosses/3)
                print "\tSpiders were alive a total of %s seconds, %s buildings and %s units were killed during this time" % (replayData.teams[team].spiderBossesTotalAliveTime, replayData.teams[team].totalBuildingsKilledDuringSpiders, replayData.teams[team].totalUnitsKilledDuringSpiders)
                print "\tNorth: %s buildings, %s units - South: %s, %s - Center: %s, %s" % (replayData.teams[team].totalBuildingsKilledDuringNorthSpider, replayData.teams[team].totalUnitsKilledDuringNorthSpider, replayData.teams[team].totalBuildingsKilledDuringSouthSpider, replayData.teams[team].totalUnitsKilledDuringSouthSpider, replayData.teams[team].totalBuildingsKilledDuringCenterSpider, replayData.teams[team].totalUnitsKilledDuringCenterSpider)
                max_lifespan = max(replayData.teams[team].spiderBossesCenterTotalAliveTime, replayData.teams[team].spiderBossesNorthTotalAliveTime, replayData.teams[team].spiderBossesSouthTotalAliveTime)
                position = "center" if replayData.teams[team].spiderBossesCenterTotalAliveTime == max_lifespan else "north" if replayData.teams[team].spiderBossesNorthTotalAliveTime == max_lifespan else "south"
                print "\tThe spider that lived the longest was located at the %s" % (position)
                print "\tMissed %s regen globes" % (replayData.teams[team].missedRegenGlobes)


        if mapName.strip() == 'Sky Temple':
            for team in xrange(0,len(replayData.teams)):
                if (replayData.teams[team].luxoriaTemplesCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTemplesCapturedSeconds)) > 0:
                    percent = 100 * round(replayData.teams[team].luxoriaTemplesCapturedSeconds/(replayData.teams[team].luxoriaTemplesCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTemplesCapturedSeconds)),2)
                else:
                    percent = 0

                if (replayData.teams[team].luxoriaTempleNorthCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleNorthCapturedSeconds)) > 0:
                    northPercent = 100 * round(replayData.teams[team].luxoriaTempleNorthCapturedSeconds/(replayData.teams[team].luxoriaTempleNorthCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleNorthCapturedSeconds)),2)
                else:
                    northPercent = 0

                if (replayData.teams[team].luxoriaTempleCenterCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleCenterCapturedSeconds)) > 0:
                    southPercent = 100 * round(replayData.teams[team].luxoriaTempleCenterCapturedSeconds/(replayData.teams[team].luxoriaTempleCenterCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleCenterCapturedSeconds)),2)
                else:
                    southPercent = 0

                if (replayData.teams[team].luxoriaTempleSouthCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleSouthCapturedSeconds)) > 0:
                    centerPercent = 100 * round(replayData.teams[team].luxoriaTempleSouthCapturedSeconds/(replayData.teams[team].luxoriaTempleSouthCapturedSeconds+float(replayData.teams[abs(team-1)].luxoriaTempleSouthCapturedSeconds)),2)
                else:
                    centerPercent = 0

                print "Team %s controlled temples %s percent of the time (%s seconds)" % (team, percent, replayData.teams[team].luxoriaTemplesCapturedSeconds)
                print "\t North Tower: %s percent (%s seconds)" % (northPercent, replayData.teams[team].luxoriaTempleNorthCapturedSeconds)
                print "\t South Tower: %s percent (%s seconds)" % (southPercent, replayData.teams[team].luxoriaTempleCenterCapturedSeconds)
                print "\t Center Tower: %s percent (%s seconds)" % (centerPercent, replayData.teams[team].luxoriaTempleSouthCapturedSeconds)

        if mapName.strip() == 'Battlefield of Eternity':
            for team in xrange(0, len(replayData.teams)):
                print "Team %s spawned %s immortals" % (replayData.teams[team].id, replayData.teams[team].totalImmortalsSummoned)
                for immortal in xrange(0, replayData.teams[team].totalImmortalsSummoned):
                    print "\tImmortal %s summoned at %s after a %s seconds fight with %s percent power" % \
                          (immortal + 1,
                           replayData.teams[team].immortalSummonedAt[immortal],
                           replayData.teams[team].immortalFightDuration[immortal],
                           replayData.teams[team].immortalPower[immortal],
                           )


        if mapName.strip() == 'Garden of Terror':
            for team in xrange(0,len(replayData.teams)):
                print "Team %s spawned %s plants that were alive a total of %s seconds" % (team, replayData.teams[team].totalPlantsSummoned, replayData.teams[team].totalPlantsDuration)
                if replayData.teams[team].totalPlantsSummoned > 0:
                    for plant in xrange(0, replayData.teams[team].totalPlantsSummoned):
                        print "\t Plant %s, summoned at %s, alive for %s had an effectiveness of %s " \
                              "(%s units killed and %s buildings destroyed) " % \
                              (plant+1,
                               replayData.teams[team].plantSumonedAt[plant],
                               replayData.teams[team].plantDuration[plant],
                               replayData.teams[team].plantEffectiveness[plant],
                               replayData.teams[team].totalUnitsKilledDuringPlant[plant],
                               replayData.teams[team].totalBuildingsKilledDuringPlant[plant])

        if mapName.strip() == 'Dragon Shire':

            for team in xrange(0, len(replayData.teams)):
                print "Team %s spawned %s dragons that were alive a total of %s seconds" % \
                      (team, replayData.teams[team].totalDragonsSummoned, replayData.teams[team].totalDragonsDuration)
                if replayData.teams[team].totalDragonsSummoned > 0:
                    for dragon in xrange(0, replayData.teams[team].totalDragonsSummoned):
                        print "\tDragon summoned at %s, alive for %s seconds had an effectiveness of %s (%s units killed and %s buildings destroyed) " % \
                              (replayData.teams[team].dragonCaptureTimes[dragon],
                               replayData.teams[team].dragonDuration[dragon],
                               replayData.teams[team].dragonEffectiveness[dragon],
                               replayData.teams[team].totalUnitsKilledDuringdragon[dragon],
                               replayData.teams[team].totalBuildingsKilledDuringdragon[dragon])
                        print "\tIn this dragon, Team %s had the control for %s seconds before it changed ownership, Team %s had it for %s seconds " % (
                                                            team,
                                                            replayData.teams[team].wastedDragonTime[dragon],
                                                            abs(team-1),
                                                            replayData.teams[abs(team-1)].wastedDragonTime[dragon])

        if mapName.strip() == 'Infernal Shrines':
            for team in xrange(0, len(replayData.teams)):
                print "Team %s spawned %s punishers that were alive a total of %s seconds" % \
                      (team,
                       replayData.teams[team].summonedPunishers,
                       sum(replayData.teams[team].punisherTotalAliveTime))

                for punisher in xrange(0, replayData.teams[team].summonedPunishers):
                    print "\tPunisher %s, summoned at %s (%s v/s %s), alive for %s inflicted %s hero damage and %s structure damage had an effectiveness of %s " \
                          "(%s units killed and %s buildings destroyed) " % \
                          (replayData.teams[team].punisherType[punisher],
                           replayData.teams[team].punisherSummonedAt[punisher],
                           replayData.teams[team].shrineScore[punisher]['teamScore'],
                           replayData.teams[team].shrineScore[punisher]['opponentScore'],
                           replayData.teams[team].punisherTotalAliveTime[punisher],
                           replayData.teams[team].punisherHeroDmg[punisher],
                           replayData.teams[team].punisherBuildingDmg[punisher],
                           replayData.teams[team].punisherEfectiveness[punisher],
                           replayData.teams[team].totalUnitsKilledDuringPunisher[punisher],
                           replayData.teams[team].totalBuildingsKilledDuringPunisher[punisher])

        if mapName.strip() == 'Blackheart\'s Bay':
            for team in xrange(0, len(replayData.teams)):
                print "Team %s controlled %s ships for a total of %s seconds" % \
                      (team,
                       replayData.teams[team].totalShipsControlled,
                       sum(replayData.teams[team].shipDurations))
                for ship in xrange(0, len(replayData.teams[team].shipDurations)):
                    print "\t During ship %s (%s v/s %s) a total of %s units died and %s buildings where destroyed, " \
                          "the effectiveness was %s" % \
                          (ship+1,
                           replayData.teams[team].ghostShipScore[ship]['teamScore'],
                           replayData.teams[team].ghostShipScore[ship]['opponentScore'],
                           replayData.teams[team].totalUnitsKilledDuringShip[ship],
                           replayData.teams[team].totalBuildingsDestroyedDuringShip[ship],
                           replayData.teams[team].shipEffectiveness[ship])

        if mapName.strip() == 'Towers of Doom':
            for team in xrange(0, len(replayData.teams)):
                print "Team %s captured %s towers at %s " % \
                      (replayData.teams[team].id,
                       replayData.teams[team].totalTowersCaptured,
                       replayData.teams[team].towersCapturedAt)
                print "Team %s captured %s altars" % (replayData.teams[team].id, replayData.teams[team].totalAltarsCaptured)
                for altar in xrange(0, replayData.teams[team].totalAltarsCaptured):
                    print "\t%s captured at %s inflicted %s points of damage to the core" % \
                    (altar + 1,
                     replayData.teams[team].altarsCapturedAt[altar],
                     replayData.teams[team].towersCapturedAtFire[altar])

def dump_data(entities=None, replay_data=None, file_path=None):
    if not entities or not path or not replay_data:
        return None

    file_path = path.join(file_path, '%s_' % (datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")))


    if entities == 'all':
        dump_heroes(data=replay_data, output_path=file_path)
        dump_teams(data=replay_data, output_path=file_path)
        dump_units(data=replay_data, output_path=file_path)
        dump_players(data=replay_data, output_path=file_path)

    if entities == 'heroes':
        dump_heroes(data=replay_data, output_path=file_path)

    if entities == 'teams':
        dump_teams(data=replay_data, output_path=file_path)

    if entities == 'units':
        dump_units(data=replay_data, output_path=file_path)

    if entities == 'players':
        dump_players(data=replay_data, output_path=file_path)


def dump_heroes(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "heroes.json"
    print "dumping heroes data into %s" % (file_path)
    with file(file_path, 'w') as f:
            dump = jsonpickle.encode(data.heroList)
            f.write(dump)

def dump_units(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "units.json"
    print "dumping units data into %s" % (file_path)
    with file(file_path, 'w') as f:
            dump = jsonpickle.encode(data.unitsInGame)
            f.write(dump)

def dump_teams(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "teams.json"
    print "dumping teams data into %s" % (file_path)
    with file(file_path, 'w') as f:

            dump = "[" + jsonpickle.encode(data.teams[0])
            f.write(dump)

            dump = "," + jsonpickle.encode(data.teams[1]) + "]"
            f.write(dump)

def dump_players(data=None, output_path=None):
    if not data or not output_path:
        return None
    file_path = output_path + "players.json"
    print "dumping player data into %s" % (file_path)
    with file(file_path, 'w') as f:
            dump = jsonpickle.encode(data.players)
            f.write(dump)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-dir', help='Path to the output directory')
    parser.add_argument('-r', '--dump-heroes',  action='store_true', default=False, help='Indicates you want to dump hero data')
    parser.add_argument('-t', '--dump-teams', action='store_true', default=False, help='Indicates you want to dump teams data')
    parser.add_argument('-u', '--dump-units',action='store_true', default=False, help='Indicates you want to dump units data')
    parser.add_argument('-p', '--dump-players',action='store_true', default=False, help='Indicates you want to dump player data')
    parser.add_argument('-a', '--dump-all', action='store_true', default=False, help='Shortcut for --dump-heroes --dump-teams --dump-units --dump-players')
    parser.add_argument('replay_path', help='Path to the .StormReplay file to process')
    args = parser.parse_args()

    print "Processing: %s" % (args.replay_path)

    replayData = None
    replay = mpyq.MPQArchive(args.replay_path)
    replayData = processEvents(protocol, replay)

    if (args.output_dir):
        if not path.exists(args.output_dir): # check if the provided path exists
            print 'Error - Path %s does not exist' % (args.output_dir)
            exit(0)
        output_path = args.output_dir

    else:
        # If the parameter is not provided then assume the output is the same folder this script resides
        output_path = path.dirname(path.abspath(__file__))

    if (args.dump_all):
        dump_data(entities='all', file_path=output_path, replay_data=replayData)
    elif args.dump_heroes or args.dump_teams or args.dump_units or args.dump_players:
        if (args.dump_heroes):
            dump_data(entities='heroes', file_path=output_path, replay_data=replayData)
        if (args.dump_teams):
            dump_data(entities='teams', file_path=output_path, replay_data=replayData)
        if (args.dump_units):
            dump_data(entities='units', file_path=output_path, replay_data=replayData)
        if (args.dump_players):
            dump_data(entities='players', file_path=output_path, replay_data=replayData)
    else:
        print 'saving to db'
        save_to_db(replayData, args.replay_path)
