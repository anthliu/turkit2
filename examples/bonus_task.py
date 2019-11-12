import sys
import argparse
import asyncio

from context import turkit2
from turkit2.common import BonusTask
from utils import get_client

def main(args):
    client = get_client(None, production=args.production)

    task = BonusTask(
        client,
        title=args.title,
        reward=args.reward,
        description=args.description,
        worker_ids=args.worker_ids,
        duration=600,
        lifetime=60*60*48
    )

    async def proc():
        async for answer, assignment in task.ask_async(assignments=len(args.worker_ids), verbosity=100, message=args.message):
            print('Bonus done for worker:', answer)
            print(assignment)

    asyncio.run(proc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Create a bonus task for a worker(s).',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-w', '--worker_ids',
            help='Worker IDs', type=str, nargs="+")
    parser.add_argument('-r', '--reward', type=str, required=True, help='Reward for bonus -- example: 0.01 for 1 cent.')
    parser.add_argument('--title', type=str, help='Title of bonus hit created', default='Worker Bonus')
    parser.add_argument('--description', type=str, help='Description of bonus hit created', default='Worker Bonus')
    parser.add_argument('--message', help='Text will be shown in the bonus HIT.', type=str, default='Thank you!')
    parser.add_argument('--production', help='Use in production. Use carefully!', action='store_true')

    args = parser.parse_args()
    main(args)
