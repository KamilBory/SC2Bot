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
from bot import protoss_action
from bot import actions

HEADLESS = False

move_penalty = -1
enemy_killed = 5
enemy_building = 10
enemy_nexus = 25
win = 200
ally_killed = -10
ally_building = -15
ally_nexus = -20
loss = -300

start_q_table = None

learning_rate = 0.1
discount = 0.95
epsilon = 0.9

ALLY_AMOUNT = 0
BUILDING_AMOUNT = 0
NEXUS_AMOUNT = 0
ALL_AMOUNT = 0
ENEMY_AMOUNT = 0
ENEMY_BUILDING = 0
ENEMY_NEXUS = 0


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
        self.do_something_after = 0
        self.use_model = False
        self.scouts_and_spots = []
        self.train_data = []
        self.isTime = False

        self.choices = {0: actions.attack_known_enemy_unit,
                        1: actions.attack_known_enemy_structure,
                        2: actions.defend_nexus,
                        3: actions.scout,
                        4: actions.move_towards_enemy,
                        5: actions.move_towards_map_center,
                        6: actions.move_towards_map_side_right,
                        7: actions.move_towards_map_side_left,
                        }

        self.reward = 0

        self.q_table = {}
        self.unit_tab = []

        if self.use_model:
           print("USING MODEL!")
           self.model = keras.models.load_model("BasicCNN-30-epochs-0.0001-LR-4.2")

        if start_q_table is None:
            for i in range(0, 8):
                self.q_table[i] = np.random.uniform(-5, 0)

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

        await protoss_action.build_workers(self)
        await protoss_action.build_pylons(self)
        await protoss_action.build_gateways(self)
        await protoss_action.build_gas(self)
        await protoss_action.build_cyber_core(self)
        await protoss_action.build_robotics_facility(self)
        await protoss_action.build_robotics_bay(self)
        await protoss_action.build_stargate(self)
        await protoss_action.build_fleet_beacon(self)
        await protoss_action.build_forge(self)
        await protoss_action.build_twilight_council(self)
        await protoss_action.build_templar_archives(self)
        await protoss_action.build_dark_shrine(self)
        await protoss_action.expand(self)

        print(self.units().amount)

        if self.time > 240.0:
            self.isTime = True

        if self.time % 15 == 0:
            await protoss_action.recruit(self, self.isTime)

        await actions.intel(self, HEADLESS)
        if self.time > self.do_something_after:
            self.do_something_after = self.time + random.uniform(5, 15)
            await self.do_something()

        pass

    async def do_something(self):
        '''if self.use_model:
            prediction = self.model.predict([self.flipped.reshape([-1, 176, 200, 3])])
            choice = np.argmax(prediction[0])
        else:
            choice = random.randint(0, 7)
            print(choice)

        try:
            await self.choices[choice](self)
        except Exception as e:
            print(str(e))

        y = np.zeros(8)
        y[choice] = 1
        self.train_data.append([y, self.flipped]) '''

        ALLY_AMOUNT = self.units().amount
        BUILDING_AMOUNT = self.structures().amount
        NEXUS_AMOUNT = self.structures(UnitTypeId.NEXUS).amount
        ALL_AMOUNT = self.all_units().amount
        ENEMY_AMOUNT = self.all_units().enemy.not_structure.ready.amount
        ENEMY_BUILDING = self.all_units().enemy.ready.amount - self.all_units().enemy.not_structure.ready.amount
        ENEMY_NEXUS = self.all_units(UnitTypeId.NEXUS).amount

        #print(ENEMY_BUILDING)

        episode_reward = 0
        if np.random.random() > epsilon:
            #action = np.argmax(q_table[obs])
            action = np.random.randint(0, 7)
        else:
            action = np.random.randint(0, 7)
        await self.choices[action](self)

        max_future_q = np.max(self.q_table[action])
        current_q = self.q_table[action]

        await self.predictReward()

        if self.reward == win:
            new_q = win
        else:
            new_q = (1 - learning_rate) * current_q + learning_rate * (self.reward + discount * max_future_q)
        self.q_table[action] = new_q

        episode_reward += self.reward

    async def getUnits(self):
        for unitTag in self.all_units().ready:
            if unitTag not in self.unit_tab:
                self.unit_tab.append(unitTag)

        #print(len(self.units()))
        #print(len(self.enemy_structures()))
        #print(len(self.all_units().owned.not_structure.ready))

        #unit_tab = [unit.tag for unit in self.all_units()]
        #building_table = [build.tag for build in self.structures()]
        #building_table1 = [build.tag for build in self.enemy_structures()]

    async def predictReward(self):
        self.reward = 0

        await self.getUnits()
        for unit in self.unit_tab:
            if unit not in self.all_units().ready:
                if unit.is_mine:
                    if unit.is_structure:
                        if unit in self.structures(UnitTypeId.NEXUS):
                            self.reward += ally_nexus
                            self.unit_tab.remove(unit)
                            #print('Ally nexus')
                        else:
                            self.reward += ally_building
                            self.unit_tab.remove(unit)
                            #print('Ally building')
                    else:
                        self.reward += ally_killed
                        self.unit_tab.remove(unit)
                        #print('Ally killed')
                else:
                    if unit.is_structure:
                        if unit in self.structures(UnitTypeId.NEXUS):
                            self.reward += enemy_nexus
                            self.unit_tab.remove(unit)
                            #print('Enemy nexus')
                        else:
                            self.reward += enemy_building
                            self.unit_tab.remove(unit)
                            #print('Enemy building')
                    else:
                        self.reward += enemy_killed
                        self.unit_tab.remove(unit)
                        #print('Enemy killed')

        self.reward += move_penalty
        #print(reward)

