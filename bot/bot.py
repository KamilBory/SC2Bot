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
        #self.title = title
        self.scouts_and_spots = {}
        self.train_data = []
        self.isTime = False

        self.choices = {0: actions.attack_known_enemy_unit(self),
                        1: actions.attack_known_enemy_structure(self),
                        2: actions.defend_nexus(self),
                        3: actions.do_nothing(self),
                        }

        '''if self.use_model:
           print("USING MODEL!")
           self.model = keras.models.load_model("BasicCNN-30-epochs-0.0001-LR-4.2")'''

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
        # self.time = (self.state.game_loop / 22.4)
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

        if self.time > 240.0:
            isTime = True

        if self.time % 15 == 0:
            await protoss_action.recruit(self, time)

        #await actions.defend_nexus(self)

        if self.time > self.do_something_after:
            await actions.do_something(self)
        await actions.intel(self, HEADLESS)



        pass