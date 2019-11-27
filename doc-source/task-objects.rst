############
Task Objects
############

Definitions
===========

(Note: read more about Amazon MTurk Concepts in https://docs.aws.amazon.com/AWSMechTurk/latest/RequesterUI/mechanical-turk-concepts.html)

- **HIT**: A HIT (Human Intelligence Task) is a self-contained task from the programmer (also referred to the requester) to a worker.
- **Assignment**: A HIT contains 1 or more assignments. Each worker can only work on 1 assignment of a HIT.
  Each assignment of a HIT is identical. These can be used to gain consensus on a task.
- **Task Object**: Task objects are the way Turkit2 encapsulates HITs in a python object.
  A programmer can create a HIT, give a HIT to workers, and retrieve worker answers from this object interface.

Using Task Objects
==================

Using a task object is two steps.

#. Initialize the task object. All task objects share many initialization parameters,
   parameters used to specify mturk parameters, such as HIT title, reward, discription,
   duration, and lifetime.
#. Post the task object using :code:`task.ask` (or :code:`task.ask_async`, the asynchronous version). Note this can be called *multiple times for the same task object!*
   This is useful for example in image classification, where the overall task is the same,
   but the underlying image changes. The programmer specifies the image being classified in :code:`task.ask`.

Each task object has *initialization parameters* (used to initialize the object),
and *ask parameters* (used to parameterize the :code:`task.ask` function).

Note: Task objects can also be previewed using the :code:`task.preview` method.


Types of Task Objects -- Use Cases
==================================

There are many different task objects, each designed to address a specific use case for turkit2.

In general, we identify 4 use cases, and list them in order implementation complexity (least complex to most complex).

#. **Common Task** - This task is very common, and there is a task object already made for this task (e.g. text classification). These are found in :ref:`common`. Using these will require no overhead in creating the task itself.
#. **Semi-Common Task** - This task is made of many common tasks. For example, a programmer may want to ask a crowdworker to label an image and explain their reasoning in text.
   These can be implemented using **HumanIO** tasks. HumanIO tasks are created by stacking *primitive* input output functionalities. How to use a HumanIO task is detailed in :ref:`HumanIO Tasks`.
#. **Complex Task** - This task has a complex interface (e.g. segmentation) that is cannot be implemented by the first 2 types.
   But, this type can be implemented in a static web page. Then, the programmer can program the interface in a template static webpage.
   The task object :code:`Task` object from the :ref:`base` module can be used and takes the template as a parameter.
   How to use and create these templates (schemas) is detailed in :ref:`Schemas`.
#. **Dynamic Task** - This task needs dynamic features of a full website. In this case, the programmer can run their website in a server, and use the :code:`External` task object from :ref:`common` by passing a URL of the website to the task object.

Basic Example
=============

We show a commented example of how to use a task object.

We first create our boto3 mturk client, which turkit2 uses to create our HIT.

.. code-block:: python

    # import boto3 to use aws python
    import boto3

    # TextClassification is one of the task objects commonly used, hence in the common module
    from turkit2.common import TextClassification

    # Create an MTurk sandbox instance
    # (aws credentials should be stored in ~/.aws, which is taken care of by awscli)
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    client = boto3.client(
        'mturk',
        region_name='us-east-1',
        endpoint_url = endpoint
    )

We now create our task object instance.
We specify many parameters that will be shown to workers so they can decide
whether to accept the task or not (title, reward, description),
how much time will be given for the task (duration, lifetime),
and how the actual task will look like (categories, question).

Full details for parameters are detailed in :ref:`common`.

.. code-block:: python

    # Create a TextClassification task object instance
    task = TextClassification(
        client,
        title='Classify tweet sentiment',
        reward='0.05',
        description='Classify the mood of a single Twitter tweet.',
        duration=600,# duration (sec) workers will have to complete the task once accepted
        lifetime=6000,# duration (sec) the HIT will be available to workers
        categories=['positive', 'negative'],
        question='Is the mood of this tweet positive or negative?'
    )

Finally, we post the task to mturk. Turkit2 takes care of worker answers.
:code:`task.ask_async` is an alternative way of gathering worker answers asynchronously using the python asyncio library.

.. code-block:: python

    # Post to mturk from the task object. Turkit2 manages worker answers, and returns an iterator of worker_answer, assignment_details pairs
    for worker_answer, assignment_details in task.ask(
        assignments=5,
        text='This movie is sad!'
    ):
        print(worker_answer)

Full example shown here.

.. code-block:: python

    # import boto3 to use aws python
    import boto3

    # TextClassification is one of the task objects commonly used, hence in the common module
    from turkit2.common import TextClassification

    # Create an MTurk sandbox instance
    # (aws credentials should be stored in ~/.aws, which is taken care of by awscli)
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    client = boto3.client(
        'mturk',
        region_name='us-east-1',
        endpoint_url = endpoint
    )

    # Create a TextClassification task object instance
    task = TextClassification(
        client,
        title='Classify tweet sentiment',
        reward='0.05',
        description='Classify the mood of a single Twitter tweet.',
        duration=600,# duration (sec) workers will have to complete the task once accepted
        lifetime=6000,# duration (sec) the HIT will be available to workers
        categories=['positive', 'negative'],
        question='Is the mood of this tweet positive or negative?'
    )

    # Post to mturk from the task object. Turkit2 manages worker answers, and returns an iterator of worker_answer, assignment_details pairs
    for worker_answer, assignment_details in task.ask(
        assignments=5,
        text='This movie is sad!'
    ):
        print(worker_answer)
