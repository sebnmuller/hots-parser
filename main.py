__author__ = 'Rodrigo Duenas, Cristian Orellana'

import argparse
from heroprotocol import protocol39951 as protocol
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

        print "=== MAP: %s ===" % replayData.replayInfo.internalMapName
        print "Duration: %s secs (%s gl)" % (replayData.replayInfo.duration_in_secs(), replayData.replayInfo.gameLoops)
        for hero in replayData.heroList:
            print "[%s] Hero: %s (%s) " % ("Human" if replayData.heroList[hero].isHuman else "AI", replayData.heroList[hero].name, replayData.heroList[hero].playerId)
            mapName = replayData.replayInfo.internalMapName
            if mapName.strip() == 'Cursed Hollow':
                print "\tcaptured tributes: %s" % replayData.heroList[hero].capturedTributes
                print "\tclicked tributes: %s" %  replayData.heroList[hero].clickedTributes
            elif mapName.strip() == 'Tomb of the Spider Queen':
                print "\tcaptured soul gems: %s" % replayData.heroList[hero].totalSoulsTaken
            elif mapName.strip() == "Garden of Terror":
                print "\tcaptured Plant Horrors: %s" % replayData.heroList[hero].totalPlantsControlled
            print "\tRegen Globes taken: %s" % replayData.heroList[hero].regenGlobesTaken


        if mapName.strip() == 'Tomb of the Spider Queen':
            print "Team 0 took %s gems and missed %s - Summoned %s spiders in %s waves" % (replayData.team0.pickedSoulGems, replayData.team0.wastedSoulGems, replayData.team0.summonedSpiderBosses, replayData.team0.summonedSpiderBosses/3)
            print "\t Spiders were alive a total of %s seconds, %s buildings and %s units were killed during this time" % (replayData.team0.spiderBossesTotalAliveTime, replayData.team0.totalBuildingsKilledDuringSpiders, replayData.team0.totalUnitsKilledDuringSpiders)
            print "\t\tNorth: %s buildings, %s units - South: %s, %s - Center: %s, %s" % (replayData.team0.totalBuildingsKilledDuringNorthSpider, replayData.team0.totalUnitsKilledDuringNorthSpider, replayData.team0.totalBuildingsKilledDuringSouthSpider, replayData.team0.totalUnitsKilledDuringSouthSpider, replayData.team0.totalBuildingsKilledDuringCenterSpider, replayData.team0.totalUnitsKilledDuringCenterSpider)
            max_lifespan = max(replayData.team0.spiderBossesCenterTotalAliveTime, replayData.team0.spiderBossesNorthTotalAliveTime, replayData.team0.spiderBossesSouthTotalAliveTime)
            position = "center" if replayData.team0.spiderBossesCenterTotalAliveTime == max_lifespan else "north" if replayData.team0.spiderBossesNorthTotalAliveTime == max_lifespan else "south"
            print "\t The spider that lived the longest was located at the %s" % (position)
            print "Team 1 took %s gems and missed %s - Summoned %s spiders in %s waves" % (replayData.team1.pickedSoulGems, replayData.team1.wastedSoulGems, replayData.team1.summonedSpiderBosses, replayData.team1.summonedSpiderBosses/3)
            print "\t Spiders were alive a total of %s seconds, %s buildings and %s units were killed during this time" % (replayData.team1.spiderBossesTotalAliveTime, replayData.team1.totalBuildingsKilledDuringSpiders, replayData.team1.totalUnitsKilledDuringSpiders)
            print "\t\tNorth: %s buildings, %s units - South: %s, %s - Center: %s, %s" % (replayData.team1.totalBuildingsKilledDuringNorthSpider, replayData.team1.totalUnitsKilledDuringNorthSpider, replayData.team1.totalBuildingsKilledDuringSouthSpider, replayData.team1.totalUnitsKilledDuringSouthSpider, replayData.team1.totalBuildingsKilledDuringCenterSpider, replayData.team1.totalUnitsKilledDuringCenterSpider)
            max_lifespan = max(replayData.team0.spiderBossesCenterTotalAliveTime, replayData.team0.spiderBossesNorthTotalAliveTime, replayData.team0.spiderBossesSouthTotalAliveTime)
            position = "center" if replayData.team0.spiderBossesCenterTotalAliveTime == max_lifespan else "north" if replayData.team0.spiderBossesNorthTotalAliveTime == max_lifespan else "south"
            print "\t The spider that lived the longest was located at the %s" % (position)

        print "Team 0 missed %s regen globes" % (replayData.team0.missedRegenGlobes)
        print "Team 1 missed %s regen globes" % (replayData.team1.missedRegenGlobes)

        if mapName.strip() == 'Sky Temple':
            if (replayData.team0.luxoriaTemplesCapturedSeconds+float(replayData.team1.luxoriaTemplesCapturedSeconds)) > 0:
                t0percent = 100 * round(replayData.team0.luxoriaTemplesCapturedSeconds/(replayData.team0.luxoriaTemplesCapturedSeconds+float(replayData.team1.luxoriaTemplesCapturedSeconds)),2)
            else:
                t0percent = 0
            if (replayData.team1.luxoriaTemplesCapturedSeconds+float(replayData.team1.luxoriaTemplesCapturedSeconds)) > 0:
                t1percent = 100 * round(replayData.team1.luxoriaTemplesCapturedSeconds/(replayData.team0.luxoriaTemplesCapturedSeconds+float(replayData.team1.luxoriaTemplesCapturedSeconds)),2)
            else:
                t1percent = 0

            if (replayData.team0.luxoriaTempleNorthCapturedSeconds+float(replayData.team1.luxoriaTempleNorthCapturedSeconds)) > 0:
                t0NorthPercent = 100 * round(replayData.team0.luxoriaTempleNorthCapturedSeconds/(replayData.team0.luxoriaTempleNorthCapturedSeconds+float(replayData.team1.luxoriaTempleNorthCapturedSeconds)),2)
            else:
                t0NorthPercent = 0

            if (replayData.team0.luxoriaTempleCenterCapturedSeconds+float(replayData.team1.luxoriaTempleCenterCapturedSeconds)) > 0:
                t0SouthPercent = 100 * round(replayData.team0.luxoriaTempleCenterCapturedSeconds/(replayData.team0.luxoriaTempleCenterCapturedSeconds+float(replayData.team1.luxoriaTempleCenterCapturedSeconds)),2)
            else:
                t0SouthPercent = 0

            if (replayData.team0.luxoriaTempleSouthCapturedSeconds+float(replayData.team1.luxoriaTempleSouthCapturedSeconds)) > 0:
                t0CenterPercent = 100 * round(replayData.team0.luxoriaTempleSouthCapturedSeconds/(replayData.team0.luxoriaTempleSouthCapturedSeconds+float(replayData.team1.luxoriaTempleSouthCapturedSeconds)),2)
            else:
                t0CenterPercent = 0

            if (replayData.team1.luxoriaTempleNorthCapturedSeconds+float(replayData.team1.luxoriaTempleNorthCapturedSeconds)) > 0:
                t1NorthPercent = 100 * round(replayData.team1.luxoriaTempleNorthCapturedSeconds/(replayData.team0.luxoriaTempleNorthCapturedSeconds+float(replayData.team1.luxoriaTempleNorthCapturedSeconds)),2)
            else:
                t1NorthPercent = 0

            if (replayData.team1.luxoriaTempleCenterCapturedSeconds+float(replayData.team1.luxoriaTempleCenterCapturedSeconds)) > 0:
                t1SouthPercent = 100 * round(replayData.team1.luxoriaTempleCenterCapturedSeconds/(replayData.team0.luxoriaTempleCenterCapturedSeconds+float(replayData.team1.luxoriaTempleCenterCapturedSeconds)),2)
            else:
                t1SouthPercent = 0

            if (replayData.team1.luxoriaTempleSouthCapturedSeconds+float(replayData.team1.luxoriaTempleSouthCapturedSeconds)) > 0:
                t1CenterPercent = 100 * round(replayData.team1.luxoriaTempleSouthCapturedSeconds/(replayData.team0.luxoriaTempleSouthCapturedSeconds+float(replayData.team1.luxoriaTempleSouthCapturedSeconds)),2)
            else:
                t1CenterPercent = 0

            print "Team 0 controlled temples %s percent of the time (%s seconds)" % (t0percent, replayData.team0.luxoriaTemplesCapturedSeconds)
            print "\t North Tower: %s percent (%s seconds)" % (t0NorthPercent, replayData.team0.luxoriaTempleNorthCapturedSeconds)
            print "\t Center Tower: %s percent (%s seconds)" % (t0CenterPercent, replayData.team0.luxoriaTempleSouthCapturedSeconds)
            print "\t South Tower: %s percent (%s seconds)" % (t0SouthPercent, replayData.team0.luxoriaTempleCenterCapturedSeconds)
            print "Team 1 controlled temples %s percent of the time (%s seconds)" % (t1percent, replayData.team1.luxoriaTemplesCapturedSeconds)
            print "\t North Tower: %s percent (%s seconds)" % (t1NorthPercent, replayData.team1.luxoriaTempleNorthCapturedSeconds)
            print "\t Center Tower: %s percent (%s seconds)" % (t1CenterPercent, replayData.team1.luxoriaTempleSouthCapturedSeconds)
            print "\t South Tower: %s percent (%s seconds)" % (t1SouthPercent, replayData.team1.luxoriaTempleCenterCapturedSeconds)

        if mapName.strip() == 'Garden of Terror':
            t0 = replayData.team0
            t1 = replayData.team1

            print "Team 0 spawned %s plants that were alive a total of %s seconds" % (len(t0.totalPlantsSummoned), sum(t0.totalPlantsDuration.values()))
            if t0.totalPlantsSummoned > 0:
                for plant in xrange(1, len(replayData.team0.totalPlantsSummoned) + 1):
                    print "\t Plant %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (plant, t0.totalPlantsSummoned[plant], t0.totalPlantsDuration[plant],  t0.plantEffectiveness[plant], t0.totalUnitsKilledDuringPlant[plant], t0.totalBuildingsKilledDuringPlant[plant])
            if t1.totalPlantsSummoned > 0:
                print "Team 1 spawned %s plants that were alive a total of %s seconds" % (len(t1.totalPlantsSummoned), sum(t1.totalPlantsDuration.values()))
                for plant in xrange(1, len(replayData.team1.totalPlantsSummoned) + 1):
                    print "\t Plant %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (plant, t1.totalPlantsSummoned[plant], t1.totalPlantsDuration[plant], t1.plantEffectiveness[plant], t1.totalUnitsKilledDuringPlant[plant], t1.totalBuildingsKilledDuringPlant[plant])

        if mapName.strip() == 'Dragon Shire':
            t0 = replayData.team0
            t1 = replayData.team1


            print "Team 0 spawned %s dragons that were alive a total of %s seconds" % (len(t0.totaldragonsSummoned), sum(t0.totaldragonsDuration.values()))
            print "Team 1 spawned %s dragons that were alive a total of %s seconds" % (len(t1.totaldragonsSummoned), sum(t1.totaldragonsDuration.values()))


            if len(t0.totaldragonsSummoned) > 0:
                for dragon in xrange(1, len(t0.totaldragonsSummoned) + 1):
                    print "\t Dragon %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (dragon, t0.totaldragonsSummoned[dragon], t0.totaldragonsDuration[dragon],  t0.dragonEffectiveness[dragon], t0.totalUnitsKilledDuringdragon[dragon], t0.totalBuildingsKilledDuringdragon[dragon])

            if len(t1.totaldragonsSummoned) > 0:
                for dragon in xrange(1, len(t1.totaldragonsSummoned) + 1):
                    print "\t Dragon %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (dragon, t1.totaldragonsSummoned[dragon], t1.totaldragonsDuration[dragon], t1.dragonEffectiveness[dragon], t1.totalUnitsKilledDuringdragon[dragon], t1.totalBuildingsKilledDuringdragon[dragon])

            for dragon in t0.wastedDragonTime:
                print "\t In dragon %s, Team 0 had the control for %s seconds before it changed ownership, Team 1 had it for %s seconds " % (dragon, t0.wastedDragonTime[dragon], t1.wastedDragonTime[dragon])


        if mapName.strip() == 'Infernal Shrines':
            t0 = replayData.team0
            t1 = replayData.team1

            print "Team 0 spawned %s punishers that were alive a total of %s seconds" % (t0.summonedPunishers, sum(t0.punisherTotalAliveTime.values()))
            if t0.summonedPunishers > 0:
                for punisher in xrange(1, t0.summonedPunishers + 1):
                    print "\t Punisher %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (t0.punisherType[punisher], t0.punishedSummonedAt[punisher], t0.punisherTotalAliveTime[punisher],  t0.punisherEfectiveness[punisher], t0.totalUnitsKilledDuringPunisher[punisher], t0.totalBuildingsKilledDuringPunisher[punisher])

            if t1.summonedPunishers > 0:
                print "Team 1 spawned %s punishers that were alive a total of %s seconds" % (t1.summonedPunishers, sum(t1.punisherTotalAliveTime.values()))
                for punisher in xrange(1, t1.summonedPunishers + 1):
                    print "\t Punisher %s, summoned at %s, alive for %s had an effectiveness of %s (%s units killed and %s buildings destroyed) " % (t1.punisherType[punisher], t1.punishedSummonedAt[punisher], t1.punisherTotalAliveTime[punisher],  t1.punisherEfectiveness[punisher], t1.totalUnitsKilledDuringPunisher[punisher], t1.totalBuildingsKilledDuringPunisher[punisher])


        if mapName.strip() == 'Blackheart\'s Bay':
            t0 = replayData.team0
            t1 = replayData.team1
            print "T1 %s" % len(t1.totalShipsControlled)

            print "Team 0 controlled %s ships for a total of %s seconds" % (len(t0.totalShipsControlled), sum(t0.totalShipsControlled.values()))
            if len(t0.totalShipsControlled) > 0:
                for ship in t0.totalShipsControlled.keys():
                    print "\t During ship %s a total of %s unit died and %s buildings where destroyed, the effectiveness index is %s" % (ship, t0.totalUnitsKilledDuringShip[ship], t0.totalBuildingsDestroyedDuringShip[ship], t0.shipEffectiveness[ship])

            print "Team 1 controlled %s ships for a total of %s seconds" % (len(t1.totalShipsControlled), sum(t1.totalShipsControlled.values()))
            if len(t1.totalShipsControlled) > 0:
                for ship in t1.totalShipsControlled.keys():
                    print "\t During ship %s a total of %s unit died and %s buildings where destroyed, the effectiveness index is %s" % (ship, t1.totalUnitsKilledDuringShip[ship], t1.totalBuildingsDestroyedDuringShip[ship], t1.shipEffectiveness[ship])

