import asyncio
from random import randint

from turkit2.common import HumanIO
from turkit2.primitive import IText, OChoice, OText
from utils import get_client

class ALogger(object):
    def __init__(self, quiet=False):
        self.count = 0
        self.quiet = quiet

    def log(self, id_, tag, s):
        if not self.quiet:
            print(f'{id_} - {tag}: {s}')

    def assign_id(self):
        ret = self.count
        self.count += 1
        return ret

class Turkomatic(object):
    def __init__(self, client, session='', verbosity=0, redundancy=3):
        self.client = client
        self.redundancy = redundancy
        self.verbosity = verbosity

        self.is_fair_task = HumanIO(
            self.client,
            elements=[
                ('prompt', IText()),
                ('answer', OChoice('answer'))
            ],
            title='Vote on whether this task is fair.',
            reward='0.03',
            description='Given a task description, vote whether this task can be done in 2 minutes.' + session,
            duration=600,
            lifetime=6000
        )

        self.subdivide_task = HumanIO(
            self.client,
            elements=[
                ('prompt', IText()),
                ('0', OText('0')),
                ('1', OText('1')),
                ('2', OText('2')),
                ('3', OText('3')),
                ('4', OText('4')),
            ],
            title='Break down a task into steps. [~1min]',
            reward='0.15',
            description='Given a task description, break down the task into smaller steps.' + session,
            duration=1800,
            lifetime=6000
        )

        self.verify_task = HumanIO(
            self.client,
            elements=[
                ('prompt', IText()),
                ('answer', OChoice('answer'))
            ],
            title='Vote on the work of other turkers',
            reward='0.03',
            description='Given other turkers work, vote on the best.' + session,
            duration=600,
            lifetime=6000
        )

        self.solve_task = HumanIO(
            self.client,
            elements=[
                ('prompt', IText()),
                ('answer', OText('answer'))
            ],
            title='Solve a simple task [~2min]',
            reward='0.30',
            description='You are asked to solve a simple task that is part of a larger task, broken down by other turkers.' + session,
            duration=1800,
            lifetime=6000
        )

        self.merge_task = HumanIO(
            self.client,
            elements=[
                ('prompt', IText()),
                ('answer', OText('answer'))
            ],
            title='Combine the work of other turkers [~30sec]',
            reward='0.10',
            description='You are given the text answers of turkers solving parts of a large task. Combine their answers into one.' + session,
            duration=1800,
            lifetime=600
        )

    def render_prompt(self, title, pre, post, task, context=None):
        prompt = f'''
        <h2>{title}</h2>
        <p>
            <b>About:</b>
            We are dividing a large task among several workers on MTurk.
            This is an experiment to see how complicated tasks can be shared
            between multiple workers on MTurk.
            <br>
            <b>Instructions:</b>
            {pre}
            <div style="background-color:#ff9999;padding:1%;">{task}</div>
            {post}
        </p>
        '''
        def render_context(context, overall=False):
            if len(context) == 0:
                return ''
            ctx = '<ol>'
            for subtask, subcontext in context.items():
                if subtask == task:
                    subtask = f'<b>{subtask} (this is your task)</b>'
                task_s = subtask + '\n' + render_context(subcontext)
                if overall:
                    ctx += f'<li><b>overall:</b>{task_s}</li>'
                else:
                    ctx += f'<li>{task_s}</li>'
            ctx += '</ol>'
            return ctx

        if context is not None:
            ctx_prompt = '<br>Here is the current plan made by other crowd workers:' + render_context(context, True)
        else:
            ctx_prompt = ''

        return prompt + ctx_prompt

    async def _is_fair(self, task, context=None):
        prompt = self.render_prompt(
            title='Is this task fair?',
            pre='Judge whether the following task can be completed within 2 minutes.',
            post='Your answer will be used to decide whether to subdivide this task or not.',
            task=task,
            context=None
        )
        votes = []
        async for answer, assignment in self.is_fair_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt, 'answer': ['yes', 'no']}
        ):
            votes.append(answer['answer'])
        best_vote = max(set(votes), key=votes.count)
        return best_vote == 'yes'

    async def _subdivide(self, task, context=None):
        prompt = self.render_prompt(
            title='Break down the task written in red.',
            pre='Help us plan how this work should be divided. Here is the task:',
            post='''
            <b>Do not solve this task by yourself.</b>
            Please break the task down into 2 or more steps. Write each step below.
            You may leave some steps blank.
            <br>
            Each step you suggest will be posted to Mechanical Turk again
            for another Turker to do. Make sure each step makes sense to another Turker.
            <br>
            Here is what makes a good answer:
            <ul>
            <li>Every step is a complete sentence or set of instructions.</li>
            <li>Every step contains all the information required to do a task.</li>
            <li>Every step explains clearly what a Turker should do.</li>
            <li>Every step can be understood itself without reading the original task in red.</li>
            </ul>
            <br>
            Your work will be checked for correctness before being approved.
            ''',
            task=task,
            context=None
        )
        divisions = []
        async for answer, assignment in self.subdivide_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt}
        ):
            answer_list = [answer[str(i)] for i in range(5)]
            task_list = [a for a in answer_list if a is not None and len(a) > 3]
            divisions.append(task_list)
        return divisions
    
    async def _solve(self, task, context):
        prompt = self.render_prompt(
            title='Solve a simple task.',
            pre='Please do the following task (in red) and enter the solution in the box at the bottom of this page.',
            post='If the instructions do not make sense, please look at the overall plan below and take your best guess.',
            task=task,
            context=context
        )
        solutions = []
        async for answer, assignment in self.solve_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt}
        ):
            solutions.append(answer['answer'])
        return solutions

    async def _merge(self, task, solutions, context=None):
        post = '\n'.join(f'<div style="background-color:#99ff99;padding:1%;"><b>Turker {i}:</b><br>{sol}</div>' for i, sol in enumerate(solutions))
        prompt = self.render_prompt(
            title='Merge Turker solutions',
            pre='Your goal is to find a solution to the following task (in red) by combining the answers of other Turkers (in green).',
            post=post + '<br>Please combine the solutions written above a single solution.',
            task=task,
            context=context
        )
        solutions = []
        async for answer, assignment in self.merge_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt}
        ):
            solutions.append(answer['answer'])
        return solutions

    async def _verify_subdivide(self, task, divisions, context=None):
        def render_breakdown(div):
            return '<ul>' + '\n'.join(f'<li>{x}</li>' for x in div) + '</ul>'
        post = ''
        for i, div in enumerate(divisions):
            r_div = render_breakdown(div)
            post += f'<div style="background-color:#99ff99;padding:1%;"><b>Turker {i}:</b>{r_div}</div>\n'

        prompt = self.render_prompt(
            title='Vote on the work of other turkers.',
            pre='''
            We gave several Turkers the following task (in red) and asked them to break it down into smaller tasks.
            <br>
            Here is what makes a good answer:
            <ul>
            <li>Every step is a complete sentence or set of instructions.</li>
            <li>Every step contains all the information required to do a task.</li>
            <li>Every step explains clearly what a Turker should do.</li>
            <li>Every step can be understood itself without reading the original task in red.</li>
            </ul>
            <br>
            Vote on which one you think is the best.
            ''',
            post=post,
            task=task,
            context=None
        )
        votes = []
        async for answer, assignment in self.verify_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt, 'answer': [f'Turker {i}' for i in range(len(divisions))]}
        ):
            votes.append(answer['answer'])
        best_vote = max(set(votes), key=votes.count)
        best_worker = int(best_vote.split()[1])
        return divisions[best_worker]

    async def _verify_solve(self, task, solutions, context=None):
        post = '\n'.join(f'<div style="background-color:#99ff99;padding:1%;"><b>Turker {i}:</b><br>{sol}</div>' for i, sol in enumerate(solutions))

        prompt = self.render_prompt(
            title='Vote on the work of other turkers.',
            pre='We gave several Turkers the following task (in red) and asked them solve it. Vote on which one you think is the best.',
            post=post,
            task=task,
            context=None
        )
        votes = []
        async for answer, assignment in self.verify_task.ask_async(
            verbosity=self.verbosity, assignments=self.redundancy,
            parameters={'prompt': prompt, 'answer': [f'Turker {i}' for i in range(len(solutions))]}
        ):
            votes.append(answer['answer'])
        best_vote = max(set(votes), key=votes.count)
        best_worker = int(best_vote.split()[1])
        return solutions[best_worker]

    async def ask_async(self, task, depth_limit, quiet=True):
        context = {task: {}}
        local = context[task]
        return await self.pds(task, depth_limit, context, local, ALogger(quiet=quiet))

    async def pds(self, task, depth_limit, context, local, logger):
        id_ = logger.assign_id()
        logger.log(id_, 'task', task)
        logger.log(id_, 'context', context)
        is_fair = await self._is_fair(task, context)
        logger.log(id_, 'is_fair', is_fair)
        if is_fair or depth_limit == 0:
            solutions = await self._solve(task, context)
            logger.log(id_, 'solutions', solutions)
            best_solution = await self._verify_solve(task, solutions, context)
            logger.log(id_, 'best solution', best_solution)
            return best_solution
        else:
            divisions = await self._subdivide(task, context)
            logger.log(id_, 'divisions', divisions)
            best_division = await self._verify_subdivide(task, divisions, context)
            logger.log(id_, 'best division', best_division)
            for step in best_division:
                local[step] = {}
            subtasks = []
            for step in best_division:
                subtasks.append(asyncio.create_task(
                    self.pds(step, depth_limit - 1, context, local[step], logger)
                ))

            sub_solutions = await asyncio.gather(*subtasks)
            logger.log(id_, 'subtask solutions', sub_solutions)
            merge_candidates = await self._merge(task, sub_solutions, context)
            logger.log(id_, 'merges', merge_candidates)
            best_merge = await self._verify_solve(task, merge_candidates, context)
            logger.log(id_, 'best merge', best_merge)
            return best_merge

def test():
    client = get_client()
    session = randint(0, 1000)
    turkomatic = Turkomatic(client, session=str(session), redundancy=1, verbosity=100)
    task = 'Do some research.'
    overall = 'Write a 3 paragraph essay on crowdsourcing'
    test_context = {
        overall: {
            'Do some research.': {},
            'Write the stuff.': {
                'do it 1': {},
                'do it 2': {}
            }
        }
    }
    test_divisions = [
        ['aowief', 'awoeif', 'aow', 'owe'],
        ['aoweif', 'oaw', 'oawregi'],
        ['24', '241']
    ]
    test_solutions = ['awoeief', 'aowasdf', '123']

    #asyncio.run(turkomatic._verify_solve(task, solutions=test_solutions, context=test_context))
    #asyncio.run(turkomatic._solve(task, context=test_context))
    #asyncio.run(turkomatic._merge(task, solutions=test_solutions, context=test_context))

    asyncio.run(turkomatic.ask_async(overall, 2, quiet=False))

if __name__ == '__main__':
    test()
