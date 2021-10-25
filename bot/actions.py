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
import math


async def intel(self, HEADLESS):
    game_data = np.zeros((self.game_info.map_size[1], self.game_info.map_size[0], 3), np.uint8)

    for unit in self.units().ready:
        pos = unit.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(unit.radius * 8), (255, 0, 0),
                   math.ceil(int(unit.radius * 0.5)))

    for structure in self.structures().ready:
        pos = structure.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(structure.radius * 8), (255, 0, 0),
                   math.ceil(int(structure.radius * 0.5)))

    for enemy_building in self.enemy_structures:
        pos = enemy_building.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(enemy_building.radius * 8), (0, 0, 255),
                   math.ceil(int(enemy_building.radius * 0.5)))

    for unit in self.enemy_units:
        pos = unit.position
        cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(unit.radius * 8), (0, 0, 255),
                   math.ceil(int(unit.radius * 0.5)))

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

        military_weight = len(self.units(UnitTypeId.VOIDRAY)) / (self.supply_cap - self.supply_left)
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

async def defend_nexus(self):
    nexus = self.townhalls.ready.random
    if len(self.enemy_units) > 0:
        target = self.enemy_units.closest_to(nexus)
        for u in self.units().idle:
            u.attack(target)


async def attack_known_enemy_structure(self):
    if len(self.enemy_structures) > 0:
        target = random.choice(self.enemy_structures)
        for u in self.units().idle:
            u.attack(target)


async def attack_known_enemy_unit(self):
    if len(self.enemy_units) > 0:
        target = self.enemy_units.closest_to(random.choice(self.units(UnitTypeId.NEXUS)))
        for u in self.units().idle:
            u.attack(target)

async def do_something(self):
    #print('Hejka')
    if self.use_model:
        prediction = self.model.predict([self.flipped.reshape([-1, 176, 200, 3])])
        choice = np.argmax(prediction[0])
    else:
        choice = random.randint(0,2)

    try:
        await self.choices[choice]
    except Exception as e:
        print(str(e))

    #self.train_data.append([y, self.flipped])

async def scout(self):
    self.expand_dis_dir = {}

    for el in self.expansion_locations:
        distance_to_enemy_start = el.distance_to(self.enemy_start_locations[0])
        self.expand_dis_dir[distance_to_enemy_start] = el

    self.ordered_exp_distances = sorted(k for k in self.expand_dis_dir)

    if len(self.units(UnitTypeId.OBSERVER)) == 0:
        if len(self.scouts_and_spots) == 0:
            scout = self.units(UnitTypeId.PROBE).random
            self.scouts_and_spots.append(scout)
    else:
        if len(self.scouts_and_spots) <= 4:
            scout = self.units(UnitTypeId.OBSERVER).idle.random
            self.scouts_and_spots.append(scout)

    to_be_removed = []
    existing_ids = [unit.tag for unit in self.units]
    
    for s in self.scouts_and_spots:
        if s.tag not in existing_ids:
            to_be_removed.append(s)
          
    for s in to_be_removed:
        self.scouts_and_spots.remove(s)

    for i in range(0, len(self.scouts_and_spots)):
        print(i)
        location = self.expand_dis_dir[i]
        self.scouts_and_spots[i].move(location)
