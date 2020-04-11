#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Default configurations.
'''

__author__ = 'Yan Xinxin'

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'db': 'cfun'
    },
    'db_pool':{
        'max_overflow': 0,  # 超过连接池大小外最多创建的连接
        'pool_size': 5,  # 连接池大小
        'pool_timeout': 30,  # 池中没有线程最多等待的时间，否则报错
        'pool_recycle': -1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
    },
    'session': {
        'secret': 'cfunChouChou'
    }
}
