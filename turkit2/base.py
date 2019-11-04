import os
from typing import Optional
from pathlib import Path
import asyncio
#from xml.sax.saxutils import escape
import xmlschema
from jinja2 import Template

class Task(object):
    def __init__(self, mturk_client,
        schema_template : Template,
        title: str,
        reward: str,
        description: str,
        duration: int,
        lifetime: int,
        #
        keywords: str='',
        auto_approval_delay: int=7200,# 24 hours
        max_heartbeat: int=600,# 10 minutes
        run_once=None,
        cache_path=None,
        base_schema='html_question.xml'
    ):
        '''
        TODO add qualifications
        TODO add documentation
        TODO implement run once

        run_once: add ID to use (str)
        cache_path: path to cache results for run_once (default if None)
        '''
        self.mturk_client = mturk_client
        self.schema_template = schema_template
        with (Path(__file__).parent / 'schemas' / base_schema).open() as f:
            self.question_schema = Template(f.read())

        self.answer_schema = xmlschema.XMLSchema(str(Path(__file__).parent / 'schemas' / 'QuestionFormAnswers.xsd'))

        self.title = title
        self.reward = reward
        self.description = description
        self.keywords = keywords
        self.duration = duration
        self.auto_approval_delay = auto_approval_delay
        self.lifetime = lifetime
        self.max_heartbeat = max_heartbeat

        if run_once is not None:
            self.run_id = run_once
            if cache_path is None:
                base_path = Path.cwd() / '.turkit_cache'
            else:
                base_path = Path(cache_path)

            if not base_path.exists():
                os.mkdir(str(base_path))

            self.cache_path = base_path / f'{self.run_id}.yaml'

    def _get_cache(self):
        if not self.cache_path.exists():
            return dict()
        with self.cache_path.open('r') as f:
            return yaml.load(f, Loader=yaml.BaseLoader)

    def _write_cache(self):
        '''
        TODO fix
        '''
        data = {
        }

        with self.cache_path.open('w') as f:
            yaml.dump(f, data)

    def _render(self, **schema_args):
        html_content = self.schema_template.render(**schema_args)
        #xml_question = self.question_schema.render(html_content=escape(html_content))
        xml_question = self.question_schema.render(html_content=html_content.replace('&', '&amp;'))
        return xml_question

    def _parse(self, answer):
        resource = xmlschema.XMLResource(answer)
        parsed = self.answer_schema.to_dict(resource)
        assert 'Answer' in parsed
        assert isinstance(parsed['Answer'], list)
        result = {}
        for qanda in parsed['Answer']:
            assert 'QuestionIdentifier' in qanda
            if 'FreeText' in qanda:
                answer = qanda['FreeText']
            else:
                answer = dict(qanda)
                del answer['QuestionIdentifier']# remove dupe info
            result[qanda['QuestionIdentifier']] = answer
        return result

    def _create_hit(self, assignments, xml_question):
        response = self.mturk_client.create_hit(
            MaxAssignments=assignments,
            Title=self.title,
            Description=self.title,
            Keywords=self.keywords,
            Reward=self.reward,
            LifetimeInSeconds=self.lifetime,
            AssignmentDurationInSeconds=self.duration,
            AutoApprovalDelayInSeconds=self.auto_approval_delay,
            Question=xml_question
        )
        return response

    def _get_assignments(self, hitid):
        '''
        TODO pagination
        '''
        response = self.mturk_client.list_assignments_for_hit(
            HITId=hitid,
            #AssignmentStatuses=['Submitted']
        )
        return response['Assignments']

    def preview(self, **schema_args):
        assert "sandbox" in str(self.mturk_client._endpoint), "Need to preview in sandbox! (Use sandbox endpoint)"
        xml_question = self._render(**schema_args)
        response = self._create_hit(1, xml_question)
        return "https://workersandbox.mturk.com/mturk/preview?groupId=" + response['HIT']['HITGroupId']

    def ask(self, assignments: int=1, verbosity: int=0, **schema_args):
        yield from asyncio.run(self.ask_async(assignments, verbosity, **schema_args))

    async def ask_async(self, assignments: int=1, verbosity: int=0, **schema_args):
        xml_question = self._render(**schema_args)

        response = self._create_hit(assignments, xml_question)

        if verbosity >= 1:
            print("https://worker.mturk.com/mturk/preview?groupId=" + response['HIT']['HITGroupId'])
            print("https://workersandbox.mturk.com/mturk/preview?groupId=" + response['HIT']['HITGroupId'])

        heartbeat = 30
        cache = {}
        while len(cache) < assignments:
            await asyncio.sleep(heartbeat)
            new_assignment = False
            assignment_dicts = self._get_assignments(response['HIT']['HITId'])
            for assignment in assignment_dicts:
                if assignment['AssignmentId'] not in cache:
                    if verbosity >= 3:
                        print('New assignment found.')
                    cache[assignment['AssignmentId']] = assignment
                    answer = self._parse(assignment['Answer'])
                    new_assignment = True
                    yield answer, assignment

            if not new_assignment:
                heartbeat = min(self.max_heartbeat, 2 * heartbeat)
                if verbosity >= 3:
                    print(f'No new assignments found, increasing timeout to {heartbeat}')
