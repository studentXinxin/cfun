#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Yan Xinxin'

import time, uuid, json, datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, Float, REAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

Base = declarative_base()

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:  # 添加了对datetime的处理
                    if isinstance(data, datetime.datetime):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.date):
                        fields[field] = data.isoformat()
                    elif isinstance(data, datetime.timedelta):
                        fields[field] = (datetime.datetime.min + data).time().isoformat()
                    else:
                        fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Base):
    __tablename__ = 'users'

    id = Column(String(50), primary_key=True, default=next_id)
    email = Column(String(50))
    passwd = Column(String(50))
    admin = Column(Boolean, default=False)
    name = Column(String(50))
    image = Column(String(500))
    created_at = Column(REAL, default=time.time)

class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(String(50), primary_key=True, default=next_id)
    user_id = Column(String(50))
    user_name = Column(String(50))
    user_image = Column(String(500))
    name = Column(String(50))
    summary = Column(String(200))
    content = Column(Text)
    created_at = Column(REAL, default=time.time)

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(String(50), primary_key=True, default=next_id)
    blog_id = Column(String(50))
    user_id = Column(String(50))
    user_name = Column(String(50))
    user_image = Column(String(500))
    content = Column(Text)
    created_at = Column(REAL, default=time.time)
