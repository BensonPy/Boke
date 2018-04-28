from django.db import models


class UserInfo(models.Model):
    """
    用户信息表
    """
    nid = models.BigAutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=64)
    avatar = models.ImageField(verbose_name='头像', default='static/imgs/avatar/default.png')
    qq = models.CharField(verbose_name='qq', max_length=32)
    article_count = models.IntegerField(verbose_name='文章个数', default=0)


class Article(models.Model):
    """
    文章表
    """
    nid = models.BigAutoField(primary_key=True)
    title = models.CharField(verbose_name='文章标题', max_length=128)
    summary = models.CharField(verbose_name='文章简介', max_length=255)
    read_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    author = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    type_choices = [
        (1, "学习"),
        (2, "游戏"),
        (3, "感情"),
        (4, "生活"),
    ]
    article_type_id = models.IntegerField(choices=type_choices, default=None)


class ArticleDetail(models.Model):
    """
    文章详细表
    """
    content = models.TextField(verbose_name='文章内容')
    article = models.OneToOneField(verbose_name='所属文章', to='Article', to_field='nid', on_delete=models.CASCADE)


class Comment(models.Model):
    """
    评论表
    """
    nid = models.BigAutoField(primary_key=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)


class Reply(models.Model):
    """
    回复表
    """
    nid = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(verbose_name="回复文章", to="Article", to_field="nid", on_delete=models.CASCADE)
    content = models.CharField(verbose_name="回复内容", max_length=255)
    user = models.ForeignKey(verbose_name="回复用户", to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    comment_reply = models.ForeignKey(verbose_name="回复评论", to='Comment', to_field='nid', on_delete=models.CASCADE)


class Up(models.Model):
    """
    记录赞表
    """
    nid = models.BigAutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name='赞用户', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    up = models.BooleanField(verbose_name='是否赞')