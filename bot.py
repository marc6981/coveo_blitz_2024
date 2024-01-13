from game_message import *
from actions import *
import random
from marc import *
from alexis import *
from simon import *
import logging

# LOGGING_FOLDER = "logs"

# logging.basicConfig(
#     filename="logs/logging.txt",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )
# logging.info("Message")


class Bot:
    def __init__(self):
        print("Initializing your super mega duper bot")

        self.someone_at_shield = False

        #RADAR 
        self.RADAR_FREQIENCE = 200
        self.last_radar_tick = self.RADAR_FREQIENCE / 2
        self.crewRadar = None
        self.radar_queue = []

        



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

    def get_next_move(self, game_message: GameMessage):
        """
        Here is where the magic happens, for now the moves are not very good. I bet you can do better ;)
        """

        # If first tick
        logging.info(f"Tick: {game_message.tick}")
        if game_message.tick == 1:
            self.first_tick(game_message)

        # get priority actions

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









    
        if self.crewRadar == None and self.last_radar_tick >= self.RADAR_FREQIENCE:
            self.crewRadar = idle_crewmates[0]    ##TODO find the right crewmate to go to radar
            self.radar_queue = create_radar_queue(game_message)
        else:
            self.last_radar_tick += 1





        if(self.crewRadar):
           
            if self.crewRadar.currentStation == "RADAR":
                if len(self.radar_queue) == 0:
                    self.last_radar_tick = 0
                    idle_crewmates.append(self.crewRadar)
                    self.crewRadar = None

                else:
                    actions.append(self.radar_queue.pop(0))
                    print("scan complete at tick: " + str(game_message.tick))
                
                
            elif not self.crewRadar.destination:
                actions.append(closest_radar_from_crewmate(game_message, self.crewRadar, actions))

            
            















        # station_id_to_avoid_going = get_station_to_avoid_going(game_message)

        if not self.someone_at_shield:
            action = get_sheild_action(game_message)

            if action:
                actions.append(action)
                self.someone_at_shield = True
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

        for crewmate in idle_crewmates:
            station_to_go = get_closest_station_to_shoot(
                game_message, crewmate, actions
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
        print(f"actions: {actions}")
        return actions
