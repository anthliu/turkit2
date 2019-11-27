#######
Turkit2
#######

**Currently in development**

*Human computation* is the concept of treating human work as a *unit of algorithmic computation*.
Amazon’s Mechanical Turk (MTurk) is a platform that can enable human computation --
a programmer can hire anonymous workers to perform tasks, such as (image or text) labeling, tagging, and segmentation.

**Turkit2** is a Python library that aims to make human computation easier.
Turkit2 allows a programmer to easily
create (or reuse existing) static webpage templates that allow workers to do work,
recruit workers, and retrieve the work done by workers.

A typical workflow is as follows.

#. A programmer wants to embed human work into their program, e.g.human-in-the-loop methodologies such as active learning, or crowd workflows such as Soylent.
#. The programmer designs an interface for a human in their program.
#. The programmer builds **task object** for their interface. Read more about :ref:`Task Objects`.
#. The programmer uses their task object in their program.

Turkit2 is built on top of the low level AWS API boto3, and uses Jinja2 for its templating mechanism.

Installation
------------

#. Navigate to a directory you want to save the library code. (command line)
   
   .. code-block:: bash
      
      git clone https://github.com/anthliu/turkit2.git
      cd turkit2
      pip install -r requirements.txt
      pip install -e .
#. Install the aws cli to use your AWS keys with boto3.
   https://docs.aws.amazon.com/cli/latest/userguide/install-cliv1.html
#. Run :code:`aws configure`
   
   For region: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html
   
   Output format: None is fine (just press enter).
#. Check to make sure your installation works. Navigate to a working directory

   .. code-block:: bash
      
      wget https://raw.githubusercontent.com/anthliu/turkit2/master/tests/installation_test.py
      python installation_test.py
   
   This should open a tab in your browser to a sandbox mturk task that was created in the test script.


Documentation
-------------

https://turkit2.readthedocs.io/en/latest/
