## Metrics currently tracked

### Heroes

#### Basic stats

    How many times the hero died (buggy atm, there is a bug in the protocol decoder which make this hard to track)
    How many neutral NPCS the hero killed (i.e. when taking mercenary camps)
    How many mercenary camps were captured by the hero
    How many buildings the hero destroyed or help to destroy (was in the vicinity of the destroyed building)
    How many units in total the hero killed
    How many enemy heroes were slain by the hero
    How many tributes the hero captured (Specific for Cursed Hollow map)
    How many tributes the hero clicked, but not necessarily captured.
    How many soul gems the hero picked up (Specific for Tomb of the Spider Queen map)
    How many watch towers were captured by the hero
    How many regen globes were picked up by the hero
    What abilities were casted by the hero (this is a list of pairs (second, ability casted)
    How many plants were controlled by the hero (Specific for Garden of Terror map)
    How many units were killed by the hero while he was controlling the plant.
    How many buildings where destroyed by the hero while he was controlling the plant.
    How many units were polymorphed by the hero while he was controlling the plant.
    How many pots the hero placed when he was controlling the plant.
    How many plant pots this hero killed when he was defending against a plant.
    How many dragons where controlled by the hero (Specific for Dragon Shire map)
    How many units were killed while the player was controlling the dragon.
    How many buildings were destroyed while the players was controlling the dragon.
    How many coins were picked up (Specific for Blackheart's Bay)
    How many skulls were picked up (Specific for Haunted Mines)

#### Specific stats:

    For Cho'Gall: % of rune bombs detonated by Gall. (WIP)

#### Skills

    We have each skill casted by each hero, the landing coordinates (in case is a non-targeted skill) and the target (in case is targeted) - this is mostly raw data.

### Teams

#### Basic Stats

    Team level
    Is this team the winner?
    Is this team the loser?
    How many regen globes did the team not pick up
    How many regen globes the team picked up
    How many watch tower were taken by the team
    How many seconds the watchtower was under the team control (per watch tower)
    What percentage of the time was the watchtower under the team's control? (per watch tower)
    How many bosses were taken by this team, this is the mercenary boss(es) (has seconds into the game associated)
    How many mercenary camps did this team take? (Has seconds into the game associated)

#### Stats for Tomb of the Spider Map

    How many soul gems where not picked up by the team?
    How many soul gems where picked up by members of the team?
    How many spiders where summoned by the team?
    How many seconds was alive the spider that summoned on top lane? (this is per summon event)
    How many seconds was alive the spider that summoned on center lane? (this is per summon event)
    How many seconds was alive the spider that summoned on bottom lane? (this is per summon event)
    How many seconds were alive all spiders in total (this is per summon event)
    How many buildings were killed while the spiders were active (this includes all buildings destructions not only those directly destroyed by the spider)
    How many buildings were killed while the top spider was active (this includes all buildings destructions not only those directly destroyed by the spider)
    How many buildings were killed while the center spider was active (this includes all buildings destructions not only those directly destroyed by the spider)
    How many buildings were killed while the bottom spider was active (this includes all buildings destructions not only those directly destroyed by the spider)
    How many units were killed while the spiders were active (this includes all unit kills not only those directly killed by the spider)
    How many units were killed while the top spider was active (this includes all buildings destructions not only those directly destroyed by the spider)
    How many units were killed while the top spider was active (this includes all buildings destructions not only those directly destroyed by the spider)
    What was the effectiveness of each spider? effectiveness = how many units/buildings were killed/destroyed while the spider was active considering the unit/building weight (how important it is) divided by a distance factor. That way a unit that died far away from the spider contributes less to the effectiveness than one that died closer.

#### Stats for Garden of Terror Map

    How many plants did the team summon?
    How many seconds was the plant alive? (Per plant event)
    How many units were killed directly by the plant (per plant event)
    How many buildings were killed directly by the plant? (per plant event)
    How many units were killed while the plant was active, that's it not necessarily killed directly by the plant. (per plant event)
    How many buildings were destroyed while the plant was active, again not necessarily killed directly by the plant. (per plant event)
    How many plant pots did this plant place? (per plant event)
    How many plant pots the members of the team killed.
    How effective was the plant (per plant event)

#### Stats for Sky Temple

    How many temples did the team capture? (global)
    For how long was the temple under the team's control? (global)
    How many seconds was the north temple under the control of the team? (per event)
    How many times did this team capture the north temple? (per event)
    How many seconds was the center temple under the control of the team? (per event)
    How many times did this team capture the center temple? (per event)
    How many seconds was the south temple under the control of the team? (per event)
    How many times did this team capture the south temple? (per event)
    What percentage of the time were the temples under this team control? (total seconds under team control / total time controlled overall, per event)
    What percentage of the time was the north temple under this team control? (per event)
    What percentage of the time was the center temple under this team control? (per event)
    What percentage of the time was the south temple under this team control? (per event)
    How many buildings were destroyed while the temple was under the control of the team (per temple, per event)
    How many units were destroyed while the temple was under the control of the team (per temple, per event)
    What was the effectiveness of the temple (per temple, per event)

#### Stats for Dragon Shrine

    How many dragons the team in total summoned
    How many seconds was the dragon active (per dragon)
    How many units were killed directly by the dragon (per dragon)
    How many buildings were destroyed by the dragon (per dragon)
    How effective was the dragon (per dragon)
    How many buildings were destroyed while the dragon was active (per dragon)
    How many units where killed while the dragon was active (per dragon)
    How many seconds the statue was available to be picked up by a member of the team but no one did it (per dragon)

#### Stats for Haunted Mines

    How many golems were summoned
    Distance traveled by the golem (per golem)
    How effective was the golem (per golem)
    How many units were killed directly by the golem (per golem)
    How many buildings were destroyed by the golem (per golem)
    How many units were killed while the golem was active (per golem)
    How many buildings were destroyed while the golem was active (per golem)
    How many seconds was the golem active (per golem)

#### Stats for Blackheart's Bay

    How many ships the team controlled
    How many units were killed while the ship was active (per ship)
    How many buildings were destroyed while the ship was active (per ship)
    How effective was the ship (units killed * unit's strength modifier, per ship)

#### Stats for Infernal Shrines

    How many punishers were summoned by the team (per punisher)
    How many seconds was the punisher active (per punisher)
    How many units were killed while the punisher was active (per punisher)
    How many buildings were destroyed while the punisher was active (per punisher)
    Punisher effectiveness (per punisher)

### All units (NPC, minions, buildings)

#### Common unit attributes/stats
 Each unit present in the replay is registered by the parser and the following attributes are stored

    isDead // just a flag to determine if the unit died during the game or not (valid only for non heroes)
    diedAt // Seconds into the game when it was destroyed (-1 means never died)
    diedAtX // X Coordinate where the unit died
    diedAtY // Y coordinate where the unit died
    diedAtGameLoops // Gameloops into the game when the unit died/was destroyed
    gameLoopsAlive = -1 // -1 means never died.
    killerTeam // Team that the killer unit belongs to
    killerTag // Tag of the killer unit
    killerTagIndex // Tag indes of the killer unit
    killerTagRecycle = // Tag recycle of the killer unit
    killerPlayerId // Player id of the killer unit
    ownerList = list() # owner, when, duration (None = forever) // For units that can be controlled (i.e. dragon)
    clickerList = OrderedDict() # key = gameloop , value = player id // For clickable units (i.e. tributes / dragon statue)
    unitsKilled // Units killed by this unit
    buildingsKilled // Buildings destroyed by this unit
    unitTagIndex // Tag index of the unit
    unitTagRecycle // Tag Recycle of the unit
    unitTag // Tag of the unit
    bornAt // Seconds into the game when it was created
    bornAtGameLoops // Gameloops into the game when the unit was created
    internalName # Internal unit name
    team // Team this unit belongs to, or Hero controlling it at born time (if it's <= 10)
    bornAtX // X Coordinate where the unit died
    bornAtY // Y Coordinate where the unit died
    positions // List of each (x,y) pair per second, for the unit
    distanceFromKiller // distance the unit was from its killer, usefull to determine killer's effectivity
