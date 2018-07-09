# imports
import sc2
import random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, \
GATEWAY, CYBERNETICSCORE, STALKER, VOIDRAY, STARGATE
from examples.protoss.cannon_rush import CannonRushBot

class sc2_lechita_1(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 50

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assymilators()
        await self.expand()
        await self.build_offensive_buildings()
        await self.build_offensive_units()
        await self.attack()

    async def build_workers(self):
        if len(self.workers)<self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near = nexuses.first)

    async def build_assymilators(self):
        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(15., nexus)
            for vespene in vespenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1., vespene).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene))

    async def expand(self):
        if self.units(NEXUS).amount < ((self.iteration*3)/self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
            await self.expand_now()

    async def build_offensive_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < (self.iteration/self.ITERATIONS_PER_MINUTE):
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if len(self.units(STARGATE)) < (self.iteration/self.ITERATIONS_PER_MINUTE):
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    await self.build(STARGATE, near=pylon)


    async def build_offensive_units(self):
        for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0:
                if not self.units(STALKER).amount>self.units(VOIDRAY).amount:
                    await self.do(gateway.train(STALKER))
        for stargate in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(stargate.train(VOIDRAY))


    async def attack(self):
        aggressive_units = {STALKER: [15, 5],
                            VOIDRAY: [8, 3]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
                for single_unit in self.units(UNIT).idle:
                    await self.do( single_unit.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for  single_unit in self.units(UNIT).idle:
                        await self.do(single_unit.attack(random.choice(self.known_enemy_units)))


        if self.units(STALKER).amount > 1:
            if len(self.known_enemy_units)>0:
                for stalker in self.units(STALKER).idle:
                    await self.do(stalker.attack(random.choice(self.known_enemy_units)))

        if self.units(STALKER).amount > 15:
            for stalker in self.units(STALKER).idle:
                await self.do(stalker.attack(self.find_target(self.state)))

    def find_target(self, state):
        if len(self.known_enemy_units)>0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures)>0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

run_game(maps.get("Abyssal reef LE"), [
    Bot(Race.Protoss, sc2_lechita_1()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=False )
