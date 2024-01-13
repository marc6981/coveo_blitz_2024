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

    # Get the position of closest enemy from our ship amongst all enemy ships
    for shipId, shipPosition in game_message.shipsPositions.items():
        if shipId != game_message.currentTeamId:
            distance = calculate_distance(our_ship_position, shipPosition)
            if closest_enemy_ship is None or distance < closest_distance:
                closest_enemy_ship = shipId
                closest_distance = distance

    # Find the turret with the given turretId
    turret_station = next((turret for turret in game_message.ships[game_message.currentTeamId].stations.turrets if turret.id == turretId), None)

    if turret_station is not None:
        # Check if the turret is already aimed at the closest enemy ship
        current_target = getattr(turret_station, 'currentTarget', None)
        if current_target != closest_enemy_ship:
            # Aim the turret at the closest enemy ship
            actions.append(TurretLookAtAction(turretId, closest_enemy_ship))

        # Check if the turret is at max charge
        max_charge = game_message.constants.ship.stations.turretInfos[turret_station.turretType].maxCharge
        if turret_station.charge == max_charge:
            # If turret is at max charge, append a TurretShootAction
            actions.append(TurretShootAction(turretId))
        else:
            # If the turret is not at max charge, charge it
            actions.append(TurretChargeAction(turretId))
    else:
        print(f"No turret station found with turretId: {turretId}")

    print("Actions: ", actions)
    return actions