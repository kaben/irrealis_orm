'''
Tool to quickly setup SQLAlchemy object relation mappings that uses reflection
to autoload table information from existing databases.
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection

class ORM(object):
    '''Sets up SQLAlchemy object relational mappings.'''

    def __mapped_class(self, name, Base, dct):
        '''
        Creates class of given name, inheriting from Base, with attributes
        defined in dct. Attaches class to this ORM instance as attributes with
        same name.
        '''
        setattr(self, name, type(name, (Base,), dct))

    def create_mapped_classes(self, orm_defs):
        '''
        Creates and maps the ORM classes specified in orm_defs.
        '''
        for name, dct in orm_defs.iteritems(): self.__mapped_class(name, self.Base, dct)

    def configure_with_engine(self, engine):
        '''
        Loads database table info from engine into ORM.
        '''
        # Configuration of subsequent database connections.
        self.engine = engine
        # Reflect info from the new database connection.
        if self.def_refl: self.Base.prepare(self.engine)
        else: self.Base.metadata.create_all(self.engine)
        # New sesison factory, this time bound to the new engine. Now any
        # sessions we make will also be bound to the engine.
        self.session_factory = sessionmaker(self.engine)

    def create_engine(self, url):
        '''
        Configures engine for database given by SQLAlchemy url, then loads
        database table info into ORM.
        '''
        # Configuration of subsequent database connections.
        self.configure_with_engine(create_engine(url))

    def __init__(self, orm_defs = None, engine = None, deferred_reflection = True):
        '''
        Creates and maps the ORM classes specified in orm_defs.  If SQLAlchemy
        database url/engine is given, loads database table info into ORM.
        
        Use as follows:
        >>> orm_defs = dict(
        ...    ThingClass1 = dict(__tablename__ = 'thing_1_table'),
        ...    ThingClass2 = dict(__tablename__ = 'thing_2_table'),
        ... )
        >>> url = "driver://user:password@host/database"

        Followed by:
        >>> orm = ORM(orm_defs, url)

        Or:
        >>> orm = ORM(orm_defs)
        >>> orm.create_engine(url)

        Or:
        >>> orm = ORM()
        >>> orm.create_mapped_classes(orm_defs)
        >>> orm.create_engine(url)

        Or:
        >>> engine = create_engine(url)
        >>> orm = ORM(orm_defs, engine)

        Or:
        >>> engine = create_engine(url)
        >>> orm = ORM(orm_defs)
        >>> orm.configure_with_engine(engine)

        Or:
        >>> engine = create_engine(url)
        >>> orm = ORM()
        >>> orm.create_mapped_classes(orm_defs)
        >>> orm.configure_with_engine(engine)

        Then:
        >>> session = orm.create_session()
        >>> thing_1 = orm.ThingClass1()
        >>> session.add(thing_1)
        >>> query = session.query(orm.Thing1)

        'thing_1_table' and 'thing_2_table' are example database table names,
        and 'ThingClass1' and 'ThingClass2' name example classes to create and
        map to the tables with SQLAlchemy reflection and declarative
        techniques. For more info, see
        - http://docs.sqlalchemy.org/en/rel_0_8/core/reflection.html
        - http://docs.sqlalchemy.org/en/rel_0_8/extensions/declarative.html
        or see test_orm() defined in this module.
        '''
        # Prep SQLAlchemy reflection with new SQLAlchemy declarative Base,
        # discarding any existing Base, engine, and session factory. Reflection
        # may be deferred if engine isn't specified.
        self.def_refl = deferred_reflection
        self.Base = declarative_base(cls=DeferredReflection if self.def_refl else object)
        # Create mapped classes if given.
        if orm_defs is None: orm_defs = dict() # Empty dict.
        self.create_mapped_classes(orm_defs)
        # Create or configure engine if given.
        if engine is not None:
          # "engine" can be either an SQLAlchemy url, or an SQLAlchemy engine.
          if type(engine) in (str, unicode): self.create_engine(engine)
          else: self.configure_with_engine(engine)
        # Convenience monkeypatch for displaying ORM objects.
        def monkey_repr(self):
            attr_dict = self.__dict__.copy()
            attr_dict.pop("_sa_instance_state", None)
            return "<{name}: {attr_dict}>".format(name=self.__class__.__name__, attr_dict=attr_dict)
        self.Base.__repr__ = monkey_repr

    def create_session(self):
        '''Creates and returns an SQLAlchemy database session for this ORM.'''
        return self.session_factory()

    @property
    def session(self):
        '''Convenient access to per-ORM session.'''
        if not hasattr(self, "_session"): self._session = self.create_session()
        return self._session

