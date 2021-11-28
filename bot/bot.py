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
import pandas as pd
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

class QLearningTable:
    def __init__(self, actions, learning_rate = 0.01, decay = 0.9):
        self.actions = actions
        self.learning_rate = learning_rate
        self.decay = decay
        self.QTable = pd.DataFrame(columns = self.actions, dtype = np.float64)

    async def chooseAction(self, observation, e_greedy = 0.9):
        await self.checkState(observation)
        if np.random.uniform() < e_greedy:
            state_action = self.QTable.loc[observation, :]
            action = np.random.choice(state_action[state_action == np.max(state_action)].index)
        else:
            action = np.random.choice(self.actions)

        if action == "attack_known_enemy_unit":
            act = 0
        elif action == "attack_known_enemy_structure":
            act = 1
        elif action == "defend_nexus":
            act = 2
        elif action == "scout":
            act = 3
        elif action == "move_towards_enemy":
            act = 4
        elif action == "move_towards_map_center":
            act = 5
        elif action == "move_towards_map_side_right":
            act = 6
        elif action == "move_towards_map_side_left":
            act = 7

        return act

    async def learn(self, state, action, reward, s_):
        await self.checkState(s_)
        q_predict = self.QTable.loc[state, action]
        if s_ != 'terminal':
            q_target = reward + self.decay * self.QTable.loc[s_, :].max()
        else:
            q_target = reward

        self.QTable.loc[state, action] += self.learning_rate * (q_target - q_predict)


    async def checkState(self, state):
        if state not in self.QTable.index:
            self.QTable = self.QTable.append(pd.Series([0] * len(self.actions),
                                                       index = self.QTable.columns,
                                                       name = state))


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
        self.previous_action = None
        self.previous_state = None

        self.choices = {0: actions.attack_known_enemy_unit,
                        1: actions.attack_known_enemy_structure,
                        2: actions.defend_nexus,
                        3: actions.scout,
                        4: actions.move_towards_enemy,
                        5: actions.move_towards_map_center,
                        6: actions.move_towards_map_side_right,
                        7: actions.move_towards_map_side_left,
                        }

        self.choicesQLearn = ["attack_known_enemy_unit",
                              "attack_known_enemy_structure",
                              "defend_nexus",
                              "scout",
                              "move_towards_enemy",
                              "move_towards_map_center",
                              "move_towards_map_side_right",
                              "move_towards_map_side_left"
                              ]

        self.reward = 0
        self.visibleCount = 0

        self.q_table = {}
        self.unit_tab = []
        self.unit_tab1 = []
        self.QTable = QLearningTable(self.choicesQLearn)

        if self.use_model:
           print("USING MODEL!")
           self.model = keras.models.load_model("BasicCNN-30-epochs-0.0001-LR-4.2")


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

        await self.getUnits()

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

        #print(len(self.unit_tab1))


        if self.time > 240.0:
            self.isTime = True

        if self.time % 15 == 0:
            await protoss_action.recruit(self, self.isTime)

        await actions.intel(self, HEADLESS)
        if self.time > self.do_something_after:
            self.do_something_after = self.time + random.uniform(4, 10)
            await self.do_something()

        await self.predictReward()

        pass

    async def do_something(self):
        #print(ENEMY_BUILDING)

        state = str(await self.getState())
        action = await self.QTable.chooseAction(state)
        await self.choices[action](self)
        actionString = self.choicesQLearn[action]
        if self.previous_action is not None:
            await self.QTable.learn(self.previous_state, self.previous_action, self.reward, state)
        self.previous_state = state
        self.previous_action = actionString

        self.reward = 0

        '''episode_reward = 0
        if np.random.random() > epsilon:
            #action = np.argmax(q_table[obs])
            action = np.random.randint(0, 7)
        else:
            action = np.random.randint(0, 7)
        await self.choices[action](self)

        max_future_q = np.max(self.q_table[action])
        current_q = self.q_table[action]

        if self.reward == win:
            new_q = win
        else:
            new_q = (1 - learning_rate) * current_q + learning_rate * (self.reward + discount * max_future_q)
        self.q_table[action] = new_q

        episode_reward += self.reward'''

    async def getUnits(self):
        for unitTag in self.all_units().ready:
            if unitTag not in self.unit_tab and unitTag not in self.all_units(UnitTypeId.PROBE) and (unitTag.is_mine or unitTag.is_enemy):
                self.unit_tab.append(unitTag)

        self.unit_tab1.clear()
        for unitTag1 in self.all_units().ready:
            if unitTag1 not in self.all_units(UnitTypeId.PROBE) and (unitTag1.is_mine or unitTag1.is_enemy):
                self.unit_tab1.append(unitTag1)

        #print(len(self.units()))
        #print(len(self.enemy_structures()))
        #print(len(self.all_units().owned.not_structure.ready))

        #unit_tab = [unit.tag for unit in self.all_units()]
        #building_table = [build.tag for build in self.structures()]
        #building_table1 = [build.tag for build in self.enemy_structures()]

    async def predictReward(self):

        #print(len(self.unit_tab), "   ", len(self.unit_tab1))
        #print(self.units()[3].name)
        for u in self.unit_tab:
            if u not in self.unit_tab1:
                if u.is_mine:
                    if u.is_structure:
                        if u.name == "Nexus":
                            self.reward += ally_nexus
                            self.unit_tab.remove(u)
                            print('Ally nexus')
                        else:
                            self.reward += ally_building
                            self.unit_tab.remove(u)
                            print('Ally building')
                    else:
                        self.reward += ally_killed
                        self.unit_tab.remove(u)
                        print('Ally killed')
                else:
                    if u.is_visible:
                        if u.is_structure:
                            if u.name == "Nexus":
                                self.reward += enemy_nexus
                                self.unit_tab.remove(u)
                                print('Enemy nexus')
                            else:
                                self.reward += enemy_building
                                self.unit_tab.remove(u)
                                print('Enemy building')
                        else:
                            self.reward += enemy_killed
                            self.unit_tab.remove(u)
                            print('Enemy killed')

        self.reward += move_penalty
        #print(reward)

    async def getState(self):
        enemyCount = 0
        allyCount = 0
        enemyattack = 0
        enemybuild = 0
        center = False
        left = False
        right = False

        for u in self.unit_tab:
            if not u.is_structure:
                if u.is_mine:
                    allyCount += 1
                else:
                    if self.enemy_units().closer_than(75, self.start_location).amount > 0:
                        enemyattack += 1
                    enemyCount += 1
            else:
                if u.is_enemy or u.is_snapshot:
                    enemybuild +=1

        if self.units().closer_than(10, position.Point2(
                position.Pointlike((self.game_info.map_center.x, self.game_info.map_center.y)))).amount > 0:
            center = True
        else:
            center = False
        if self.units().closer_than(10, position.Point2(position.Pointlike((
                                                                           self.game_info.map_center.x - self.game_info.map_size.x / 4,
                                                                           self.game_info.map_center.y - self.game_info.map_size.y / 4)))).amount > 0:
            left = True
        else:
            left = False
        if self.units().closer_than(10, position.Point2(position.Pointlike((
                                                                           self.game_info.map_center.x + self.game_info.map_size.x / 4,
                                                                           self.game_info.map_center.y + self.game_info.map_size.y / 4)))).amount > 0:
            right = True
        else:
            right = False

        return (enemyCount,
                allyCount,
                enemyattack,
                enemybuild,
                center,
                left,
                right)

