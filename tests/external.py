import sys
import asyncio

from context import turkit2
from turkit2.common import External
from utils import get_client

client = get_client()

task = External(client, 'Test2', '0.01', 'test test', 600, 6000)

#print(task.preview(text='This library is the best!', question="Does this text follow pattern: 'enthusiastic'"))
async def proc():
    async for answer, assignment in task.ask_async(verbosity=100, url=sys.argv[1]):
        print(answer)
        print(assignment)

asyncio.run(proc())
