import os
import json
import uuid
from app import models
from io import BytesIO
from django.urls import reverse
from app.utils.pagination import Pagination
from django.shortcuts import render
from django.shortcuts import redirect
from django import forms as django_forms
from django.shortcuts import HttpResponse
from django.db.utils import IntegrityError
from django.forms import fields as django_fields
from app.utils.check_code import create_validate_code
from django.core.exceptions import ValidationError


def check_login(func):
    """
    验证登录状态装饰器
    :param func:
    :return:
    """

    def inner(request, *args, **kwargs):
        if request.session.get('user_info'):
            return func(request, *args, **kwargs)
        else:
            return redirect('/login.html')

    return inner


class BaseForm(object):
    """
    Form基类
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(BaseForm, self).__init__(*args, **kwargs)


class LoginForm(BaseForm, django_forms.Form):
    """
    验证登录的Form
    """
    username = django_fields.CharField(
        min_length=6,
        max_length=20,
        error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符",
                        'max_length': "用户名长度不能大于32个字符"}
    )
    password = django_fields.CharField(
        min_length=6,
        max_length=32,
        error_messages={'required': '密码不能为空.',
                        'min_length': "密码长度不能小于6个字符",
                        'max_length': "密码长度不能大于32个字符"}
    )
    rmb = django_fields.IntegerField(required=False)

    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')


class RegisterForm(BaseForm, django_forms.Form):
    """
    验证注册的Form
    """
    username = django_fields.CharField(
        min_length=6,
        max_length=20,
        error_messages={'required': '用户名不能为空.', 'min_length': "用户名长度不能小于6个字符",
                        'max_length': "用户名长度不能大于32个字符"}
    )
    password = django_fields.CharField(
        min_length=6,
        max_length=32,
        error_messages={'required': '密码不能为空.',
                        'min_length': "密码长度不能小于6个字符",
                        'max_length': "密码长度不能大于32个字符"}
    )
    confirm_password = django_fields.CharField(
        min_length=6,
        max_length=32,
        error_messages={'required': '密码不能为空.',
                        'min_length': "密码长度不能小于6个字符",
                        'max_length': "密码长度不能大于32个字符"}
    )
    qq = django_fields.IntegerField()
    check_code = django_fields.CharField(
        error_messages={'required': '验证码不能为空.'}
    )

    def clean_check_code(self):
        if self.request.session.get('CheckCode').upper() != self.request.POST.get('check_code').upper():
            raise ValidationError(message='验证码错误', code='invalid')


# Create your views here.
def index(request, *args, **kwargs):
    """
    首页
    展示所有
    :param request:
    :return:
    """
    article_type_list = models.Article.type_choices
    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        base_url = reverse('index', kwargs=kwargs)
    else:
        article_type_id = None
        base_url = '/'
    data_count = models.Article.objects.filter(**kwargs).count()
    page_obj = Pagination(request.GET.get('p'), data_count)
    article_list = models.Article.objects.filter(**kwargs).order_by('-nid')[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)
    article_nid_list = models.Article.objects.values_list('nid')
    top_read = []
    count = 0
    for i in article_nid_list:
        count += 1
        if count <= 10:
            article_obj = models.Article.objects.filter(nid=i[0])
            read_count = article_obj.values('read_count').first().get('read_count')
            top_read.append({'nid': article_obj.values('nid').first().get('nid'), 'read_count': read_count,
                             'title': article_obj.values('title').first().get('title'),
                             'article_type_id': article_obj.values('article_type_id').first().get('article_type_id'),
                             'author_name': article_obj.values('author__username').first().get('author__username')})
            top_read.sort(key=lambda obj: obj.get('read_count'), reverse=True)
    return render(
        request,
        'home.html',
        {
            'article_list': article_list,
            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'page_str': page_str,
            'top_read': top_read,
        }
    )


def detail(request, article_type_id, author_name, nid):
    """
    文章详情
    :param request:
    :param article_type_id:
    :param author_name:
    :param nid:
    :return:
    """
    content_title = models.Article.objects.filter(nid=nid).values('title').first().get('title')
    content = models.ArticleDetail.objects.filter(article_id=nid).values('content').first().get('content')
    qq = models.UserInfo.objects.filter(username=author_name).values('qq').first().get('qq')
    article = models.Article.objects.filter(nid=nid).first()
    comment_list = models.Comment.objects.filter(article=article)
    reply_list = models.Reply.objects.filter(article_id=nid)
    if request.method == "GET":
        new_read_count = int(models.Article.objects.filter(nid=nid).values('read_count').first().get('read_count')) + 1
        models.Article.objects.filter(nid=nid).update(read_count=str(new_read_count))
    return render(request, 'article_detail.html', {'content_title': content_title,
                                                   'content': content,
                                                   'author_name': author_name,
                                                   'comment_list': comment_list,
                                                   'qq': qq,
                                                   'nid': nid,
                                                   'article': article,
                                                   'reply_list': reply_list})


def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        result = {'status': False, 'message': None, 'data': None}
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user_info = models.UserInfo.objects. \
                filter(username=username, password=password). \
                values('nid', 'username').first()
            if not user_info:
                result['message'] = '用户名或密码错误'
            else:
                result['status'] = True
                request.session['user_info'] = user_info
                if form.cleaned_data.get('rmb'):
                    request.session.set_expiry(60 * 60 * 24 * 7)
        else:
            if 'check_code' in form.errors:
                result['message'] = '验证码错误或者过期'
            else:
                result['message'] = '用户名或密码错误'
        return HttpResponse(json.dumps(result))


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.set_expiry = 1
    request.session.clear()
    return redirect('/')


def check_code(request):
    """
    自动生成验证码，用到Python的PIL模块
    :param request:
    :return:
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, 'PNG')
    request.session['CheckCode'] = code
    return HttpResponse(stream.getvalue())


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        result = {'status': False, 'message': None, 'data': None}
        form = RegisterForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            qq = form.cleaned_data.get('qq')
            if password != confirm_password:
                result['message'] = '两次输入的密码不一致'
            else:
                try:
                    models.UserInfo.objects.create(
                        username=username,
                        password=password,
                        qq=qq
                    )
                except IntegrityError:
                    result['message'] = '用户名已被注册'
                else:
                    result['status'] = True
        else:
            if 'check_code' in form.errors:
                result['message'] = "验证码错误或过期"
            elif 'username' in form.errors:
                result['message'] = "用户名格式错误，至少6位"
            elif 'password' in form.errors or 'confirm_password' in form.errors:
                result['message'] = "密码格式错误，至少6位"
            else:
                result['message'] = "QQ格式错误"
        return HttpResponse(json.dumps(result))


