import sys
import asyncio

from context import turkit2
from turkit2.common import External
from utils import get_client

client = get_client(None)

task = External(
    client,
    title='Test2',
    reward='0.01',
    description='test test',
    duration=600,
    lifetime=60*60*24
)

async def proc():
    async for answer, assignment in task.ask_async(verbosity=100, url=sys.argv[1]):
        print(answer)
        print(assignment)

async def main():
    tasks = []
    for _ in range(20):
        tasks.append(asyncio.create_task(proc()))
    await asyncio.gather(*tasks)

asyncio.run(main())
