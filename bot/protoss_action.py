import sc2
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2 import position
from sc2.player import Bot, Computer
import random
    
# Buildings needed in greater numbers
    
async def build_pylons(self):
    nexus = self.townhalls.ready.random
    x = random.uniform(1, 2) * self.enemy_start_locations[0][0]
    y = random.uniform(1, 2) * self.enemy_start_locations[0][1]
    build_pos = position.Point2(position.Pointlike((x,y)))
    pos = nexus.position.towards(build_pos, random.uniform(8, 15))
    if (self.supply_left < 4
            and self.already_pending(UnitTypeId.PYLON) == 0
            and self.can_afford(UnitTypeId.PYLON)):
        await self.build(UnitTypeId.PYLON, near=pos)


async def build_gateways(self):
    if (self.structures(UnitTypeId.PYLON).ready
            and self.can_afford(UnitTypeId.GATEWAY)
            and self.structures(UnitTypeId.GATEWAY).amount < 3 + self.structures(UnitTypeId.NEXUS).amount
            and self.already_pending(UnitTypeId.GATEWAY) == 0):
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        await self.build(UnitTypeId.GATEWAY, near=pylon)

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

async def build_robotics_facility(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.CYBERNETICSCORE):
            if not self.structures(UnitTypeId.ROBOTICSFACILITY):
                if (self.can_afford(UnitTypeId.ROBOTICSFACILITY)
                        and self.already_pending(UnitTypeId.ROBOTICSFACILITY) == 0):
                    await self.build(UnitTypeId.ROBOTICSFACILITY, near = pylon)


async def expand(self):
    if self.structures(UnitTypeId.NEXUS).amount < 3 \
            and self.can_afford(UnitTypeId.NEXUS) \
            and self.already_pending(UnitTypeId.NEXUS) == 0:
        await self.expand_now()

async def build_shield_battery(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.CYBERNETICSCORE):
            if (self.can_afford(UnitTypeId.SHIELDBATTERY)
                and self.already_pending(UnitTypeId.SHIELDBATTERY) == 0):
                await self.build(UnitTypeId.SHIELDBATTERY, near = pylon)

async def build_stargate(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.CYBERNETICSCORE):
            if not self.structures(UnitTypeId.STARGATE):
                if (self.can_afford(UnitTypeId.STARGATE)
                    and self.already_pending(UnitTypeId.STARGATE) == 0):
                    await self.build(UnitTypeId.STARGATE, near = pylon)

async def build_photon_cannon(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.FORGE):
            if (self.can_afford(UnitTypeId.PHOTONCANNON)
                and self.already_pending(UnitTypeId.PHOTONCANNON) == 0):
                await self.build(UnitTypeId.PHOTONCANNON, near = pylon)

# Buildings needed in smaller numbers

async def build_cyber_core(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.GATEWAY).ready:
            if not self.structures(UnitTypeId.CYBERNETICSCORE):
                if (self.can_afford(UnitTypeId.CYBERNETICSCORE)
                    and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0):
                        await self.build(UnitTypeId.CYBERNETICSCORE, near = pylon)

async def build_robotics_bay(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.ROBOTICSFACILITY):
            if not self.structures(UnitTypeId.ROBOTICSBAY):
                if (self.can_afford(UnitTypeId.ROBOTICSBAY)
                        and self.already_pending(UnitTypeId.ROBOTICSBAY) == 0):
                    await self.build(UnitTypeId.ROBOTICSBAY, near = pylon)

async def build_twilight_council(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.CYBERNETICSCORE):
            if not self.structures(UnitTypeId.TWILIGHTCOUNCIL):
                if (self.can_afford(UnitTypeId.TWILIGHTCOUNCIL)
                        and self.already_pending(UnitTypeId.TWILIGHTCOUNCIL) == 0):
                    await self.build(UnitTypeId.TWILIGHTCOUNCIL, near = pylon)

