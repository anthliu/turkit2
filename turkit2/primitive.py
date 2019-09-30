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
    ):
        '''
        TODO add qualifications
        TODO add documentation
        '''
        self.mturk_client = mturk_client
        self.schema_template = schema_template
        with (Path(__file__).parent / 'schemas' / 'html_question.xml').open() as f:
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

    def _render(self, **schema_args):
        html_content = self.schema_template.render(**schema_args)
        #xml_question = self.question_schema.render(html_content=escape(html_content))
        xml_question = self.question_schema.render(html_content=html_content.replace('&', '&amp;'))
        return xml_question

    def _parse(self, answer):
        resource = xmlschema.XMLResource(answer)
        return self.answer_schema.to_dict(resource)

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

    def ask(self, assignments=1, verbosity=0, **schema_args):
        yield from asyncio.run(self.ask_async(assignments, verbosity, **schema_args))

    async def ask_async(self, assignments=1, verbosity=0, **schema_args):
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
