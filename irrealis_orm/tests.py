from irrealis_orm import ORM
from sqlalchemy import Table, Column, Integer, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm.exc import MultipleResultsFound

import unittest

class TestORM(unittest.TestCase):
    '''
    Unit tests of ORM core functionality.
    '''
    def setUp(self):
        '''
        Creates a test SQLAlchemy database engine with a simple in-memory
        SQLite database.
        '''
        self.metadata = MetaData()
        Table('users', self.metadata,
          Column('id', Integer, primary_key = True),
          Column('name', Text),
          Column('fullname', Text),
        )
        Table('addresses', self.metadata,
          Column('id', Integer, primary_key = True),
          Column('user_id', None, ForeignKey('users.id')),
          Column('email', Text, nullable = False),
        )
        self.engine = create_engine('sqlite:///:memory:')
        self.metadata.create_all(self.engine)

        # The ORM definition assumes the database tables are defined, and when
        # the ORM is constructed most column information will be found by
        # inspecting the database.
        #
        # Relationships must still be stated explicitly -- probably because the
        # SQLAlchemy designers found relationships hard to infer in certain
        # cases (see the TestManyToManySelf case below for an example of this).
        self.orm_defs = dict(
          User = dict(
            __tablename__ = 'users',
            addresses = relationship("Address"),
          ),
          Address = dict(
            __tablename__ = 'addresses',
            user = relationship("User"),
          ),
        )
    
    def exercise_orm(self, orm):
        '''
        Tests a database-mapped ORM.
        '''
        user = orm.User(name = u"Name", fullname = u"Full Name")
        address = orm.Address(email = u"full.name@domain.com", user = user)
        orm.session.add_all([user, address])
        orm.session.commit()
        self.assertTrue(address in user.addresses)

    def test_orm(self):
        orm = ORM()
        orm.create_mapped_classes(self.orm_defs)
        orm.configure_with_engine(self.engine)
        self.exercise_orm(orm)

    def test_orm_with_defs(self):
        orm = ORM(self.orm_defs)
        orm.configure_with_engine(self.engine)
        self.exercise_orm(orm)

    def test_orm_with_defs_and_engine(self):
        orm = ORM(self.orm_defs, self.engine)
        self.exercise_orm(orm)

    def test_nonreflected_orm_with_defs_and_url(self):
        orm_defs = dict(
          User = dict(
            __tablename__ = 'users',
            id = Column('id', Integer, primary_key = True),
            name = Column('name', Text),
            fullname = Column('fullname', Text),
            addresses = relationship("Address"),
          ),
          Address = dict(
            __tablename__ = 'addresses',
            id = Column('id', Integer, primary_key = True),
            user_id = Column('user_id', None, ForeignKey('users.id')),
            email = Column('email', Text, nullable = False),
            user = relationship("User"),
          ),
        )
        orm = ORM(orm_defs, 'sqlite:///:memory:', deferred_reflection = False)
        self.exercise_orm(orm)


class TestManyToManySelf(unittest.TestCase):
    '''
    Demo setup and use of self-referential many-to-many relationship
    
    A self-referential many-to-many relationship is one of the more complicated
    things one might try to do when constructing relational mappings. Setup is
    similar, but less-complicated, for other kinds of relationships:
    - Many-to-many (non-self-referential)
    - Many-to-one or one-to-many (self-referential or non-self-referential)
    - One-to-one (self-referential or non-self-referential)

    Since their setup is similar, this demo should help you with all of the
    above situations.
    '''
    def test_demo_self_referential_many_to_many_relationship(self):
        # First, setup the database tables.
        metadata = MetaData()
        Table("things", metadata,
          Column("id", Integer, primary_key=True),
          Column("name", Text),
        )
        # An association table is needed for many-to-many relationships, but
        # isn't usually necessary for other kinds of relationships.
        Table("things_association", metadata,
          Column("id", Integer, primary_key=True),
          Column("parent_id", Integer, ForeignKey("things.id")),
          Column("child_id", Integer, ForeignKey("things.id")),
        )
        engine = create_engine('sqlite:///:memory:')
        metadata.create_all(engine)

        # Second, assuming the database tables are already setup for the
        # relationship, ask SQLAlchemy to autoload the tables; but we still
        # must tell SQLAlchemy separately how to construct the relationship for
        # the ORM.
        orm_defs = dict(
          Thing = dict(
            __tablename__ = "things",
            children = relationship(
              "Thing",
              secondary = "things_association",
              primaryjoin = "Thing.id==things_association.c.parent_id",
              secondaryjoin = "Thing.id==things_association.c.child_id",
              backref="parents",
            ),
          ),
        )
        orm = ORM(orm_defs, engine)

        # Now make and connect parents/children.
        parent1 = orm.Thing(name = u"Parent1")
        parent2 = orm.Thing(name = u"Parent2")
        child1 = orm.Thing(name = u"Child")
        child2 = orm.Thing(name = u"Child")
        # The result should be the same whether we append the child to a
        # parent's list of children, or append a parent to child's list of
        # parents.
        parent1.children.append(child1)
        parent2.children.append(child1)
        child2.parents.append(parent1)
        child2.parents.append(parent2)

        # Commit to the database.
        orm.session.add_all([parent1, parent2, child1, child2])
        orm.session.commit()

        # Verify relationships.
        self.assertTrue(child1 in parent1.children)
        self.assertTrue(child2 in parent1.children)
        self.assertTrue(child1 in parent2.children)
        self.assertTrue(child2 in parent2.children)
        self.assertTrue(parent1 in child1.parents)
        self.assertTrue(parent2 in child1.parents)
        self.assertTrue(parent1 in child2.parents)
        self.assertTrue(parent2 in child2.parents)


