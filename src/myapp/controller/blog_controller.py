#!/usr/bin/env python3
# -*- coding: utf-8 -*-

''' blog controller '''

__author__ = 'Yan Xinxin'

import logging
from flask import Blueprint, render_template, request, json, make_response
from conf.config import toDict
from myapp.models.models import Blog,Comment,AlchemyEncoder
from myapp.framework_base.apis import Page,APIPermissionError,APIValueError
from myapp.framework_base.orm import SessionFactory
from myapp.framework_base import markdown2
from sqlalchemy import desc

blog_blue = Blueprint('blog_blue', __name__)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@blog_blue.route('/', methods=["GET"])
def index(*, page='1'):
    return render_template('blogs.html', page_index=get_page_index(page), __user__=request.__user__)


@blog_blue.route('/blog/<id>', methods=['GET'])
def get_blog(id):
    session = SessionFactory()
    blog = session.query(Blog).filter(Blog.id==id).one()
    comments = session.query(Comment).filter(Comment.blog_id==id).order_by(desc('created_at')).all()
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    session.close()
    return render_template('blog.html',blog=blog,comments=comments, __user__=request.__user__)


@blog_blue.route('/manage/blogs',methods=['GET'])
def manage_blogs(*, page='1'):
    return render_template('manage_blogs.html',page_index=get_page_index(page), __user__=request.__user__)


@blog_blue.route('/blogs/create',methods=['GET'])
def manage_create_blog():
    return render_template('blog_edit.html',id='',action='/api/blogs', __user__=request.__user__)


@blog_blue.route('/blogs/edit',methods=['GET'])
def manage_edit_blog():
    id = request.args.get("id")
    return render_template('blog_edit.html',id=id,action='/api/blogs/%s' % id, __user__=request.__user__)


@blog_blue.route('/api/blogs',methods=['GET'])
def api_blogs(*, page='1'):
    page = request.args.get('page')
    page_index = get_page_index(page)
    session = SessionFactory()
    num = session.query(Blog).count()
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p.__dict__, blogs=())
    blogs = session.query(Blog).order_by(desc('created_at')).offset(p.offset).limit(p.limit).all()
    session.close()
    r = make_response(json.dumps(dict(page=p.__dict__, blogs=blogs),cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@blog_blue.route('/api/blogs/<id>',methods=['GET'])
def api_get_blog(*, id):
    session = SessionFactory()
    blog = session.query(Blog).filter(Blog.id==id).one()
    session.close()
    r = make_response(json.dumps(blog, cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@blog_blue.route('/api/blogs', methods=['POST'])
def api_create_blog():
    check_admin(request)
    data = toDict(json.loads(request.get_data(as_text=True)))
    if not data.name or not data.name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not data.summary or not data.summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not data.content or not data.content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=data.name.strip(), summary=data.summary.strip(), content=data.content.strip())
    session = SessionFactory()
    session.add(blog)
    session.commit()
    session.close()
    r = make_response(json.dumps(blog, cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@blog_blue.route('/api/blogs/<id>',methods=['POST'])
def api_update_blog(id):
    check_admin(request)
    data = toDict(json.loads(request.get_data(as_text=True)))
    session = SessionFactory()
    blog = session.query(Blog).filter(Blog.id==id).one()
    if not data.name or not data.name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not data.summary or not data.summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not data.content or not data.content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog.name = data.name.strip()
    blog.summary = data.summary.strip()
    blog.content = data.content.strip()
    session.commit()
    session.close()
    r = make_response(json.dumps(blog, cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r


@blog_blue.route('/api/blogs/<string:id>/delete',methods=['POST'])
def api_delete_blog(id):
    check_admin(request)
    session = SessionFactory()
    blog = session.query(Blog).filter(Blog.id == id).one()
    session.delete(blog)
    session.commit()
    session.close()
    r = make_response(json.dumps(blog, cls=AlchemyEncoder))
    r.content_type = 'application/json'
    return r