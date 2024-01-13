from game_message import *
from actions import *
import random


def calculate_distance(pos1: Vector, pos2: Vector) -> float:
    return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5


def choose_turret_actions(game_message: GameMessage, turretId: str):
    actions = []
    our_ship_position = game_message.shipsPositions[game_message.currentTeamId]
    closest_enemy_ship = None
    closest_distance = None

    # Get the position of the closest enemy from our ship amongst all enemy ships
    for shipId, shipPosition in game_message.shipsPositions.items():
        if shipId != game_message.currentTeamId:
            distance = calculate_distance(our_ship_position, shipPosition)
            if closest_enemy_ship is None or distance < closest_distance:
                closest_enemy_ship = shipId
                closest_distance = distance

    # Find the turret with the given turretId
    turret_station = next(
        (
            turret
            for turret in game_message.ships[
                game_message.currentTeamId
            ].stations.turrets
            if turret.id == turretId
        ),
        None,
    )

    if turret_station is not None:
        # Define max_charge for the turret
        max_charge = game_message.constants.ship.stations.turretInfos[
            turret_station.turretType
        ].maxCharge

        # If turret's charge is exactly 0, aim at the closest enemy ship's position
        if turret_station.charge == 0:
            closest_enemy_ship_position = game_message.shipsPositions.get(
                closest_enemy_ship
            )
            if closest_enemy_ship_position:
                actions.append(
                    TurretLookAtAction(turretId, closest_enemy_ship_position)
                )

        # If turret is at max charge, shoot
        if turret_station.charge == max_charge:
            actions.append(TurretShootAction(turretId))

        # If turret's charge is 0 or above and not at max charge, charge the turret
        elif turret_station.charge >= 0 and turret_station.charge < max_charge:
            actions.append(TurretChargeAction(turretId))

    else:
        print(f"No turret station found with turretId: {turretId}")

    print("Actions: ", actions)
    return actions
