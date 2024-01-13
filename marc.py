from actions import *
from game_message import *


ROTABLE_TURRET = ["NORMAL", "EMP"]
ROTABLE_NOT_TURRET = []
TURRET = []


def get_most_priority_action_for_crew(game_message: GameMessage, crew_id):
    """
    find the best action for a crew member
    """

    crew_pos = get_crew_position(game_message, crew_id)

    # first we need to find if we need to sheild or not
    # we need to shield if we have less than 50% of our shield

    # if need_to_shield(game_message):
    #     actions.append(get_sheild_action(game_message))

    # we need to shoot if we have a target
    turrets = get_all_rotating_turrets(game_message, ROTABLE_TURRET)
    all_pos_of_turret = [turret.position for turret in turrets]

    pos_crew_need_to_go = find_the_closest_pos_between_a_point_and_a_list_of_point(
        crew_pos, all_pos_of_turret
    )

    # check if we are at the right position
    if pos_crew_need_to_go != crew_pos:
        return CrewMoveAction(crew_id, pos_crew_need_to_go)


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


def get_sheild_action(game_message):
    """
    need to find all the shield station and find the
    """

    # return ShieldAction(game_message.currentTeamId)


def get_all_rotating_turrets(game_message: GameMessage, rotating_turrets_list):
    # Find all turrets that are not rotating
    ship = get_infinite_loopers_ship(game_message)
    rotating_turrets_list = ["NORMAL", "EMP"]
    non_rotating_turrets = [
        turrets
        for turrets in ship.stations.turrets
        if not turrets.turretType in rotating_turrets_list
    ]
    # logging.info("Non rotating turrets: " + str(non_rotating_turrets))
    return non_rotating_turrets


def get_infinite_loopers_ship(game_message: GameMessage):
    # Find your ship
    team_id = game_message.currentTeamId
    team_ship = game_message.ships.get(team_id)
    return team_ship
