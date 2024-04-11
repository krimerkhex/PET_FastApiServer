import asyncio
from enum import Enum, auto
from random import choice


class Action(Enum):
    HIGHKICK = auto()
    LOWKICK = auto()
    HIGHBLOCK = auto()
    LOWBLOCK = auto()


class Agent:
    def __aiter__(self, health=5):
        self.health = health
        self.actions = list(Action)
        return self

    async def __anext__(self):
        return choice(self.actions)


def kung_fu(action):
    r_value = Action.LOWKICK
    match action:
        case Action.LOWKICK:
            r_value = Action.LOWBLOCK
        case Action.HIGHKICK:
            r_value = Action.HIGHBLOCK
        case Action.LOWBLOCK:
            r_value = Action.HIGHKICK
    return r_value


def hit(neo_action, agent_action):
    r_value = False
    if agent_action is Action.HIGHBLOCK and neo_action is Action.LOWKICK or agent_action is Action.LOWBLOCK and neo_action is Action.HIGHKICK:
        r_value = True
    return r_value


async def fight():
    neo = list(Action)
    agent_1 = Agent()
    async for agent_action in agent_1:
        neo_action = kung_fu(agent_action)
        agent_1.health -= hit(neo_action, agent_action)
        print(f"Agent: {agent_action}, Neo: {neo_action}, Agent Health: {agent_1.health}")
        if agent_1.health == 0:
            print("Neo wins, FATALITY!")
            break


async def fight_with_one(agent_action, agent, counter):
    if agent.health > 0:
        neo_action = kung_fu(agent_action)
        agent.health -= hit(neo_action, agent_action)
        print(f"Agent {counter}: {agent_action}, Neo: {neo_action}, Agent Health: {agent.health}")


async def fightmany(agent, counter):
    async for agent_action in agent:
        task = asyncio.create_task(fight_with_one(agent_action, agent, counter))
        if agent.health == 0:
            break
        else:
            await task


async def prepare_to_fightmany(n):
    neo = list(Action)
    agents = [Agent() for _ in range(n)]
    tasks = []
    counter = 1
    for agent in agents:
        tasks.append(asyncio.create_task(fightmany(agent, counter)))
        counter += 1
    for task in tasks:
        await task
    print("Neo wins, FATALITY!")


async def main(n):
    if n == 1:
        task = asyncio.create_task(fight())
        await task
    else:
        task = asyncio.create_task(prepare_to_fightmany(n))
        await task


if __name__ == "__main__":
    asyncio.run(main(10))
