from game_message import *
from actions import *
import random
import logging
from bot import *
from marc import *


def closest_radar_from_crewmate( game_message: GameMessage, crewmate: CrewMember, actions=[]):
    """
    Returns the closest radar from the crewmate
    """
    min_dist = 999
    min_station = None
    for station in crewmate.distanceFromStations.radars:
        if not can_go_to_stationId(game_message, crewmate, station.stationId, actions):
            continue
        if station.distance < min_dist:
            min_dist = station.distance
            min_station = station
    if min_station:
        #print (f"crewmate {crewmate.name} is going to station {min_station}")
        #print(f"{crewmate}")
        return CrewMoveAction(crewmate.id,min_station.stationPosition)


 
def create_radar_queue(game_message: GameMessage):
    """
    Returns a list of radar actions
    """
    radar_queue = []
    for shipId, shipPosition in game_message.shipsPositions.items():
        if shipId != game_message.currentTeamId:
            radar_queue.append(RadarScanAction(shipId, shipPosition))
    return radar_queue



def find_right_crewmate(game_message: GameMessage, actions=[]):
    """
    Returns the right crewmate to go to the radar
    """
    min_dist = 999
    min_station = None
    min_crewmate = None
    for crewmate in game_message.ships[game_message.currentTeamId].crew:
        for station in crewmate.distanceFromStations.radars:
            if not can_go_to_stationId(game_message, crewmate, station.stationId, actions):
                continue
            if station.distance < min_dist:
                min_dist = station.distance
                min_station = station
                min_crewmate = crewmate
    if min_station:
        return min_crewmate.id


def get_crew_at_radar(game_message: GameMessage):
    """
    Returns True if someone is at the radar
    """
    crewmates = []
    for crewmate in game_message.ships[game_message.currentTeamId].crew:
        for station in crewmate.distanceFromStations.radars:
            if station.distance == 0:
                crewmates.append(crewmate)
    return crewmates


def get_radar_id(game_message: GameMessage):
    """
    Returns the radar id
    """
    idradar = []
    for radars in game_message.ships[game_message.currentTeamId].stations.radars:
       print(f"SALUT: + {radars}")
       idradar.append(radars.id)
    return idradar

def find_crew_by_id(game_message: GameMessage, crewmate_id):
    """
    Returns the crewmate by id
    """
    for crewmate in game_message.ships[game_message.currentTeamId].crew:
        if crewmate.id == crewmate_id:
            return crewmate
    return None
    