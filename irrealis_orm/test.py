from irrealis_orm import ORM
from sqlalchemy import Table, Column, Integer, Text, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relationship
import unittest

class TestORM(unittest.TestCase):
    def setUp(self):
        '''
        Creates a test SQLAlchemy database engine with a simple in-memory
        SQLite database.
        '''
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
    
    def exercise_orm(self, orm):
        '''
        Tests a database-mapped ORM.
        '''
        user = orm.User(name = u"Name", fullname = u"Full Name")
        address = orm.Address(email = u"full.name@domain.com", user = user)
        session = orm.create_session()
        session.add_all([user, address])
        session.commit()
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

if __name__ == "__main__": unittest.main()
