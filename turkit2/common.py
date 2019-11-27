from pathlib import Path
from typing import List, Tuple, Optional
import uuid
from jinja2 import Template

from turkit2.base import Task
from turkit2.primitive import IText, OText
from turkit2.qualifications import Unique

class External(Task):
    """
    Use to post a HIT where the task is hosted in an external website.

    :param mturk_client: boto3 mturk client
    :param title: the HIT title shown to workers in the "marketplace"
    :type title: str
    :param reward: reward of completing the HIT in string (e.g. "0.15" is 15 cents)
    :type reward: str
    :param description: the HIT description shown to workers in the "marketplace"
    :type description: str
    :param duration: Time workers have to complete the HIT after accepting (seconds)
    :type duration: int
    :param lifetime: Time the HIT lasts in the "marketplace" (seconds)
    :type lifetime: int
    :param keywords: (default='') HIT keywords in "marketplace"
    :type keywords: str
    :param auto_approval_delay: (default=7200 (24 hours)) Time before a submitted HIT is automatically approved (seconds)
    :type auto_approval_delay: int
    :param max_heartbeat: (default=600 (10 minutes)) The maximum interval Turkit2 checks MTurk whether new assignments have been submitted
    :type max_heartbeat: int
    :param qualifications: (default=[]) List of qualifications (from qualifications module) restricting workers that can work on this HIT
    :type qualifications: List[qualifications]
    :param run_once: (default=None) Supply a unique ID to cache answers from workers so that when the same ID is supplied, the HIT is not posted again
    :type run_once: str, optional
    :param cache_path: (default=None) Supply a custom cache path for run_once. If not supplied, use current_dictory/.turkit_cache
    :type cache_path: str, optional
    """
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
        qualifications: List[object]=[],
        run_once=None,
        cache_path=None,
    ):
        schema = None
        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat, qualifications=qualifications, run_once=run_once, cache_path=cache_path, base_schema='external_question.xml')

    def _render(self, url):
        xml_question = self.question_schema.render(external_url=url.replace('&', '&amp;'))
        return xml_question

class HumanIO(Task):
    """
    Use to post a HIT where the task is hosted in an external website. Learn more in :ref:`HumanIO Tasks`.

    :param mturk_client: boto3 mturk client
    :param elements: The (ID, primitive) list composing the HumanIO task.
    :type elements: List[Tuplie[str, object]]
    :param title: the HIT title shown to workers in the "marketplace"
    :type title: str
    :param reward: reward of completing the HIT in string (e.g. "0.15" is 15 cents)
    :type reward: str
    :param description: the HIT description shown to workers in the "marketplace"
    :type description: str
    :param duration: Time workers have to complete the HIT after accepting (seconds)
    :type duration: int
    :param lifetime: Time the HIT lasts in the "marketplace" (seconds)
    :type lifetime: int
    :param keywords: (default='') HIT keywords in "marketplace"
    :type keywords: str
    :param auto_approval_delay: (default=7200 (24 hours)) Time before a submitted HIT is automatically approved (seconds)
    :type auto_approval_delay: int
    :param max_heartbeat: (default=600 (10 minutes)) The maximum interval Turkit2 checks MTurk whether new assignments have been submitted
    :type max_heartbeat: int
    :param qualifications: (default=[]) List of qualifications (from qualifications module) restricting workers that can work on this HIT
    :type qualifications: List[qualifications]
    :param run_once: (default=None) Supply a unique ID to cache answers from workers so that when the same ID is supplied, the HIT is not posted again
    :type run_once: str, optional
    :param cache_path: (default=None) Supply a custom cache path for run_once. If not supplied, use current_dictory/.turkit_cache
    :type cache_path: str, optional
    """
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
        qualifications: List[object]=[],
        run_once=None,
        cache_path=None,
    ):
        '''
        TODO: Documentation
        '''
        with (Path(__file__).parent / 'schemas' / 'hio_bootstrap.html').open() as f:
            schema = Template(f.read())

        self.elements = elements
        self.elem_id_to_idx = {id_: idx for idx, (id_, _) in enumerate(self.elements)}

        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat, qualifications=qualifications, run_once=run_once, cache_path=cache_path)

    def _render(self, parameters):
        parameters = dict(parameters)
        elem_args = [None for _ in range(len(self.elements))]
        for id_, arg in parameters.items():
            elem_args[self.elem_id_to_idx[id_]] = arg

        rendered_elements = []
        for (id_, elem), arg in zip(self.elements, elem_args):
            if arg is None:
                rendered_elements.append(elem.render())
            else:
                rendered_elements.append(elem.render(arg))

        return super()._render(rendered_elements=rendered_elements)

class BonusTask(HumanIO):
    def __init__(self, mturk_client,
        title: str,
        reward: str,
        description: str,
        duration: int,
        lifetime: int,
        worker_ids: List[str],
        #
        keywords: str='',
        auto_approval_delay: int=600,# 10 minutes
        max_heartbeat: int=600,# 10 minutes
    ):
        elements = [('message', IText()), ('feedback', OText(id_='feedback'))]
        run_once = None
        cache_path = None
        self.worker_ids = worker_ids

        id_ = str(uuid.uuid4())
        qual = Unique(mturk_client, id_, comparator='e', description='Worker Bonus Qual')
        response = qual.get()
        for worker_id in self.worker_ids:
            mturk_client.associate_qualification_with_worker(
                QualificationTypeId=response['QualificationTypeId'],
                WorkerId=worker_id,
                SendNotification=False
            )
        qualifications = [qual]

        super().__init__(mturk_client, elements, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat, qualifications=qualifications, run_once=run_once, cache_path=cache_path)

    def _render(self, message):
        return super()._render(parameters={'message': {'text': message}})


class TextClassification(Task):
    """
    Text classification HIT.
    """
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
        qualifications: List[object]=[],
        run_once=None,
        cache_path=None,
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
        super().__init__(mturk_client, schema, title, reward, description, duration, lifetime, keywords, auto_approval_delay, max_heartbeat, qualifications=qualifications, run_once=run_once, cache_path=cache_path)

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
