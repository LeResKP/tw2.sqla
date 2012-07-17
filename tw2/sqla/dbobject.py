#!/usr/bin/python

from sqlalchemy.ext.declarative import DeclarativeMeta
from elixir.entity import EntityMeta
import sqlalchemy as sa
import widgets


class TwsConfig(object):
    """Use to define the properties of a fields

    Example:
        url = TwsConfig(
                Column(Text, nullable=True),
                editable=False,
                )
    """

    def __init__(self, 
            field=None, 
            viewable=True, 
            editable=True,
            widget_cls=None,
            validator_cls=None,
            tabname=None,
            ):
        self.__dict__.update(locals())


def generate_metaclass(classname, metaclass):
    """Generate a metaclass which will set the _tws_config on the class
    according to the TwsConfig objects.
    Also we add the id propery to make sure it's always defined.
    """
    def __new__(cls, classname, bases, dict_):
        conf_dict = {}

        for base in bases:
            cls_conf = getattr(base, '_tws_config', {})
            conf_dict.update(cls_conf)

        for key, value in dict_.items():
            if isinstance(value, TwsConfig):
                dict_[key] = value.field
                conf_dict[key] = value
        # Put the config in the class
        dict_['_tws_config'] = conf_dict
        return metaclass.__new__(cls, classname, bases, dict_)

    def get_id(obj):
        mapper = sa.orm.class_mapper(obj.__class__)
        if len(mapper.primary_key) == 1:
            # We should only have one primary key
            pkey = mapper.primary_key[0].key
            return getattr(obj, pkey)

    def __init__(cls, classname, bases, dict_):
        if 'id' not in cls.__dict__:
            # cls.id should be defined to make sure we can get the values of the foreign objects
            cls.id = property(get_id)
        return metaclass.__init__(cls, classname, bases, dict_)

    return type(classname, (metaclass,), {'__new__': __new__, '__init__': __init__})

SqlaDeclarativeMeta = generate_metaclass('SqlaDeclarativeMeta', DeclarativeMeta)
ElixirEntityMeta = generate_metaclass('ElixirEntityMeta', EntityMeta)

