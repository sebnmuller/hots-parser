__author__ = 'Rodrigo Duenas, Cristian Orellana'



from replay import *

def processEvents(protocol=None, replayFile=None):
    """"
    This is the main loop, reads a replayFile and applies available decoders (trackerEvents, gameEvents, msgEvents, etc)
    Receives the protocol and the replayFile as an mpyq file object
    """
    if not protocol or not replayFile:
        print "Error - Protocol and replayFile are needed"
        return -1

    replay_data = Replay(protocol, replayFile)
    #replayUuid = uuid.uuid1()
    replay_data.process_replay_details()
    replay_data.process_replay_header()
    replay_data.process_replay_initdata()
    replay_data.process_replay()
    replay_data.process_replay_attributes()
    replay_data.calculate_army_strength()
    replay_data.process_map_events()
    replay_data.process_generic_events()


    return replay_data

def processTimestampedEvents(protocol, replayFile):
    replay_data = Replay(protocol, replayFile)
    replay_data.process_replay_events()

    return replay_data
