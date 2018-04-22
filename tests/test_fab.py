from pprint import pprint
from collections import OrderedDict
from wtforms_jsonschema2.fab import FABConverter
from unittest import TestCase
from wtforms.form import Form
from flask_appbuilder.fields import QuerySelectField
from flask_appbuilder import SQLA, AppBuilder
from flask import Flask
from flask_appbuilder import Model
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Gender(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return self.name


class FABTestForm(Form):
    _schema = OrderedDict([
        ('type', 'object'),
        ('properties', OrderedDict([
            ('gender', {
                'type': 'object',
                'title': 'Gender',
                'enum': [{'id': '1', 'label': 'Male'},
                         {'id': '2', 'label': 'Female'},
                         {'id': '3', 'label': 'Alien'},
                         {'id': '4', 'label': 'Other'}]
            })
        ]))
    ])
    gender = QuerySelectField('Gender',
                              query_func=lambda: [Gender(1, 'Male'),
                                                  Gender(2, 'Female'),
                                                  Gender(3, 'Alien'),
                                                  Gender(4, 'Other')],
                              get_pk_func=lambda x: x.id)


cfg = {'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
       'CSRF_ENABLED': False,
       'WTF_CSRF_ENABLED': False,
       'SECRET_KEY': 'bla'}

app = Flask('wtforms_jsonschema2_testing')
app.config.update(cfg)
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)


class PersonType(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        if self.name:
            return self.name
        else:
            return 'Person Type %s' % self.id


class Person(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    dt = Column(DateTime)
    person_type_id = Column(Integer, ForeignKey('person_type.id'),
                            nullable=False)
    person_type = relationship(PersonType, backref='people')

    def __repr__(self):
        return self.name


class Picture(Model):
    id = Column(Integer, primary_key=True)
    picture = Column(String, nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    person = relationship(Person, backref='pictures')

    def __repr__(self):
        return self.picture


class PictureView(ModelView):
    datamodel = SQLAInterface(Picture)
    add_columns = ['picture']
    _pretty_name = 'Picture'


class PersonView(ModelView):
    datamodel = SQLAInterface(Person)
    related_views = [PictureView]
    add_columns = ['name', 'dt', 'person_type', 'pictures']
    _pretty_name = 'Person'


class PersonTypeView(ModelView):
    datamodel = SQLAInterface(PersonType)
    related_views = [PersonView]


appbuilder.add_view(PersonView, 'people')
appbuilder.add_view(PersonTypeView, 'people types')
appbuilder.add_view(PictureView, 'pictures')

person_schema = OrderedDict([
    ('type', 'object'),
    ('definitions', OrderedDict([
        ('Person', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('name', {
                    'type': 'string',
                    'title': 'Name'
                }),
                ('dt', {
                    'type': 'string',
                    'format': 'date-time',
                    'title': 'Dt'
                }),
                ('person_type', {
                    'title': 'Person Type',
                    'type': 'object',
                    'enum': [{'id': '1', 'label': 'male'},
                             {'id': '2', 'label': 'Person Type 2'}]
                }),
                ('pictures', {
                    'type': 'array',
                    'title': 'Pictures',
                    'items': [
                        {'$ref': '#/defintions/Picture'}
                    ]
                })
            ])),
            ('required', ['name', 'person_type'])
        ])),
        ('Picture', OrderedDict([
            ('type', 'object'),
            ('properties', OrderedDict([
                ('picture', {'title': 'Picture', 'type': 'string'})
            ])),
            ('required', ['picture'])
        ]))
    ])),
    ('type', 'object'),
    ('properties', OrderedDict([
        ('Person', {'$ref': '#/definitions/Person'})
    ]))

])


class TestFABFormConvert(TestCase):
    def setUp(self):
        self.converter = FABConverter()
        self.maxDiff = None
        app.testing = True
        self.app = app.test_client()
        ctx = app.app_context()
        ctx.push()
        db.create_all()
        db.session.add(PersonType(name='male'))
        db.session.add(PersonType())
        db.session.commit()
        db.session.flush()

    def tearDown(self):
        db.drop_all()

    def test_full_view(self):
        schema = self.converter.convert(PersonView)
        pprint(schema)
        pprint(person_schema)
        self.assertEqual(schema, person_schema)

    def test_fab_form(self):
        schema = self.converter.convert(FABTestForm)
        pprint(schema)
        pprint(FABTestForm._schema)
        self.assertEqual(schema,
                         FABTestForm._schema)
