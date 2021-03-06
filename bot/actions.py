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
    if self.townhalls.ready.amount > 0:
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
        target = self.enemy_units.random
        for u in self.units().idle:
            u.attack(target)

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
            scout = self.units(UnitTypeId.OBSERVER).random
            self.scouts_and_spots.append(scout)

    to_be_removed = []
    existing_ids = [unit.tag for unit in self.units]
    
    for s in self.scouts_and_spots:
        if s.tag not in existing_ids:
            to_be_removed.append(s)
          
    for s in to_be_removed:
        self.scouts_and_spots.remove(s)

    for s in self.scouts_and_spots:
        i = 0
        location = self.expand_dis_dir[i]
        s.move(location)
        i += 1

async def move_towards_enemy(self):
    pos = position.Point2(position.Pointlike((self.enemy_start_locations[0].x, self.enemy_start_locations[0].y)))
    await helper_function(self, pos)

async def move_towards_map_center(self):
    pos = position.Point2(position.Pointlike((self.game_info.map_center.x, self.game_info.map_center.y)))
    await helper_function(self, pos)

async def move_towards_map_side_left(self):
    pos = position.Point2(position.Pointlike((self.game_info.map_center.x - self.game_info.map_size.x / 4, self.game_info.map_center.y -  self.game_info.map_size.y / 4)))
    await helper_function(self, pos)

async def move_towards_map_side_right(self):
    pos = position.Point2(position.Pointlike((self.game_info.map_center.x + self.game_info.map_size.x / 4, self.game_info.map_center.y +  self.game_info.map_size.y / 4)))
    await helper_function(self, pos)

async def do_nothing(self):
    print("StandDown")

async def helper_function(self, pos):
    for u in self.units(UnitTypeId.ZEALOT):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.SENTRY):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.STALKER):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.ADEPT):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.HIGHTEMPLAR):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.DARKTEMPLAR):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.PHOENIX):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.ORACLE):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.TEMPEST):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.CARRIER):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.MOTHERSHIP):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.OBSERVER):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.WARPPRISM):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.IMMORTAL):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.COLOSSUS):
        if u.is_idle:
            u.attack(pos)
    for u in self.units(UnitTypeId.DISRUPTOR):
        if u.is_idle:
            u.attack(pos)
