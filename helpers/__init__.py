__author__ = 'Rodrigo Duenas, Cristian Orellana'

import datetime
from math import sqrt, sin, asin, degrees, hypot, radians
from collections import OrderedDict



def win_timestamp_to_date(ts=None, date_format='%Y-%m-%d %H:%M:%S'):
    if ts:
        return datetime.datetime.fromtimestamp(int((ts/10000000) - 11644473600)).strftime(date_format)
    else:
        return None

def get_seconds_from_event_gameloop(e):
    return int((e['_gameloop'] % 2**32)/16)

def get_seconds_from_int_gameloop(gameloop):
    return int((gameloop % 2**32)/16)

def get_gameloops(e):
    return (e['_gameloop'] % 2**32)

def get_unit_tag(e):
    return (e['m_unitTagIndex'] << 18) + e['m_unitTagRecycle']

def get_ability_tag(e):
    if e.get('m_abilityTag'):
        return e['m_abilityTag']
    else:
        return e['m_abil']['m_abilLink'] << 5 | e['m_abil']['m_abilCmdIndex']

def calculate_distance(x1, y1, x2, y2):
    return sqrt(pow(x1-x2,2)+pow(y1-y2,2))

def get_unit_owners(e, unitsInGame, totalDuration):
    """
    Get the owner of the unit and the time the unit was owned
    """

    # This is for units where the ownership is not permanent, like Sky Temple towers, Ghost Ship and Dragon Statue
    # one common trait among these units is that ownership will alternate between teams (teams 11 and 12) and map (team 0)

    if e['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent':
        unitTag = get_unit_tag(e)
        unit = unitsInGame[unitTag]
        if unit.is_sky_temple_tower() or unit.is_dragon_statue() or unit.is_ghostship():
            if e['m_upkeepPlayerId'] in (11, 12, 0):
                owner = e['m_upkeepPlayerId'] - 11
            elif e['m_upkeepPlayerId'] in xrange(1,6): # If the player is in the slots 1 to 5, then team 0
                owner = 0
            elif e['m_upkeepPlayerId'] in xrange(6,11): # If the player is in the slots 6 to 10, then team 1
                owner = 1
            ownerTuple = (owner, get_seconds_from_event_gameloop(e), None) # owner, when, duration (None = forever)
            totalOwners = len(unit.ownerList)
            if len(unit.ownerList) > 0: # update duration (in secs) for previous capture
                unit.ownerList[totalOwners - 1][2] = int(ownerTuple[1] - unit.ownerList[totalOwners-1][1])
            unit.ownerList.append(list(ownerTuple))


    # This is for pickable units
        if e['_event'] == 'NNet.Replay.Tracker.SUnitOwnerChangeEvent' and e['m_upkeepPlayerId'] in xrange(0,11):
            unitTag = get_unit_tag(e)


    # This is for vehicles (Dragon, Plant)

            if unit.is_plant_vehicle() :
                owner = e['m_upkeepPlayerId'] - 1
                unit.bornAt = get_seconds_from_event_gameloop(e)
                unit.bornAtGameLoops = e['_gameloop']
                unit.positions[e['_gameloop']] = [unit.bornAtX, unitsInGame[unitTag].bornAtY]
                #ownerTuple = (owner, unit.bornAt, get_seconds_from_event_gameloop(e)-unit.bornAt)
                ownerTuple = (owner, unit.bornAt, 0)
                unit.ownerList.append(list(ownerTuple))


            elif not unit.is_sky_temple_tower() and not unit.is_plant_vehicle() \
                    and not unit.is_ghostship() and not unit.is_dragon_statue():
                owner = e['m_upkeepPlayerId'] - 1
                ownerTuple = (owner, get_seconds_from_event_gameloop(e), 0)
                unit.ownerList.append(list(ownerTuple))



def get_position_by_second(unit, total_time):
    pos = OrderedDict()
    iter = 0
    dist_iter = 1
    # try:

    for gl in xrange(unit.bornAtGameLoops, unit.get_death_time(total_time)*16 + 1):
        if gl in unit.positions.keys():

            if get_seconds_from_int_gameloop(gl) not in pos.keys():
                # If the info for this second is not stored yet
                pos[get_seconds_from_int_gameloop(gl)] = unit.positions[gl]
                iter += 1
                dist_iter = 1

        # if we don't have information for the current second, we need to estimate it
        else:
            total_positions = len(unit.positions)
            if get_seconds_from_int_gameloop(gl) not in pos.keys() and iter < total_positions:
                x_1 = unit.positions[unit.positions.keys()[iter-1]][0]
                y_1 = unit.positions[unit.positions.keys()[iter-1]][1]
                # print unit.unit_tag_index()
                # print unit.unit_tag_recycle()
                # print unit.positions.keys()
                # print "iter %s" % iter
                x_2 = unit.positions[unit.positions.keys()[iter]][0]
                y_2 = unit.positions[unit.positions.keys()[iter]][1]
                elapsed_seconds = get_seconds_from_int_gameloop(unit.positions.keys()[iter] - unit.positions.keys()[iter-1])
                distance = hypot(x_2-x_1, y_2-y_1)
                if distance > 0:
                    alpha = degrees(asin(abs(y_2 - y_1)/distance))
                else:
                    alpha = 0
                beta = 180 - 90 - alpha
                distance_per_second = distance / elapsed_seconds
                travel_distance = distance_per_second * dist_iter
                distance_x = round(travel_distance * sin(radians(beta)))
                distance_y = round(travel_distance * sin(radians(alpha)))
                if y_1 < y_2:
                    multi_y = 1
                else:
                    multi_y = -1
                if x_1 < x_2:
                    multi_x = 1
                else:
                    multi_x = -1
                new_x = x_1 + distance_x * multi_x
                new_y = y_1 + distance_y * multi_y

                pos[get_seconds_from_int_gameloop(gl)] = [new_x, new_y]
                dist_iter += 1
    # except Exception, e:
    #     print "error here!!! %s" % e
    return pos





def get_unit_clicked(e, unitsInGame):
    """
    Gets information when a unit has been clicked by another one. i.e: When clicking tribute or returning souls
    """

    if e['_event'] == 'NNet.Game.SCmdUpdateTargetUnitEvent':
        unitTag = e['m_target']['m_tag']
        if unitTag in unitsInGame.keys():
            if unitsInGame[unitTag].is_tribute():
                playerId = e['_userid']['m_userId']
                clickTuple = (playerId, get_seconds_from_event_gameloop(e))
                unitsInGame[unitTag].clickerList.append(clickTuple)


def get_hero_deaths_from_game_event(e, heroList):
    """
    This function works by reading the specific Game Event information
    Parse the event and looks if a there is a NNet.Game.SCameraUpdateEvent with no m_target (None)
    this only happens when the camera is pointing to the spawn area. It uses the m_userId instead of
    the unitIndex.
    """

    if e['_event'] == 'NNet.Game.SCameraUpdateEvent' and not e['m_target'] and e['_gameloop'] > 10:
        # find the hero
        playerId =  find_hero_key_from_user_id(heroList, (e['_userid']['m_userId']))
        unitTag = [key for (key, value) in sorted(heroList.items()) if value.playerId == playerId][0]
        eventTime = get_seconds_from_event_gameloop(e)

        if len(heroList[unitTag].deathList.keys()) > 0:
            if eventTime - int(heroList[unitTag].deathList.keys()[0]) > 12: # we need this to rule out the first event which is actually tracked
                heroDeathEvent = {'killerPlayerId': None , 'killerUnitIndex': None} # sadly, we don't know who killed it
                heroList[unitTag].deathList[eventTime] = heroDeathEvent # and this is actually the respawn time, not death time
                heroList[unitTag].deathCount += 1




def find_hero_key_from_tag(heroList=None, tag=None):
    if len(heroList) == 0 or not heroList:
        return None
    else:
        for k, v in heroList.iteritems():
            if v.unitTag == tag:
                return k
    return None

def find_hero_key_from_user_id(heroList=None, userId=None):
    if len(heroList) == 0 or not heroList:
        return None
    else:
        for k, v in heroList.iteritems():
            if v.userId == userId:
                return k
    return None

def find_player_key_from_user_id(playerList=None, userId=None):
    if len(playerList) == 0 or not playerList:
        return None
    else:
        for k, v in playerList.iteritems():
            if v.userId == userId:
                return k
    return None



def get_hero_death_from_tracker_events(e, heroList):
    """
    This function works by reading the specific Replay Tracker Event information
    Parse the event and looks if a hero unit was destroyed, if so, adds a new entry to the deathList
    """
    deadUnitTag = get_unit_tag(e)
    playerId = find_hero_key_from_tag(heroList, deadUnitTag)

    if e['_event'] == 'NNet.Replay.Tracker.SUnitDiedEvent' and playerId is not None:
        seconds = get_seconds_from_event_gameloop(e)

        if e['m_killerUnitTagIndex']:
            killerUnitTag = get_unit_tag(e)
            heroDeathEvent = {'killerPlayerId': e['m_killerPlayerId'], 'killerUnitIndex': killerUnitTag}
            heroList[playerId].deathList[seconds] = heroDeathEvent
            heroList[playerId].deathCount += 1
        else:
            # There is a bug that cause m_killerUnitTagIndex and m_killerUnitTagRecycle to be null
            heroDeathEvent = {'killerPlayerId': e['m_killerPlayerId'], 'killerUnitIndex': None}
            heroList[playerId].deathList[seconds] = heroDeathEvent
            heroList[playerId].deathCount += 1

