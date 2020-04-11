#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yan Xinxin'

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from conf.config import configs

engine = create_engine(
    "mysql+pymysql://%s:%s@%s:%d/%s?charset=utf8" % (configs.db.user, configs.db.password, configs.db.host, configs.db.port, configs.db.db),
    max_overflow=configs.db_pool.max_overflow,  # 超过连接池大小外最多创建的连接
    pool_size=configs.db_pool.pool_size,  # 连接池大小
    pool_timeout=configs.db_pool.pool_timeout,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=configs.db_pool.pool_recycle  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)

SessionFactory = sessionmaker(bind=engine,expire_on_commit=False)

# def select(sql, args, size=None):
#     log(sql, args)
#     session = SessionFactory()
#     cur = session.execute(sql.replace('?', '%s'), args or ())
#     if size:
#         rs = cur.fetchmany(size)
#     else:
#         rs = cur.fetchall()
#     cur.close()
#     session.close()
#     logging.info('rows returned: %s' % len(rs))
#     return rs
