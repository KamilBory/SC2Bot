import sc2
from sc2 import BotAI, run_game, maps, Race, Difficulty, position, Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer
import random
import numpy as np
import cv2
import time

HEADLESS = False

class CompetitiveBot(BotAI):
    NAME: str = "CompetitiveBot"
    """This bot's name"""
    RACE: Race = Race.Protoss
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):
        # Initialize inhereted class
        sc2.BotAI.__init__(self)
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50
        self.do_something_after = 0
        self.train_data = []

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts

    def on_end(self, game_result):
        print('--- on_end called ---')
        print(game_result)

        if game_result == Result.Victory:
            np.save("train_data/{}.npy".format(str(int(time.time()))), np.array(self.train_data))

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        self.iteration = iteration
        # Functions strictly for Protoss
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_gateways()
        await self.build_gas()
        await self.build_cyber_core()
        await self.train_stalkers()
        await self.build_robotics_facility()
        await self.build_robotics_bay()
        await self.train_colossus()
        await self.expand()
        await self.intel()
        await self.attack()

        pass

    # Functions for Protoss

    def random_location_variance(self, enemy_start_location):
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-20, 20)) / 100) * enemy_start_location[0]
        y += ((random.randrange(-20, 20)) / 100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.game_info.map_size[0]:
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            y = self.game_info.map_size[1]

        go_to = position.Point2(position.Pointlike((x, y)))
        return go_to

    async def intel(self):
        game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)

        # UNIT: [SIZE, (BGR COLOR)]
        draw_dict = {
            UnitTypeId.PROBE: [1, (55, 200, 0)],
            UnitTypeId.NEXUS: [15, (0, 255, 0)],
            UnitTypeId.PYLON: [3, (20, 235, 0)],
            UnitTypeId.ASSIMILATOR: [2, (55, 200, 0)],
            UnitTypeId.GATEWAY: [3, (200, 100, 0)],
            UnitTypeId.CYBERNETICSCORE: [3, (150, 150, 0)],
            UnitTypeId.STARGATE: [5, (255, 0, 0)],
            UnitTypeId.ROBOTICSFACILITY: [5, (215, 155, 0)],

            UnitTypeId.STALKER: [3, (255, 100, 0)],
            UnitTypeId.COLOSSUS: [3, (255, 120, 0)],
            #UnitTypeId.OBSERVER: [3, (255, 255, 255)]
        }

        for unit_type in draw_dict:
            for unit in self.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), draw_dict[unit_type][0], draw_dict[unit_type][1], -1)

        main_base_names = ["nexus", "supplydepot", "hatchery"]
        for enemy_building in self.enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() not in main_base_names:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)

        for enemy_unit in self.enemy_units:

            if not enemy_unit.is_structure:
                worker_names = ["probe",
                                "scv",
                                "drone"]
                # if that unit is a PROBE, SCV, or DRONE... it's a worker
                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)

        for obs in self.units(UnitTypeId.OBSERVER).ready:
            pos = obs.position
            cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (255, 255, 255), -1)

            line_max = 50
            mineral_ratio = self.minerals / 1500
            if mineral_ratio > 1.0:
                mineral_ratio = 1.0

            vespene_ratio = self.vespene / 1500
            if vespene_ratio > 1.0:
                vespene_ratio = 1.0

            population_ratio = self.supply_left / self.supply_cap
            if population_ratio > 1.0:
                population_ratio = 1.0

            plausible_supply = self.supply_cap / 200.0

            military_weight = len(self.units(VOIDRAY)) / (self.supply_cap - self.supply_left)
            if military_weight > 1.0:
                military_weight = 1.0

            cv2.line(game_data, (0, 19), (int(line_max * military_weight), 19), (250, 250, 200),
                     3)  # worker/supply ratio
            cv2.line(game_data, (0, 15), (int(line_max * plausible_supply), 15), (220, 200, 200),
                     3)  # plausible supply (supply/200.0)
            cv2.line(game_data, (0, 11), (int(line_max * population_ratio), 11), (150, 150, 150),
                     3)  # population ratio (supply_left/supply)
            cv2.line(game_data, (0, 7), (int(line_max * vespene_ratio), 7), (210, 200, 0), 3)  # gas / 1500
            cv2.line(game_data, (0, 3), (int(line_max * mineral_ratio), 3), (0, 255, 25), 3)  # minerals minerals/1500

        # flip horizontally to make our final fix in visual representation:
        self.flipped = cv2.flip(game_data, 0)

        if not HEADLESS:
            resized = cv2.resize(self.flipped, dsize=None, fx=2, fy=2)
            cv2.imshow('Intel', resized)
            cv2.waitKey(1)

    async def build_workers(self):
        nexus = self.townhalls.ready.random
        if(self.can_afford(UnitTypeId.PROBE)
           and nexus.is_idle
           and self.workers.amount < self.townhalls.amount * 22):
            nexus.train(UnitTypeId.PROBE)

    async def build_pylons(self):
        nexus = self.townhalls.ready.random
        pos = nexus.position.towards(self.enemy_start_locations[0], 10)
        if(self.supply_left < 4
           and self.already_pending(UnitTypeId.PYLON) == 0
           and self.can_afford(UnitTypeId.PYLON)):
            await self.build(UnitTypeId.PYLON, near = pos)

    async def build_gateways(self):
        if(self.structures(UnitTypeId.PYLON).ready
           and self.can_afford(UnitTypeId.GATEWAY)
           and self.structures(UnitTypeId.GATEWAY).amount < 4):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.GATEWAY, near = pylon)

    async def build_gas(self):
        if self.structures(UnitTypeId.GATEWAY):
            for nexus in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, nexus)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.ASSIMILATOR, vg)
                        worker.stop(queue = True)

    async def build_cyber_core(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.GATEWAY).ready:
                if not self.structures(UnitTypeId.CYBERNETICSCORE):
                    if (self.can_afford(UnitTypeId.CYBERNETICSCORE)
                        and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0):
                            await self.build(UnitTypeId.CYBERNETICSCORE, near = pylon)

    async def train_stalkers(self):
        for gateway in self.structures(UnitTypeId.GATEWAY).ready:
            if(self.can_afford(UnitTypeId.STALKER)
               and gateway.is_idle):
                gateway.train(UnitTypeId.STALKER)

    async def attack(self):
        if len(self.units(UnitTypeId.STALKER).idle) > 0:
            choice = random.randrange(0, 4)
            target = False
            if self.iteration > self.do_something_after:
                if choice == 0:
                    # no attack
                    wait = random.randrange(20, 165)
                    self.do_something_after = self.iteration + wait

                elif choice == 1:
                    #attack_unit_closest_nexus
                    if len(self.enemy_units) > 0:
                        target = random.choice(self.enemy_units)

                elif choice == 2:
                    #attack enemy structures
                    if len(self.enemy_structures) > 0:
                        target = random.choice(self.enemy_structures)

                elif choice == 3:
                    #attack_enemy_start
                    target = self.enemy_start_locations[0]

                if target:
                    for vr in self.units(UnitTypeId.STALKER).idle:
                        self.do(vr.attack(target))
                y = np.zeros(4)
                y[choice] = 1
                print(y)
                self.train_data.append([y,self.flipped])

    async def build_robotics_facility(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.CYBERNETICSCORE):
                if not self.structures(UnitTypeId.ROBOTICSFACILITY):
                    if (self.can_afford(UnitTypeId.ROBOTICSFACILITY)
                            and self.already_pending(UnitTypeId.ROBOTICSFACILITY) == 0):
                        await self.build(UnitTypeId.ROBOTICSFACILITY, near = pylon)

    async def build_robotics_bay(self):
        if self.structures(UnitTypeId.PYLON).ready:
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            if self.structures(UnitTypeId.ROBOTICSFACILITY):
                if not self.structures(UnitTypeId.ROBOTICSBAY):
                    if (self.can_afford(UnitTypeId.ROBOTICSBAY)
                            and self.already_pending(UnitTypeId.ROBOTICSBAY) == 0):
                        await self.build(UnitTypeId.ROBOTICSBAY, near = pylon)

    async def train_colossus(self):
        for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
            if self.structures(UnitTypeId.ROBOTICSBAY):
                if(self.can_afford(UnitTypeId.COLOSSUS)
                   and robotic_facility.is_idle):
                    robotic_facility.train(UnitTypeId.COLOSSUS)

    async def expand(self):
        if self.structures(UnitTypeId.NEXUS).amount < 3 and self.can_afford(UnitTypeId.NEXUS):
            await self.expand_now()
