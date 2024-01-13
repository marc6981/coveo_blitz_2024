from game_message import *
from actions import *
import random
from marc import *
from alexis import *
import logging

# LOGGING_FOLDER = "logs"

# logging.basicConfig(
#     filename="logs/logging.txt",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
# logging.info("Message")
logging.basicConfig(filename='logging.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")
        self.someone_at_shield = False
        self.someone_at_helm = False
        self.correction_angle = 0
        self.epsilon =0.01
        self.attacker_mate = None
        self.powerful_turret = None

    def first_tick(self, game_message: GameMessage):
        # print(f"type: {game_message.type}")
        # print(f"tick: {game_message.tick}")
        # print(f"lastTickErrors: {game_message.lastTickErrors}")
        # print(f"constants: {game_message.constants}")
        # print(f"currentTickNumber: {game_message.currentTickNumber}")
        # print(f"debris: {game_message.debris}")
        # print(f"rockets: {game_message.rockets}")
        # print(f"shipsPositions: {game_message.shipsPositions}")
        # print(f"ships: {game_message.ships}")
        # print(f"currentTeamId: {game_message.currentTeamId}")
        pass

    def calculate_angle_to_rotate(self,game_message: GameMessage,TURRET_TYPE= ["SNIPER", "CANNON", "FAST"]):
        turretss =None
        #Get all station id thar are SNIPER, CANNON, FAST
        for turrets in game_message.ships[game_message.currentTeamId].stations.turrets:
            if turrets.turretType in TURRET_TYPE:
                #Caculate angle between the turret and the enemy ship
                enemy_station_angle = calculate_turret_angle(game_message)
                self.correction_angle = enemy_station_angle - turrets.orientationDegrees
                turretss = turrets
        return turretss

    def get_all_helm_station_id(self, game_message: GameMessage):
        team_ship = get_infinite_loopers_ship(game_message)
        helm_station_id,helm_grid_position = [(station.id, station.gridPosition) for station in team_ship.stations.helms]
        return helm_station_id, helm_grid_position
    
    def find_closest_crewmate_to_helm(self,game_message: GameMessage,actions=[]):
        min_dist = 999
        helm_station = None
        team_ship = get_infinite_loopers_ship(game_message)
        for crewmate in team_ship.crew:

            for station in crewmate.distanceFromStations.helms:
                if not can_go_to_stationId(game_message, crewmate,station.stationId, actions):
                    continue
                if station.distance < min_dist:
                    min_dist = station.distance
                    helm_station = station
                    crewmate_closest_station = crewmate            
        if helm_station:
            return CrewMoveAction(crewmate_closest_station.id, helm_station.stationPosition)

   

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """
        # If first tick
        logging.info(f"Tick: {game_message.tick}")
        if game_message.tick == 1:
            self.first_tick(game_message)


        
        #fIND CLOSEST CREWMATE TO HELM
        #enleve de idle crewmate
        #Faire l,action
        # rotate jusqua temps que l'angle est self.best_angle

        # get priority actions
        #if self.correction_angle <= self.epsilon or self.correction_angle >= -self.epsilon:
      
        actions = []
       

        team_id = game_message.currentTeamId
        my_ship = game_message.ships.get(team_id)
        other_ships_ids = [
            shipId for shipId in game_message.shipsPositions.keys() if shipId != team_id
        ]

        # Find who's not doing anything and try to give them a job?
        idle_crewmates = [
            crewmate
            for crewmate in my_ship.crew
            if crewmate.currentStation is None and crewmate.destination is None
        ]
        self.powerful_turret = self.calculate_angle_to_rotate(game_message)

        print("Voici le correction_angle " +str(self.correction_angle))
        if self.correction_angle !=0:
            
            # qqn au heml ou en direction du helm
            crewmate_at_helm = get_crewmate_at_helm(game_message)
            crewmate_going_to_helm = get_crewmate_going_to_helm(game_message)
            if crewmate_at_helm:
                actions.append(ShipRotateAction(self.correction_angle))
            elif crewmate_going_to_helm is None :
                action = self.find_closest_crewmate_to_helm(game_message)
                if action:
                    actions.append(action)
                    # remove this crewmate from the idle crewmates
                    idle_crewmates = [
                        crewmate
                        for crewmate in idle_crewmates
                        if crewmate.id != action.crewMemberId
                    ]
        else:
            crewmate_at_helm = get_crewmate_at_helm(game_message)
            if crewmate_at_helm:
                idle_crewmates.append(crewmate_at_helm)
            crewmate_going_to_helm = get_crewmate_going_to_helm(game_message)
            if crewmate_going_to_helm:
                idle_crewmates.append(crewmate_going_to_helm)
        # station_id_to_avoid_going = get_station_to_avoid_going(game_message)

        if not self.someone_at_shield:
            action = get_sheild_action(game_message)

            if action:
                actions.append(action)
                self.someone_at_shield = True
                # remove this crewmate from the idle crewmates
                idle_crewmates = [
                    crewmate
                    for crewmate in idle_crewmates
                    if crewmate.id != action.crewMemberId
                ]

        else:
            # check all crewmates to see if at least one is at the shield
            for crewmate in my_ship.crew:
                if crewmate.currentStation and crewmate.currentStation == "SHIELDS":
                    self.someone_at_shield = True
                    break
                # check if a crewmate is going to the shield
                # for all stations shield in the  teamship.stations.shields
                for shield_station in my_ship.stations.shields:
                    if (
                        crewmate.destination
                        and crewmate.destination == shield_station.gridPosition
                    ):
                        self.someone_at_shield = True
                        break
        if can_powerfull_turret_shoot(game_message, self.powerful_turret,actions):
            crewmate_that_can_shoot = who_can_shoot_with_powerfull_turret(game_message, self.powerful_turret,actions)
            if crewmate_that_can_shoot:
                actions.append(CrewMoveAction(crewmate_that_can_shoot.id, self.powerful_turret.position))
                idle_crewmates = [
                    crewmate
                    for crewmate in idle_crewmates
                    if crewmate.id != crewmate_that_can_shoot.id
                ]
        for crewmate in idle_crewmates:
            station_to_go = get_closest_station_to_shoot(
                game_message, crewmate, actions, TURRET_TYPE=["NORMAL", "EMP"]
            )

            if station_to_go:
                print(f"crewmate {crewmate.id} is going to station {station_to_go}")

                # station_id_to_avoid_going.append(station_to_go.stationId)
                # send the crewmate to the station
                actions.append(
                    CrewMoveAction(crewmate.id, station_to_go.stationPosition)
                )

            else:
                
                station_to_go = get_closest_station_to_shoot(
                    game_message,
                    crewmate,
                    actions,
                    TURRET_TYPE=["FAST", "CANNON", "SNIPER"],
                )

                if station_to_go:
                    print(f"crewmate {crewmate.id} is going to station {station_to_go}")

                    # station_id_to_avoid_going.append(station_to_go.stationId)
                    # send the crewmate to the station
                    actions.append(
                        CrewMoveAction(crewmate.id, station_to_go.stationPosition)
                    )

        # for crewmate in idle_crewmates:
        #     visitable_stations = (
        #         crewmate.distanceFromStations.shields
        #         + crewmate.distanceFromStations.turrets
        #         + crewmate.distanceFromStations.helms
        #         + crewmate.distanceFromStations.radars
        #     )
        #     station_to_move_to = random.choice(visitable_stations)
        #     actions.append(
        #         CrewMoveAction(crewmate.id, station_to_move_to.stationPosition)
        #     )

        # Now crew members at stations should do something!
        operatedTurretStations = [
            station
            for station in my_ship.stations.turrets
            if station.operator is not None
        ]
        for turret_station in operatedTurretStations:
            turret_actions = choose_turret_actions(game_message, turret_station.id)
            actions.extend(turret_actions)

        operatedHelmStation = [
            station
            for station in my_ship.stations.helms
            if station.operator is not None
        ]
        # if operatedHelmStation:
        #     actions.append(ShipRotateAction(random.uniform(0, 360)))

        operatedRadarStation = [
            station
            for station in my_ship.stations.radars
            if station.operator is not None
        ]
        # for radar_station in operatedRadarStation:
        #     actions.append(
        #         RadarScanAction(radar_station.id, random.choice(other_ships_ids))
        #     )

        # You can clearly do better than the random actions above! Have fun!
        return actions