@check_login
def write(request, author_name):
    """
    写文章
    :param request:
    :return:
    """
    if request.method == "GET":
        return render(request, 'write_article.html', {'author_name': author_name})
    elif request.method == "POST":
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        article_type_id = request.POST.get('article_type')
        author_id = models.UserInfo.objects.filter(username=author_name).values('nid').first().get('nid')
        obj = models.Article.objects.create(title=title, summary=summary, article_type_id=article_type_id,
                                            author_id=author_id)
        models.ArticleDetail.objects.create(content=content, article=obj)
        new_article_count = int(
            models.UserInfo.objects.filter(nid=author_id).values('article_count').first().get('article_count')) + 1
        models.UserInfo.objects.filter(nid=author_id).update(article_count=str(new_article_count))
        return redirect('/')


@check_login
def edit(request, author_name, article_id):
    """
    修改文章
    :param request:
    :param author_name:
    :param article_id:
    :return:
    """
    if request.method == "GET":
        title = models.Article.objects.filter(nid=article_id).values('title').first().get('title')
        summary = models.Article.objects.filter(nid=article_id).values('summary').first().get('summary')
        article_type_id = int(
            models.Article.objects.filter(nid=article_id).values('article_type_id').first().get('article_type_id'))
        content = models.ArticleDetail.objects.filter(article_id=article_id).values('content').first().get('content')
        return render(request, 'edit_article.html', {'author_name': author_name,
                                                     'title': title,
                                                     'summary': summary,
                                                     'article_type_id': article_type_id,
                                                     'content': content,
                                                     'article_id': article_id})
    elif request.method == "POST":
        title = request.POST.get('title')
        summary = request.POST.get('summary')
        content = request.POST.get('content')
        article_type_id = request.POST.get('article_type')
        obj = models.Article.objects.filter(nid=article_id).first()
        models.Article.objects.filter(nid=obj.nid).update(title=title, summary=summary, article_type_id=article_type_id)
        models.ArticleDetail.objects.filter(article=obj).update(content=content)
        return redirect('/')


