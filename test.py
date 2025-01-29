# from line_provider.controller import EventsController
#
# c = EventsController()
# c1 = EventsController()
# print(id(c) == id(c1))

from bet_maker.redis_controller import RedisController
import asyncio


#
#
async def run():
    r = RedisController()
    await r._flush()
    print("Created")


if __name__ == "__main__":
    asyncio.run(run())
