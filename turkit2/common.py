from pathlib import Path
from typing import List, Tuple
from jinja2 import Template

from turkit2.base import Task

class External(Task):
    def __init__(self, mturk_client,
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
        schema = None
        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat, base_schema='external_question.xml')

    def _render(self, url):
        xml_question = self.question_schema.render(external_url=url.replace('&', '&amp;'))
        return xml_question

class HumanIO(Task):
    def __init__(self, mturk_client,
        elements: List[Tuple[str, object]],
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
        TODO: Documentation
        '''
        with (Path(__file__).parent / 'schemas' / 'hio.html').open() as f:
            schema = Template(f.read())

        self.elements = elements
        self.elem_id_to_idx = {id_: idx for idx, (id_, _) in enumerate(self.elements)}

        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat)

    def _render(self, parameters):
        parameters = dict(parameters)
        elem_args = [{} for _ in range(len(self.elements))]
        for id_, args in parameters.items():
            elem_args[self.elem_id_to_idx[id_]] = args

        rendered_elements = [elem.render(**args) for (id_, elem), args in zip(self.elements, elem_args)]

        return super()._render(rendered_elements=rendered_elements)


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