@check_login
def delete(request, article_id):
    """
    删除文章
    :param request:
    :param article_id:
    :return:
    """
    obj = models.Article.objects.filter(nid=article_id).first()
    models.ArticleDetail.objects.filter(article=obj).delete()
    models.Article.objects.filter(nid=obj.nid).delete()
    new_article_count = int(
        models.UserInfo.objects.filter(nid=request.session['user_info']['nid']).values('article_count').first().get(
            'article_count')) - 1
    models.UserInfo.objects.filter(nid=request.session['user_info']['nid']).update(article_count=str(new_article_count))
    return redirect(to='/article_manage/' + request.session['user_info']['username'])


@check_login
def delete_comment(request):
    """
    删除评论
    :param request:
    :return:
    """
    nid = request.POST.get('comment_nid')
    models.Comment.objects.filter(nid=nid).delete()
    return HttpResponse("OK")


@check_login
def reply(request, username, nid):
    """
    评论
    :param request:
    :param username:
    :param nid:
    :return:
    """
    if request.method == "POST":
        new_comment_count = int(
            models.Article.objects.filter(nid=nid).values('comment_count').first().get('comment_count')) + 1
        models.Article.objects.filter(nid=nid).update(comment_count=str(new_comment_count))
    content = request.POST.get('content')
    user = models.UserInfo.objects.filter(username=username).first()
    models.Comment.objects.create(content=content, article_id=nid, user=user)
    return HttpResponse("OK")


@check_login
def comment_reply(request, comment_id, user_nid, article_id):
    """
    回复评论
    :param request:
    :param comment_id:
    :param user_nid:
    :param article_id:
    :return:
    """
    content = request.POST.get('content')
    models.Reply.objects.create(comment_reply_id=comment_id, content=content, user_id=user_nid, article_id=article_id)
    return HttpResponse("OK")


@check_login
def good(request, article_id, user_id):
    """
    点赞
    :param request:
    :param article_id:
    :param user_id:
    :return:
    """
    result = {'status': True}
    new_read_count = int(
        models.Article.objects.filter(nid=article_id).values('read_count').first().get('read_count')) - 1
    models.Article.objects.filter(nid=article_id).update(read_count=str(new_read_count))
    if models.Up.objects.filter(article_id=article_id, user_id=user_id):
        result = {'status': False}
        return HttpResponse(json.dumps(result))
    else:
        models.Up.objects.create(up=False, article_id=article_id, user_id=user_id)
        new_up_count = int(models.Article.objects.filter(nid=article_id).values('up_count').first().get('up_count')) + 1
        models.Article.objects.filter(nid=article_id).update(up_count=str(new_up_count))
        models.Up.objects.filter(article_id=article_id, user_id=user_id).update(up=True)
        return HttpResponse(json.dumps(result))


@check_login
def user_info(request, username):
    """
    查询用户信息
    :param request:
    :param username:
    :return:
    """
    if request.method == "GET":
        user = models.UserInfo.objects.filter(username=username).first()
        return render(request, 'user_info.html', {'user': user})
    elif request.method == "POST":
        qq = request.POST.get('qq')
        password = request.POST.get('password')
        models.UserInfo.objects.filter(username=username).update(qq=qq, password=password)
        return HttpResponse("OK")


@check_login
def upload_avatar(request, nid):
    """
    头像上传以及预览
    :param request:
    :param nid:
    :return:
    """
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        print(file_obj)
        if not file_obj:
            pass
        else:
            file_name = str(uuid.uuid4())
            file_path = os.path.join('../static/imgs/avatar', file_name)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            models.UserInfo.objects.filter(nid=nid).update(avatar=file_path)
            request.session['user_info']['avatar'] = file_path
            ret['status'] = True
            ret['data'] = file_path
    return HttpResponse(json.dumps(ret))


@check_login
def article_manage(request, username):
    """
    文章管理
    :param request:
    :param username:
    :return:
    """
    if request.method == 'GET':
        user = models.UserInfo.objects.filter(username=username).first()
        article_list = models.Article.objects.filter(author=user)
        data_count = models.Article.objects.filter(author=user).count()
        page = Pagination(request.GET.get('p', 1), data_count)
        page_str = page.page_str(reverse('article', kwargs={'username': username}))
        print(article_list)
        return render(request, 'article_manage.html', {'user': user,
                                                       'article_list': article_list,
                                                       'page_str': page_str})