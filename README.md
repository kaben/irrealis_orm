irrealis_orm
============

This is a tool to quickly setup SQLAlchemy object relation mappings (ORMs). It
uses SQLAlchemy's reflection tools to autoload table information from existing
databases. ORM instances are configured using a dictionary describing which
tables to map, what classes to map them to, and how they're related.


Demo usage
=========

I've placed a commented demo in the "TestManyToManySelf" test case defined in
"irrealis_orm/tests.py".


Motivation
==========

I have written bioinformatics tools to analyze data stored in Chado database
tables, but the number and complexity of table definitions in the Chado schema
is daunting to any programmer: the schema is highly normalized (see
http://gmod.org/wiki/Chado_Tables) and reflects the complexity of the gene
ontology (see http://www.geneontology.org). There are, literally, at least a
hundred table definitions in the schema. This made for a great deal of
repetitive and utterly boring grunt work before I could start accessing and
using the data.

To save time I used SQLAlchemy's database introspection tools to automatically
load table definitions from the database. Unfortunately, for a variety of
reasons it is usually impossible to use database introspection to infer SQL
relationships describing directed graphs, such as those used in Chado. Since
this is usually futile, SQLAlchemy doesn't try to do it. So it must be done
manually, and after doing it four or five times I wrote this tool to simplify
the workflow.

I then found myself using the tool whenever I wanted a Python ORM to a database
I didn't design myself.

How to run tests
================

To run tests, type "python -m irrealis_orm.tests".  If you have "nose" and
"coverage" installed, type "nosetests --with-coverage --cover-package=irrealis_orm".
