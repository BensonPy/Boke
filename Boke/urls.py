"""Boke URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.urls import path
from django.conf.urls import url, include
from app import views
urlpatterns = [
    url(r'admin/', admin.site.urls),
    url('^$', views.index),
    url(r'^home/$', views.index),
    url(r'^login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^check_code/$', views.check_code),
    url(r'^register/$', views.register),
    url(r'^reply/(?P<username>\w+)/(?P<nid>\d+)$', views.reply),
    url(r'^write/(?P<author_name>\w+).html$', views.write),
    url(r'^delete/(?P<article_id>\d+)/$', views.delete),
    url(r'^edit/(?P<author_name>\w+)/(?P<article_id>\d+).html', views.edit),
    url(r'^all/(?P<article_type_id>\d+).html$', views.index, name='index'),
    url(r'^(?P<article_type_id>\w+)/(?P<author_name>\w+)/(?P<nid>\d+).html$', views.detail),
    url(r'^delete_comment/$', views.delete_comment),
    url(r'^good/(?P<article_id>\d+)/(?P<user_id>\d+)$', views.good),
    url(r'^user_info/(?P<username>\w+)$', views.user_info),
    url(r'^upload-avatar/(?P<nid>\d+)$', views.upload_avatar),
    url(r'^article_manage/(?P<username>\w+)', views.article_manage, name='article'),
    url(r'^comment-reply/(?P<article_id>\d+)/(?P<comment_id>\d+)/(?P<user_nid>\w+)$', views.comment_reply),
]
