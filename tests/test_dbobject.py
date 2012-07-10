import tw2.core as twc, tw2.sqla as tws, sqlalchemy as sa, tw2.forms as twf
import testapi


class BaseObject(object):
    """ Contains all tests to be run over Elixir and sqlalchemy-declarative """
    def setUp(self):
        raise NotImplementedError, "Must be subclassed."

    def test_twsconfig(self):
        config = self.DbTestCls1._tws_config
        assert(len(config) == 1)
        assert(config['name'].editable == False)
        assert(config['name'].viewable == True)

    def test_inheritance(self):
        config = self.DbTestCls2._tws_config
        assert(len(config) == 2)
        assert(config['name'].editable == False)
        assert(config['name'].viewable == False)
        assert(config['surname'].editable == True)
        assert(config['surname'].viewable == False)

    def test_widget_and_validator(self):
        config = self.DbTestCls3._tws_config
        assert(len(config) == 3)
        assert(config['pwd'].widget_cls == twf.PasswordField)
        assert(config['pwd'].validator_cls == None)
        assert(config['emailaddress'].widget_cls == None)
        assert(config['emailaddress'].validator_cls == twc.EmailValidator)

    def test_automatic_id(self):
        assert(type(self.DbTestCls3.id) == property)
        obj = self.DbTestCls3.query.first()
        assert(obj.id == 1)
        assert(obj.iduser == obj.id)
        assert(type(self.DbTestCls1.id) != property)
        assert(type(self.DbTestCls2.id) != property)

class TestElixir(BaseObject):
    def setUp(self):
        import elixir as el
        import transaction
        el.metadata = sa.MetaData('sqlite:///:memory:')

        class Entity(el.EntityBase):
            __metaclass__ = tws.ElixirEntityMeta

        class DbTestCls1(Entity):
            el.using_options(inheritance='multi', tablename='test1')
            id = el.Field(el.Integer, primary_key=True)
            name = tws.TwsConfig(
                        el.Field(el.String),
                        viewable=True,
                        editable=False,
                    )
        class DbTestCls2(DbTestCls1):
            el.using_options(inheritance='multi', tablename='test2')
            id = el.Field(el.Integer, sa.ForeignKey('test1.id'), primary_key=True)
            name = tws.TwsConfig(
                    viewable=False,
                    editable=False,
                    )
            surname = tws.TwsConfig(
                        el.Field(el.String),
                        viewable=False,
                        editable=True,
                    )
        class DbTestCls3(Entity):
            iduser = el.Field(el.Integer, primary_key=True)
            name = tws.TwsConfig(
                        el.Field(el.String),
                        viewable=True,
                        editable=False,
                    )
            pwd = tws.TwsConfig(
                        el.Field(el.String),
                        widget_cls=twf.PasswordField
                        )
            emailaddress = tws.TwsConfig(
                        el.Field(el.String),
                        validator_cls=twc.EmailValidator
                        )
        
        self.DbTestCls1 = DbTestCls1
        self.DbTestCls2 = DbTestCls2
        self.DbTestCls3 = DbTestCls3
    
        el.setup_all()
        el.metadata.create_all()

        self.DbTestCls3(iduser=1, name="Bob")
        transaction.commit()
        testapi.setup()


class TestSQLA(BaseObject):
    def setUp(self):
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base(metadata=sa.MetaData('sqlite:///:memory:'), metaclass=tws.SqlaDeclarativeMeta)
        Base.query = tws.transactional_session().query_property()

        class DbTestCls1(Base):
            __tablename__ = 'Test'
            id = sa.Column(sa.Integer, primary_key=True)
            name = tws.TwsConfig(
                        sa.Column(sa.String(50)),
                        viewable=True,
                        editable=False,
                    )

        class DbTestCls2(DbTestCls1):
            __tablename__ = 'Test2'
            id = sa.Column(sa.Integer, sa.ForeignKey('Test.id'), primary_key=True)
            name = tws.TwsConfig(
                    viewable=False,
                    editable=False,
                    )
            surname = tws.TwsConfig(
                        sa.Column(sa.String(50)),
                        viewable=False,
                        editable=True,
                    )

        class DbTestCls3(Base):
            __tablename__ = 'Test3'
            iduser = sa.Column(sa.Integer, primary_key=True)
            name = tws.TwsConfig(
                        sa.Column(sa.String(50)),
                        viewable=True,
                        editable=False,
                    )
            pwd = tws.TwsConfig(
                        sa.Column(sa.String(50)),
                        widget_cls=twf.PasswordField
                    )
            emailaddress = tws.TwsConfig(
                        sa.Column(sa.String(50)),
                        validator_cls=twc.EmailValidator
                        )

        self.DbTestCls1 = DbTestCls1
        self.DbTestCls2 = DbTestCls2
        self.DbTestCls3 = DbTestCls3
    
        Base.metadata.create_all()

        session = sa.orm.sessionmaker()()
        self.session = session
        session.add(self.DbTestCls3(iduser=1, name='Bob'))
        session.commit()

        testapi.setup()