async def build_templar_archives(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL):
            if not self.structures(UnitTypeId.TEMPLARARCHIVE):
                if (self.can_afford(UnitTypeId.TEMPLARARCHIVE)
                        and self.already_pending(UnitTypeId.TEMPLARARCHIVE) == 0):
                    await self.build(UnitTypeId.TEMPLARARCHIVE, near = pylon)

async def build_dark_shrine(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.TWILIGHTCOUNCIL):
            if not self.structures(UnitTypeId.DARKSHRINE):
                if (self.can_afford(UnitTypeId.DARKSHRINE)
                        and self.already_pending(UnitTypeId.DARKSHRINE) == 0):
                    await self.build(UnitTypeId.DARKSHRINE, near = pylon)

async def build_fleet_beacon(self):
    if self.structures(UnitTypeId.PYLON).ready:
        pylon = self.structures(UnitTypeId.PYLON).ready.random
        if self.structures(UnitTypeId.STARGATE):
            if not self.structures(UnitTypeId.FLEETBEACON):
                if (self.can_afford(UnitTypeId.FLEETBEACON)
                    and self.already_pending(UnitTypeId.FLEETBEACON) == 0):
                    await self.build(UnitTypeId.FLEETBEACON, near = pylon)

async def build_forge(self):
    if not self.structures(UnitTypeId.FORGE):
        if(self.structures(UnitTypeId.PYLON).ready
           and self.can_afford(UnitTypeId.FORGE)):
            pylon = self.structures(UnitTypeId.PYLON).ready.random
            await self.build(UnitTypeId.FORGE, near = pylon)

# Workers and Units

# Workers

async def build_workers(self):
    nexus = self.townhalls.ready.random
    if (self.can_afford(UnitTypeId.PROBE)
            and nexus.is_idle
            and self.workers.amount <= self.townhalls.amount * 22):
        nexus.train(UnitTypeId.PROBE)

# Gateway units