def dump_data(entities=None, replay_data=None, file_path=None):
    if not entities or not path or not replay_data:
        return None

    file_path = path.join(file_path, '%s_' % (datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")))


    if entities == 'all':
        dump_heroes(data=replay_data, output_path=file_path)
        dump_teams(data=replay_data, output_path=file_path)
        dump_units(data=replay_data, output_path=file_path)

    if entities == 'heroes':
        dump_heroes(data=replay_data, output_path=file_path)

    if entities == 'teams':
        dump_teams(data=replay_data, output_path=file_path)

    if entities == 'units':
        dump_units(data=replay_data, output_path=file_path)


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

            dump = "[" + jsonpickle.encode(data.team0)
            f.write(dump)

            dump = "," + jsonpickle.encode(data.team1) + "]"
            f.write(dump)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-dir', help='Path to the output directory')
    parser.add_argument('-r', '--dump-heroes',  action='store_true', default=False, help='Indicates you want to dump hero data')
    parser.add_argument('-t', '--dump-teams', action='store_true', default=False, help='Indicates you want to dump teams data')
    parser.add_argument('-u', '--dump-units',action='store_true', default=False, help='Indicates you want to dump units data')
    parser.add_argument('-a', '--dump-all', action='store_true', default=False, help='Shortcut for --dump-heroes --dump-teams --dump-units')
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
    elif args.dump_heroes or args.dump_teams or args.dump_units:
        if (args.dump_heroes):
            dump_data(entities='heroes', file_path=output_path, replay_data=replayData)
        if (args.dump_teams):
            dump_data(entities='teams', file_path=output_path, replay_data=replayData)
        if (args.dump_units):
            dump_data(entities='units', file_path=output_path, replay_data=replayData)
    else:
        save_to_db(replayData, args.replay_path)
