#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yan Xinxin'

'''
JSON API definition.
'''

import json, logging, inspect, functools

class Page(object):
    '''
    Page object for display pages.
    '''

    def __init__(self, items, currentPage=1, itemsOnPage=10):
        self.items = items
        self.displayedPages = 5
        self.edges = 3
        self.itemsOnPage = itemsOnPage
        self.pages = items // itemsOnPage + (1 if items % itemsOnPage > 0 else 0)
        if (items == 0) or (currentPage > self.pages):
            self.offset = 0
            self.limit = 0
            self.currentPage = 1
        else:
            self.currentPage = currentPage
            self.offset = self.itemsOnPage * (currentPage - 1)
            self.limit = self.itemsOnPage
        self.has_next = self.currentPage < self.pages
        self.next_num = self.currentPage + 1
        self.has_prev = self.currentPage > 1
        self.prev_num = self.currentPage - 1

class APIError(Exception):
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message

class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)

class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)

class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)

if __name__=='__main__':
    import doctest
    doctest.testmod()
