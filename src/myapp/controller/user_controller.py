#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' blog controller '''

__author__ = 'Yan Xinxin'

import logging,hashlib,time,json,re
from flask import Blueprint, render_template, make_response,request,jsonify
from myapp.models.models import User,next_id,AlchemyEncoder
from myapp.framework_base.apis import Page,APIValueError,APIError
from myapp.framework_base.orm import SessionFactory
from conf.config import configs, toDict
from sqlalchemy import desc

user_blue = Blueprint('user_blue', __name__)
COOKIE_NAME = 'cfunsession'
_COOKIE_KEY = configs.session.secret

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        session = SessionFactory()
        user = session.query(User).filter(User.id==uid).one()
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.'''    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

@user_blue.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@user_blue.route('/signin', methods=['GET'])
def signin():
    return render_template('signin.html')

@user_blue.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = toDict(json.loads(request.get_data(as_text=True)))

    if not data.email:
        raise APIValueError('email', 'Invalid email.')
    if not data.passwd:
        raise APIValueError('passwd', 'Invalid password.')
    session = SessionFactory()
    users = session.query(User).filter(User.email==data.email).all()
    session.close()
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(data.passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    cookie = user2cookie(user, 86400)
    user.passwd = '******'
    r = make_response(json.dumps(user, cls=AlchemyEncoder))
    r.set_cookie(COOKIE_NAME, cookie, max_age=86400, httponly=True)
    r.content_type = 'application/json'
    return r

@user_blue.route('/signout', methods=['GET'])
def signout():
    r = make_response(render_template('signin.html'))
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@user_blue.route('/manage/users', methods=['GET'])
def manage_users(*, page='1'):
    return render_template('manage_users.html',page_index=get_page_index(page), __user__=request.__user__)

@user_blue.route('/api/users', methods=['GET'])
def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    session = SessionFactory()
    num = session.query(User).count()
    session.close()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p.__dict__, users=())
    session = SessionFactory()
    users = session.query(User).order_by(desc('created_at')).offset(p.offset).limit(p.limit).all()
    session.close()
    for u in users:
        u.passwd = '******'
    r = make_response(json.dumps(dict(page=p.__dict__, users=users), cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@user_blue.route('/api/users', methods=['POST'])
def api_register_user():
    data = toDict(json.loads(request.get_data(as_text=True)))

    if not data.name or not data.name.strip():
        raise APIValueError('name')
    if not data.email or not _RE_EMAIL.match(data.email):
        raise APIValueError('email')
    if not data.passwd or not _RE_SHA1.match(data.passwd):
        raise APIValueError('passwd')
    session = SessionFactory()
    users = session.query(User).filter(User.email==data.email).all()
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, data.passwd)
    user = User(id=uid, name=data.name.strip(), email=data.email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(data.email.encode('utf-8')).hexdigest())
    session.add(user)
    session.commit()
    session.close()
    # make session cookie:
    cookie = user2cookie(user, 86400)
    user.passwd = '******'
    r = make_response(json.dumps(user, cls=AlchemyEncoder))
    r.set_cookie(COOKIE_NAME, cookie, max_age=86400, httponly=True)
    r.content_type = 'application/json'
    return r
