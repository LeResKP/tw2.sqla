import sqlalchemy as sa

def from_dict(entity, data):
    """
    Update a mapped class with data from a JSON-style nested dict/list
    structure.  -- Copied straight from elixir.entity
    """
    # surrogate can be guessed from autoincrement/sequence but I guess
    # that's not 100% reliable, so we'll need an override

    mapper = sa.orm.object_mapper(entity)

    for key, value in data.iteritems():
        if isinstance(value, dict):
            dbvalue = getattr(entity, key)
            rel_class = mapper.get_property(key).mapper.class_
            pk_props = rel_class.__mapper__.primary_key

            if not [1 for p in pk_props if p.key in data] and \
               dbvalue is not None:
                from_dict(dbvalue, value)
            else:
                record = update_or_create(rel_class, value)
                setattr(entity, key, record)
        elif isinstance(value, list) and \
             value and isinstance(value[0], dict):

            rel_class = mapper.get_property(key).mapper.class_
            new_attr_value = []
            for row in value:
                if not isinstance(row, dict):
                    raise Exception(
                            'Cannot send mixed (dict/non dict) data '
                            'to list relationships in from_dict data.')
                record = update_or_create(rel_class, row)
                new_attr_value.append(record)
            setattr(entity, key, new_attr_value)
        else:
            setattr(entity, key, value)
    return entity

def update_or_create(cls, data, surrogate=True):
    pk_props = cls.__mapper__.primary_key

    # if all pk are present and not None
    if not [1 for p in pk_props if data.get(p.key) is None]:
        pk_tuple = tuple([data[prop.key] for prop in pk_props])
        record = cls.query.get(pk_tuple)
        if record is None:
            if surrogate:
                raise Exception("cannot create surrogate with pk")
            else:
                record = cls()
    else:
        if surrogate:
            record = cls()
        else:
            raise Exception("cannot create non surrogate without pk")
    from_dict(record, data)
    return record
