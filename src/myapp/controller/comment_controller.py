#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' blog controller '''

__author__ = 'Yan Xinxin'

import logging,hashlib,time,json,re
from flask import Blueprint, render_template, make_response, redirect, request
from myapp.models.models import Blog,Comment,User,next_id,AlchemyEncoder
from myapp.framework_base.apis import Page,APIPermissionError,APIValueError,APIError,APIResourceNotFoundError
from myapp.framework_base.orm import SessionFactory
from conf.config import configs, toDict
from myapp.framework_base import markdown2
from sqlalchemy import desc

comment_blue = Blueprint('comment_blue', __name__)

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

@comment_blue.route('/manage/', methods=['GET'])
def manage():
    return redirect('/manage/comments')

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

@comment_blue.route('/manage/comments', methods=['GET'])
def manage_comments(*, page='1'):
    return render_template('manage_comments.html',page_index=get_page_index(page), __user__=request.__user__)

@comment_blue.route('/api/comments', methods=['GET'])
def api_comments(*, page='1'):
    page_index = get_page_index(page)
    session = SessionFactory()
    num = session.query(Comment).count()
    session.close()
    p = Page(num, page_index)
    if num == 0:
        r = make_response(json.dumps(dict(page=p.__dict__, comments=[]), cls=AlchemyEncoder))
        r.content_type = 'application/json'
        return r
    session = SessionFactory()
    comments = session.query(Comment).order_by(desc('created_at')).offset(p.offset).limit(p.limit).all()
    session.close()
    r = make_response(json.dumps(dict(page=p.__dict__, comments=comments), cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@comment_blue.route('/api/blogs/<id>/comments', methods=['POST'])
def api_create_comment(id):
    data = toDict(json.loads(request.get_data(as_text=True)))
    if not data.content or not data.content.strip():
        raise APIValueError('content')
    user = request.__user__
    session = SessionFactory()
    blog = session.query(Blog).filter(Blog.id==id).one()
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=data.content.strip())
    session.add(comment)
    session.commit()
    session.close()
    r = make_response(json.dumps(comment, cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@comment_blue.route('/api/comments/<id>/delete', methods=['POST'])
def api_delete_comments(id, request):
    check_admin(request)
    session = SessionFactory()
    c = session.query(Comment).filter(Comment.id == id).one()
    if c is None:
        raise APIResourceNotFoundError('Comment')
    session.delete(c)
    session.commit()
    session.close()
    r = make_response(json.dumps(dict(id=id)))
    r.content_type = 'application/json'
    return r

