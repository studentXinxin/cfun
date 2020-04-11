#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask,request,redirect
import time,logging,json
from myapp.controller.blog_controller import blog_blue
from myapp.controller.user_controller import user_blue, COOKIE_NAME, cookie2user
from myapp.controller.comment_controller import comment_blue
from datetime import datetime

app = Flask(__name__)

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

@app.before_request
def auth():
    if request.path.startswith('/static/') or request.path.startswith('/templates/'):
        return None
    logging.info('check user: %s %s' % (request.method, request.path))
    request.__user__ = None
    cookie_str = request.cookies.get(COOKIE_NAME)
    if cookie_str:
        user = cookie2user(cookie_str)
        if user:
            logging.info('set current user: %s' % user.email)
            request.__user__ = user
    if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
        return redirect('/signin')
    return None

if __name__ == '__main__':
    app.debug = True
    app.register_blueprint(blog_blue)
    app.register_blueprint(user_blue)
    app.register_blueprint(comment_blue)
    app.add_template_filter(datetime_filter, 'datetime')
    app.run()