async def train_stalker(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if (self.structures(UnitTypeId.CYBERNETICSCORE)):
            if(self.can_afford(UnitTypeId.STALKER)
               and gateway.is_idle):
                gateway.train(UnitTypeId.STALKER)
                break

async def train_zealot(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if(self.can_afford(UnitTypeId.ZEALOT)
           and gateway.is_idle):
            gateway.train(UnitTypeId.ZEALOT)
            break

async def train_sentry(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if (self.structures(UnitTypeId.CYBERNETICSCORE)):
            if(self.can_afford(UnitTypeId.SENTRY)
               and gateway.is_idle):
                gateway.train(UnitTypeId.SENTRY)
                break

async def train_adept(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if(self.structures(UnitTypeId.CYBERNETICSCORE)):
            if(self.can_afford(UnitTypeId.ADEPT)
               and gateway.is_idle):
                gateway.train(UnitTypeId.ADEPT)
                break

async def train_high_templar(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if(self.structures(UnitTypeId.TEMPLARARCHIVE)):
            if(self.can_afford(UnitTypeId.HIGHTEMPLAR)
               and gateway.is_idle):
                gateway.train(UnitTypeId.HIGHTEMPLAR)
                break

async def train_dark_templar(self):
    for gateway in self.structures(UnitTypeId.GATEWAY).ready:
        if(self.structures(UnitTypeId.DARKSHRINE)):
            if(self.can_afford(UnitTypeId.DARKTEMPLAR)
               and gateway.is_idle):
                gateway.train(UnitTypeId.DARKTEMPLAR)
                break

# Stargate units

async def train_phoenix(self):
    for stargate in self.structures(UnitTypeId.STARGATE).ready:
        if(self.can_afford(UnitTypeId.PHOENIX)
           and stargate.is_idle):
            stargate.train(UnitTypeId.PHOENIX)
            break

async def train_oracle(self):
    for stargate in self.structures(UnitTypeId.STARGATE).ready:
        if(self.can_afford(UnitTypeId.ORACLE)
           and stargate.is_idle):
            stargate.train(UnitTypeId.ORACLE)
            break

async def train_void_ray(self):
    for stargate in self.structures(UnitTypeId.STARGATE).ready:
        if(self.can_afford(UnitTypeId.VOIDRAY)
           and stargate.is_idle):
            stargate.train(UnitTypeId.VOIDRAY)
            break

async def train_tempest(self):
    for stargate in self.structures(UnitTypeId.STARGATE).ready:
        if(self.structures(UnitTypeId.FLEETBEACON)):
            if(self.can_afford(UnitTypeId.TEMPEST)
               and stargate.is_idle):
                stargate.train(UnitTypeId.TEMPEST)
                break

async def train_carrier(self):
    for stargate in self.structures(UnitTypeId.STARGATE).ready:
        if(self.structures(UnitTypeId.FLEETBEACON)):
            if(self.can_afford(UnitTypeId.CARRIER)
               and stargate.is_idle):
                stargate.train(UnitTypeId.CARRIER)

async def train_mothership(self):
    for nexus in self.structures(UnitTypeId.NEXUS).ready:
        if(self.structures(UnitTypeId.FLEETBEACON)):
            if(self.can_afford(UnitTypeId.MOTHERSHIP)
               and nexus.is_idle):
                nexus.train(UnitTypeId.MOTHERSHIP)
                break

# Robotics facility units

async def train_observer(self):
    for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
        if(self.can_afford(UnitTypeId.OBSERVER)
           and robotic_facility.is_idle):
            robotic_facility.train(UnitTypeId.OBSERVER)

async def train_warp_prism(self):
    for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
        if(self.can_afford(UnitTypeId.WARPPRISM)
           and robotic_facility.is_idle):
            robotic_facility.train(UnitTypeId.WARPPRISM)

async def train_immortal(self):
    for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
        if(self.can_afford(UnitTypeId.IMMORTAL)
           and robotic_facility.is_idle):
            robotic_facility.train(UnitTypeId.IMMORTAL)

async def train_colossus(self):
    for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
        if self.structures(UnitTypeId.ROBOTICSBAY):
            if(self.can_afford(UnitTypeId.COLOSSUS)
               and robotic_facility.is_idle):
                robotic_facility.train(UnitTypeId.COLOSSUS)

async def train_disruptor(self):
    for robotic_facility in self.structures(UnitTypeId.ROBOTICSFACILITY).ready:
        if self.structures(UnitTypeId.ROBOTICSBAY):
            if(self.can_afford(UnitTypeId.DISRUPTOR)
               and robotic_facility.is_idle):
                robotic_facility.train(UnitTypeId.DISRUPTOR)

# Abilities and Power ups

# Cybernetics core abilities

async def buy_warp_gate(self):
    if(self.structures(UnitTypeId.CYBERNECTICSCORE).ready
       and self.can_afford(AbilityId.RESEARCH_WARPGATE)
       and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH)):
        cybercore = self.structures(UnitTypeId.CYBERNECTICSCORE).ready.first
        cybercore.research(UpgradeId.WARPGATERESEARCH)

async def buy_air_weapons(self):
    if(self.structures(UnitTypeId.CYBERNECTICSCORE).ready
       and self.can_afford(AbilityId.RESEARCH_AIRWEAPONS)
       and self.already_pending_upgrade(UpgradeId.AIRWEAPONSRESEARCH)):
        cybercore = self.structures(UnitTypeId.CYBERNECTICSCORE).ready.first
        cybercore.research(UpgradeId.AIRWEAPONSRESEARCH)

async def buy_air_aromor(self):
    if(self.structures(UnitTypeId.CYBERNECTICSCORE).ready
       and self.can_afford(AbilityId.RESEARCH_AIRAROMOR)
       and self.already_pending_upgrade(UpgradeId.AIRARMORRESEARCH)):
        cybercore = self.structures(UnitTypeId.CYBERNECTICSCORE).ready.first
        cybercore.research(UpgradeId.AIRARMORRESEARCH)


# Templar archives abilities

async def buy_psionic_storm(self):
    if(self.structures(UnitTypeId.TEMPLARARCHIVES).ready
       and self.can_afford(AbilityId.RESEARCH_PSIONICSTORM)
       and self.already_pending_upgrade(UpgradeId.PSIONICSTORMRESEARCH)):
        templararchives = self.structures(UnitTypeId.TEMPLARARCHIVES).ready.first
        templararchives.research(UpgradeId.PSIONICSTORMRESEARCH)

# Dark shrine abilities

async def buy_shadow_stride(self):
    if(self.structures(UnitTypeId.DARKSHRINE).ready
       and self.can_afford(AbilityId.RESEARCH_SHADOWSTRIDE)
       and self.already_pending_upgrade(UpgradeId.SHADOWSTRIDERESEARCH)):
        darkshrine = self.structures(UnitTypeId.DARKSHRINE).ready.first
        darkshrine.research(UpgradeId.SHADOWSTRIDERESEARCH)

# Twilight council abilities

async def buy_charge(self):
    if(self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
       and self.can_afford(AbilityId.RESEARCH_CHARGE)
       and self.already_pending_upgrade(UpgradeId.CHARGERESEARCH)):
        twilightcouncil = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
        twilightcouncil.research(UpgradeId.CHARGERESEARCH)

async def buy_blink(self):
    if(self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
       and self.can_afford(AbilityId.RESEARCH_BLINK)
       and self.already_pending_upgrade(UpgradeId.BLINKRESEARCH)):
        twilightcouncil = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
        twilightcouncil.research(UpgradeId.BLINKRESEARCH)

async def buy_resonaiting_glaives(self):
    if(self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready
       and self.can_afford(AbilityId.RESEARCH_RESONATINGGLAIVES)
       and self.already_pending_upgrade(UpgradeId.RESONATINGGLAIVESRESEARCH)):
        twilightcouncil = self.structures(UnitTypeId.TWILIGHTCOUNCIL).ready.first
        twilightcouncil.research(UpgradeId.RESONATINGGLAIVESRESEARCH)

# Random recruitment of units

async def recruit_from_gateway(self):
    for i in range(self.structures(UnitTypeId.GATEWAY).amount):
        c = random.randint(0, 5)
        if c == 0:
            await train_zealot(self)
        elif c == 1:
            await train_sentry(self)
        elif c == 2:
            await train_stalker(self)
        elif c == 3:
            await train_adept(self)
        elif c == 4:
            await train_high_templar(self)
        elif c == 5:
            await train_dark_templar(self)

async def recruit_from_stargate(self):
    for i in range(self.structures(UnitTypeId.STARGATE).amount):
        c = random.randint(0, 5)
        if c == 0:
            await train_phoenix(self)
        elif c == 1:
            await train_oracle(self)
        elif c == 2:
            await train_void_ray(self)
        elif c == 3:
            await train_tempest(self)
        elif c == 4:
            await train_carrier(self)
        elif c == 5:
            await train_mothership(self)

async def recruit_from_roboticsfacility(self):
    for i in range(self.structures(UnitTypeId.ROBOTICSFACILITY).amount):
        c = random.randint(0, 4)
        if c == 0:
            await train_observer(self)
        elif c == 1:
            await train_warp_prism(self)
        elif c == 2:
            await train_immortal(self)
        elif c == 3:
            await train_colossus(self)
        elif c == 4:
            await train_disruptor(self)

async def recruit(self, isTime):
    if isTime:
        await recruit_from_gateway(self)
        await recruit_from_stargate(self)
        await recruit_from_roboticsfacility(self)
    else:
        c = random.randint(0, 2)
        if c == 0:
            await recruit_from_gateway(self)
        elif c == 1:
            await recruit_from_stargate(self)
        elif c == 2:
            await recruit_from_roboticsfacility(self)
