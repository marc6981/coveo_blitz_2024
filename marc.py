from actions import *
from game_message import *


ROTABLE_TURRET = ["NORMAL", "EMP"]
ROTABLE_NOT_TURRET = []
TURRET = []


def get_station_id_by_vector(game_message: GameMessage, vector: Vector):
    """
    return the station id by the vector
    """
    for station in game_message.ships[game_message.currentTeamId].stations.turrets:
        if station.gridPosition == vector:
            return station.id

    for station in game_message.ships[game_message.currentTeamId].stations.shields:
        if station.gridPosition == vector:
            return station.id

    for station in game_message.ships[game_message.currentTeamId].stations.radars:
        if station.gridPosition == vector:
            return station.id
    for station in game_message.ships[game_message.currentTeamId].stations.helms:
        if station.gridPosition == vector:
            return station.id


def get_station_to_avoid_going(game_message: GameMessage):
    """
    return the list of station to avoid going
    """

    # check all the destination of the crew

    station_to_avoid_going = []

    for crew in game_message.ships[game_message.currentTeamId].crew:
        if crew.destination:
            vector_pos = crew.destination
            station_to_avoid_going.append(
                get_station_id_by_vector(game_message, vector_pos)
            )

    return station_to_avoid_going


def can_go_to_stationId(
    game_message: GameMessage, crew: CrewMember, stationId: str, current_actions=[]
):
    """
    return True if the crew can go to the stationId
    """
    # check if the someone else is going to the station in the current actions
    for action in current_actions:
        if isinstance(action, CrewMoveAction):
            if get_station_id_by_vector(game_message, action.destination) == stationId:
                return False

    # check for all crew if they are going to the station
    for crew_member in game_message.ships[game_message.currentTeamId].crew:
        if crew_member.id == crew.id:
            continue

        if crew_member.destination:
            if (
                get_station_id_by_vector(game_message, crew_member.destination)
                == stationId
            ):
                return False

    # check if someone is already at the station
    for station in game_message.ships[game_message.currentTeamId].stations.turrets:
        if station.id == stationId:
            if station.operator:
                return False

    return True


def get_closest_station_to_shoot(
    game_message: GameMessage, crew: CrewMember, current_actions=[]
) -> Station:
    """
    For the moment only return the station turret that can rotate
    """
    all_turrets_stations = get_all_turrets_by_name(game_message, ROTABLE_TURRET)
    all_turrets_station_ids = [station.id for station in all_turrets_stations]

    turrets = []
    for station in crew.distanceFromStations.turrets:
        # skip the station if it is in the list of station to avoid
        # if station.stationId in station_to_avoid:
        #     continue

        if not can_go_to_stationId(
            game_message, crew, station.stationId, current_actions
        ):
            continue

        if station.stationId in all_turrets_station_ids:
            turrets.append(station)

    min_dist = 999
    min_station = None
    for turret in turrets:
        if turret.distance < min_dist:
            min_dist = turret.distance
            min_station = turret

    return min_station


# def get_most_priority_action_for_crew(game_message: GameMessage, crew_id):
#     """
#     find the best action for a crew member
#     """

#     crew_pos = get_crew_position(game_message, crew_id)

#     # first we need to find if we need to sheild or not
#     # we need to shield if we have less than 50% of our shield

#     # if need_to_shield(game_message):
#     #     actions.append(get_sheild_action(game_message))

#     # we need to shoot if we have a target
#     turrets = get_all_rotating_turrets(game_message, ROTABLE_TURRET)
#     all_pos_of_turret = [turret.position for turret in turrets]

#     #

#     pos_crew_need_to_go = find_the_closest_pos_between_a_point_and_a_list_of_point(
#         crew_pos, all_pos_of_turret
#     )

#     # check if we are at the right position
#     if pos_crew_need_to_go != crew_pos:
#         return CrewMoveAction(crew_id, pos_crew_need_to_go)


def get_crew_position(game_message, crew_id):
    """
    return the position of the crew member
    """
    crew = game_message.ships[game_message.currentTeamId].crew
    crew_member = crew[crew_id]
    return crew_member.position


def find_the_closest_pos_between_a_point_and_a_list_of_point(pos, list_of_pos):
    """
    return the closest pos between a point and a list of point
    """
    return min(list_of_pos, key=lambda p: p.distance(pos))


def need_to_shield(game_message, threshold=50):
    """
    return True if we need to shield depending on the threshold in percent
    """

    ship_shield = game_message.ships[game_message.currentTeamId].shield
    ship_max_shield = game_message.constants.ship.maxShield

    return ship_shield / ship_max_shield < threshold / 100


def find_closest_crewmate_to_list_of_station(crewmate, list_of_station):
    """
    for crewmate find the closest station in the list of station
    """
    crewmate_pos = crewmate.position

    closest_station = None
    min_dist = 999
    for station in list_of_station:
        dist = station.position.distance(crewmate_pos)
        if dist < min_dist:
            min_dist = dist
            closest_station = station

    return closest_station


def get_sheild_action(game_message, actions=[]):
    """
    for all crew find the closest shield station
    """
    min_dist = 999
    min_station = None
    crewmate_closest_station = None
    for crewmate in game_message.ships[game_message.currentTeamId].crew:
        for station in crewmate.distanceFromStations.shields:
            if not can_go_to_stationId(
                game_message, crewmate, station.stationId, actions
            ):
                continue

            if station.distance < min_dist:
                min_dist = station.distance
                min_station = station
                crewmate_closest_station = crewmate

    if min_station:
        return CrewMoveAction(crewmate_closest_station.id, min_station.stationPosition)

    # return ShieldAction(game_message.currentTeamId)


def get_all_turrets_by_name(game_message: GameMessage, rotating_turrets_list):
    # Find all turrets that are not rotating
    ship = get_infinite_loopers_ship(game_message)
    rotating_turrets_list = ["NORMAL", "EMP"]
    turretss = [
        turrets
        for turrets in ship.stations.turrets
        if turrets.turretType in rotating_turrets_list
    ]
    # logging.info("Non rotating turrets: " + str(non_rotating_turrets))
    return turretss


def get_infinite_loopers_ship(game_message: GameMessage):
    # Find your ship
    team_id = game_message.currentTeamId
    team_ship = game_message.ships.get(team_id)
    return team_ship