class TestGetOrCreateUniqueObject(unittest.TestCase):
    '''
    Tests and demonstrates ORM.get_or_create(self, mapped_class, **keyword_args).

    get_or_create(...) tries to retrieve and return a single object of type
    mapped_class, uniquely identified by **keyword_args. If no such object can
    be found, one will be created. If **keyword_args identify multiple objects,
    the exception sqlalchemy.orm.exc.MultipleResultsFound is raised.
    '''
    def setUp(self):
        orm_defs = dict(
          Thing = dict(
            __tablename__ = 'thing',
            id = Column('id', Integer, primary_key = True),
            name = Column('name', Text),
          ),
        )
        self.orm = ORM(orm_defs, 'sqlite:///:memory:', deferred_reflection = False)

    def test_create_unique(self):
        self.assertEqual(0, self.orm.session.query(self.orm.Thing).count())
        thing1 = self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")
        self.assertEqual(1, self.orm.session.query(self.orm.Thing).count())
        thing2 = self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")
        self.assertEqual(1, self.orm.session.query(self.orm.Thing).count())
        self.assertEqual(thing1, thing2)

    def test_error_on_nonunique(self):
        self.assertEqual(0, self.orm.session.query(self.orm.Thing).count())
        thing1 = self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")
        self.assertEqual(1, self.orm.session.query(self.orm.Thing).count())
        thing2 = self.orm.Thing(name="Rumplestiltskin")
        self.orm.session.add(thing2)
        self.orm.session.commit()
        with self.assertRaises(MultipleResultsFound):
          self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")


class TestUpdateObject(unittest.TestCase):
    '''
    Tests and demonstrates ORM.update_object(self, obj, **keyword_args).

    update_object(...) updates obj's attributes/values corresponding to
    **keyword_args. It checks each keyword to make sure the object has an
    attribute of the same name; if not, the exception AttributeError is raised.
    '''
    def setUp(self):
        orm_defs = dict(
          Thing = dict(
            __tablename__ = 'thing',
            id = Column('id', Integer, primary_key = True),
            name = Column('name', Text),
            attribute = Column('attribute', Text),
          ),
        )
        self.orm = ORM(orm_defs, 'sqlite:///:memory:', deferred_reflection = False)
        self.thing = self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")

    def test_update_object(self):
        self.orm.update_object(self.thing, attribute="Sneakiness")
        thing2 = self.orm.get_or_create(self.orm.Thing, name="Rumplestiltskin")
        self.assertEqual(thing2.attribute, "Sneakiness")
        
    def test_nonsense_update_raises(self):
        with self.assertRaises(AttributeError):
          self.orm.update_object(self.thing, tie_color="Blue")
        

class TestGetOrCreateAndUpdate(unittest.TestCase):
    '''
    Tests and demonstrates ORM.get_or_create_and_update(self, mapped_class, query_dict, update_dict).

    get_or_create_and_update(...) tries to retrieve or create a unique
    mapped_class object identified by attributes in query dict; then tries to
    update this object with attributes in update_dict; and if successful,
    returns the object.

    get_or_create_and_update(...) uses get_or_create(...) and
    update_object(...), which raise exceptions when query_dict identifies more
    than one object, or when invalid attributes are specified.
    '''
    def setUp(self):
        orm_defs = dict(
          Thing = dict(
            __tablename__ = 'thing',
            id = Column('id', Integer, primary_key = True),
            name = Column('name', Text),
            attribute = Column('attribute', Text),
          ),
        )
        self.orm = ORM(orm_defs, 'sqlite:///:memory:', deferred_reflection = False)

    def test_get_or_create_and_update(self):
        query_dict = dict(name="Rumplestiltskin")
        update_dict_1 = dict(attribute="Sneakiness")
        update_dict_2 = dict(attribute="Meanness")
        thing_1 = self.orm.get_or_create_and_update(self.orm.Thing, query_dict, update_dict_1)
        self.assertEqual(thing_1.attribute, "Sneakiness")
        thing_2 = self.orm.get_or_create_and_update(self.orm.Thing, query_dict, update_dict_2)
        self.assertEqual(thing_2.attribute, "Meanness")
        self.assertEqual(thing_1, thing_2)


class TestLoadUnmappedTables(unittest.TestCase):
    def test_unmapped_tables_loaded(self):
        metadata = MetaData()
        Table("things", metadata,
          Column("id", Integer, primary_key=True),
          Column("name", Text),
        )
        Table("more_things", metadata,
          Column("id", Integer, primary_key=True),
          Column("name", Text),
        )
        engine = create_engine('sqlite:///:memory:')
        metadata.create_all(engine)
        orm_defs = dict(
          Thing = dict(
            __tablename__ = "things",
          )
        )
        orm = ORM(orm_defs, engine)
        self.assertTrue(u"more_things" in orm.Base.metadata.tables)



if __name__ == "__main__": unittest.main()
