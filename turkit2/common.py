from pathlib import Path
from typing import List
from jinja2 import Template

from turkit2.base import Task

class HumanIO(Task):
    def __init__(self,
        title: str,
        reward: str,
        description: str,
        duration: int,
        lifetime: int,
        #
        keywords: str='',
        auto_approval_delay: int=7200,# 24 hours
        max_heartbeat: int=600,# 10 minutes
    ):
        '''
        TODO: INCOMPLETE
        '''
        self.schema_template = None# TODO do

        super().__init__(schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat)

class TextClassification(Task):
    def __init__(self, mturk_client,
        title: str,
        reward: str,
        description: str,
        duration: int,
        lifetime: int,
        categories: List[str],
        #
        question: str='Which label best suits the text?',
        short_instructions: str='''
<p>Read the task carefully and inspect the text.</p>
<p>Choose the appropriate label that best suits the text.</p>
''',
        full_instructions: str='''
<p>Read the task carefully and inspect the text.</p>
<p>Choose the appropriate label that best suits the text.</p>
''',
        keywords: str='',
        auto_approval_delay: int=7200,# 24 hours
        max_heartbeat: int=600,# 10 minutes
    ):
        '''
        TODO add documentation
        '''
        with (Path(__file__).parent / 'schemas' / 'text_classification.html').open() as f:
            schema = Template(f.read())
        self.question = question
        self.categories = categories
        self.short_instructions = short_instructions
        self.full_instructions = full_instructions
        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat)

    def _render(self, **schema_args):
        assert 'text' in schema_args
        schema_args.setdefault('question', self.question)
        schema_args.setdefault('short_instructions', self.short_instructions)
        schema_args.setdefault('full_instructions', self.full_instructions)
        schema_args.setdefault('categories', self.categories)

        return super()._render(**schema_args)

    def _parse(self, answer):
        result = super()._parse(answer)
        return next(iter(result.values()))
