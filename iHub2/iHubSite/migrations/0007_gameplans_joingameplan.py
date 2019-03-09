# Generated by Django 2.1.7 on 2019-03-09 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iHubSite', '0006_joinsportplan_sportplans'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamePlans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(max_length=100, verbose_name='游戏名称')),
                ('category', models.CharField(max_length=100, verbose_name='标签/分类')),
                ('game_mode', models.CharField(max_length=100, verbose_name='游戏方式')),
                ('place', models.CharField(max_length=100, null=True, verbose_name='游戏地点')),
                ('start_time', models.DateTimeField(verbose_name='游戏开始时间')),
                ('deadline', models.DateTimeField(null=True, verbose_name='报名截止时间')),
                ('pub_username', models.CharField(max_length=100, verbose_name='发布者昵称')),
                ('pub_name', models.CharField(max_length=100, verbose_name='发布者姓名')),
                ('pub_no', models.CharField(max_length=100, verbose_name='发布者学号/工号')),
                ('pub_wechat', models.CharField(max_length=100, verbose_name='发布者微信ID')),
                ('pub_gender', models.CharField(max_length=100, verbose_name='发布者性别')),
                ('pub_time', models.DateTimeField(auto_now=True, verbose_name='发布日期')),
                ('note', models.CharField(max_length=255, null=True, verbose_name='备注')),
                ('num_need', models.IntegerField(verbose_name='需要人数')),
                ('num_have', models.IntegerField(default=0, verbose_name='已有人数')),
                ('full', models.BooleanField(default=False, verbose_name='是否人数已满')),
                ('ended', models.BooleanField(default=False, verbose_name='是否已结束')),
                ('canceled', models.BooleanField(default=False, verbose_name='是否已取消')),
                ('auth_gender', models.IntegerField(verbose_name='允许加入者性别')),
            ],
        ),
        migrations.CreateModel(
            name='JoinGamePlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('join_no', models.CharField(max_length=100, verbose_name='参加者的学号/工号')),
                ('join_username', models.CharField(max_length=100, verbose_name='参加者的昵称')),
                ('join_name', models.CharField(max_length=100, verbose_name='参加者的姓名')),
                ('join_wechat', models.CharField(max_length=100, verbose_name='参加者的微信ID')),
                ('join_gender', models.CharField(max_length=100, verbose_name='参加者的性别')),
                ('join_plan_id', models.IntegerField(verbose_name='所参加事件在Plan表中的序号')),
                ('join_time', models.DateTimeField(auto_now=True)),
                ('ended', models.BooleanField(default=False)),
                ('canceled', models.BooleanField(default=False)),
                ('quitted', models.BooleanField(default=False)),
            ],
        ),
    ]
