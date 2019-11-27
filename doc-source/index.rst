.. turkit2 documentation master file, created by
   sphinx-quickstart on Sun Nov 24 17:06:02 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to turkit2's documentation!
===================================

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

.. toctree::
   :maxdepth: 2
   :caption: Guide:

   installation
   task-objects
   humanio
   schemas

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   base
   common
   qualifications
   primitive

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
