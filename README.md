irrealis_orm
============

This is a tool to quickly setup SQLAlchemy object relation mappings that uses
reflection to autoload table information from existing databases.


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
ontology (see http://www.geneontology.org). There are, literally, more than a
hundred table definitions in the schema. This made for a great deal of
repetitive and utterly boring grunt work before I could start accessing and
using the data.

To save time (and peace of mind) I used SQLAlchemy's database introspection
tools to automatically load table definitions from the database. Unfortunately,
it is usually impossible to programattically infer SQL relationships describing
directed graphs, such as those used in Chado; at least, it's impossible by
simple database introspection, for a variety of reasons. Since this is
frequently futile, SQLAlchemy doesn't try to do it. So it must be done
manually. After doing it four or five times I wrote this tool to simplify the
workflow.

I then found myself using the tool whenever I wanted a Python ORM to a database
I didn't design myself.

How to run tests
================

To run tests, type "python -m irrealis_orm.tests".  If you have "nose" and
"coverage" installed, type "nosetests --with-coverage --cover-package=irrealis_orm".
