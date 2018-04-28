from django.contrib import admin

# Register your models here.
from app.models import UserInfo, Article, ArticleDetail, Comment, Reply, Up

admin.site.register(UserInfo)
admin.site.register(Article)
admin.site.register(ArticleDetail)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Up)