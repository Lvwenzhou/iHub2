from django.db import models


# Create your models here.
class Users(models.Model):  # 用户信息
    username = models.CharField(u"用户名", max_length=100)
    password = models.CharField(u"密码", max_length=100, null=True)  # 目前在Django的账户系统中存储密码,这里没必要存,可以为空
    no = models.CharField(u"学号/工号", max_length=100)
    identity = models.CharField(u"身份", max_length=100, null=True)  # 教师、学生、临时学生、临时教职工、外校工作人员等
    name = models.CharField(u"姓名", max_length=100)
    gender = models.CharField(u"性别", max_length=100)
    major = models.CharField(u"专业", max_length=100)
    avatar = models.ImageField(upload_to="static/avatar", null=True)  # 头像这里还不会写，先让这里空着，基本功能做完再写
    mail = models.CharField(u"邮箱", max_length=100)
    weChat_id = models.CharField(u"微信ID", max_length=100)
    phone = models.CharField(u"手机号", max_length=100)
    reg_time = models.DateTimeField(u"注册时间", max_length=100)
    credit = models.IntegerField(u"信誉积分", default=100)  # 信誉积分,默认100,取消拼车、退出拼车、预定不取会扣除
    status = models.CharField(u"个性签名/状态", max_length=255, null=True)  # 个性签名


# 以下是拼车相关功能所需表
class CarpoolPlans(models.Model):  # 拼车计划
    from_site = models.CharField(u"起点", max_length=100)
    to_site = models.CharField(u"终点", max_length=100)
    category = models.CharField(u"标签/分类", max_length=100)  # 奉贤至徐汇、奉贤至市内、至机场等
    trip_mode = models.CharField(u"出行方式", max_length=100)  # 出租车、自驾等
    pub_time = models.DateTimeField(u"发布日期", auto_now=True)  # 该条计划发布时间
    deadline = models.DateTimeField(u"截止时间", null=True)  # 在此时间前加入
    trip_time = models.DateTimeField(u"计划出行时间")  # 计划出行时间
    pub_username = models.CharField(u"发布者昵称", max_length=100)
    pub_name = models.CharField(u"发布者姓名", max_length=100)
    pub_no = models.CharField(u"发布者学号/工号", max_length=100)
    pub_wechat = models.CharField(u"发布者微信ID", max_length=100)
    pub_gender = models.CharField(u"发布者性别", max_length=100)
    note = models.CharField(u"备注", max_length=255, null=True)
    num_need = models.IntegerField(u"需要人数")  # 除发起者外的需要人数
    num_have = models.IntegerField(u"已有人数", default=0)  # 默认已有0人
    full = models.BooleanField(u"是否人数已满", default=False)  # 默认False未满,当num_have==num_need时为True
    ended = models.BooleanField(u"是否已结束", default=False)  # 默认未结束(取消、已过出行时间、用户主动标记为结束,都算结束)
    canceled = models.BooleanField(u"是否已取消", default=False)  # 默认未取消(指用户主动取消此次行程)
    auth_gender = models.IntegerField(u"允许加入者性别")  # 0-均可加入,1-仅男性,2-仅女性

    def __unicode__(self):
        return self.id
    """
    class Meta:  # 按时间下降排序
        ordering = ['-pub_time']
        verbose_name = "出行计划"
        verbose_name_plural = "出行计划"
    """


class JoinCarpoolPlan(models.Model):  # 参与者与计划的关系表
    join_no = models.CharField(u"参加者的学号/工号", max_length=100)
    join_username = models.CharField(u"参加者的昵称", max_length=100)
    join_name = models.CharField(u"参加者的姓名", max_length=100)
    join_wechat = models.CharField(u"参加者的微信ID", max_length=100)
    join_gender = models.CharField(u"参加者的性别", max_length=100)
    join_plan_id = models.IntegerField(u"所参加事件在Plan表中的序号")
    # 为了保证序号join_plan_id正确，Plan表中的数据不删除，可以改变ended的值来表示
    join_time = models.DateTimeField(auto_now=True)  # 加入时的时间
    ended = models.BooleanField(default=False)  # 计划结束(同Plan表中的ended) 默认False, 未结束
    canceled = models.BooleanField(default=False)  # 是否已取消(指行程是否已取消) 默认False, 未取消
    quitted = models.BooleanField(default=False)  # 是否已退出 默认False, 未退出


# 以下是约学习相关功能表
class StudyPlans(models.Model):  # 约学习计划
    intro = models.CharField(u"简介", max_length=200)  # 简介,不超过200字
    category = models.CharField(u"标签/分类", max_length=100)
    # 标签可包括互相监督期末复习、互相励志考研、互相教学、单方面教学、项目求队友、共同研究、各种考证考试备考等
    duration = models.CharField(u"时长", max_length=100)  # 短期(小于等于一天一夜)、中期(大于一天一夜小于两个月)、长期(两个月以上)
    study_mode = models.CharField(u"学习方式", max_length=100, null=True)  # 主要为讲解、主要为安静学习等
    study_place = models.CharField(u"学习地点", max_length=100, null=True)
    start_time = models.DateTimeField(u"计划开始时间", auto_now=False)
    end_time = models.DateTimeField(u"计划结束时间", auto_now=False, null=True)  # 有些计划结束时间可以不写，为空
    deadline = models.DateTimeField(u"报名截止时间", auto_now=False, null=True)  # 在此时间前加入，若为空则为计划开始时间
    pub_username = models.CharField(u"发布者昵称", max_length=100)
    pub_name = models.CharField(u"发布者姓名", max_length=100)
    pub_no = models.CharField(u"发布者学号/工号", max_length=100)
    pub_wechat = models.CharField(u"发布者微信ID", max_length=100)
    pub_gender = models.CharField(u"发布者性别", max_length=100)
    pub_time = models.DateTimeField(u"发布日期", auto_now=True)  # 该条计划发布时间
    note = models.CharField(u"备注", max_length=255, null=True)
    num_need = models.IntegerField(u"需要人数")  # 除发起者外的需要人数
    num_have = models.IntegerField(u"已有人数", default=0)  # 默认已有0人
    full = models.BooleanField(u"是否人数已满", default=False)  # 默认False未满,当num_have==num_need时为True
    ended = models.BooleanField(u"是否已结束", default=False)  # 默认未结束(取消、已过出行时间、用户主动标记为结束,都算结束)
    canceled = models.BooleanField(u"是否已取消", default=False)  # 默认未取消(指用户主动取消此次行程)
    auth_gender = models.IntegerField(u"允许加入者性别")  # 0-均可加入,1-仅男性,2-仅女性


class JoinStudyPlan(models.Model):  # 参与者与计划的关系表
    join_no = models.CharField(u"参加者的学号/工号", max_length=100)
    join_username = models.CharField(u"参加者的昵称", max_length=100)
    join_name = models.CharField(u"参加者的姓名", max_length=100)
    join_wechat = models.CharField(u"参加者的微信ID", max_length=100)
    join_gender = models.CharField(u"参加者的性别", max_length=100)
    join_plan_id = models.IntegerField(u"所参加事件在Plan表中的序号")
    # 为了保证序号join_plan_id正确，Plan表中的数据不删除，可以改变ended的值来表示
    join_time = models.DateTimeField(auto_now=True)  # 加入时的时间
    ended = models.BooleanField(default=False)  # 计划结束(同Plan表中的ended) 默认False, 未结束
    canceled = models.BooleanField(default=False)  # 是否已取消(指学习计划是否已取消) 默认False, 未取消
    quitted = models.BooleanField(default=False)  # 是否已退出 默认False, 未退出


# 以下是约健身相关功能表
class SportPlans(models.Model):
    intro = models.CharField(u"简介", max_length=200)  # 简介,不超过200字
    category = models.CharField(u"标签/分类", max_length=100)  # 标签包括兴趣爱好、健美、减肥、养生等
    duration = models.CharField(u"时长", max_length=100)  # 短期(小于等于一天一夜)、中期(大于一天一夜小于两个月)、长期(两个月以上)
    study_mode = models.CharField(u"学习方式", max_length=100, null=True)  # 主要为讲解、主要为安静学习等
    study_place = models.CharField(u"学习地点", max_length=100, null=True)
    start_time = models.DateTimeField(u"计划开始时间", auto_now=False)
    end_time = models.DateTimeField(u"计划结束时间", auto_now=False, null=True)  # 有些计划结束时间可以不写，为空
    deadline = models.DateTimeField(u"报名截止时间", auto_now=False, null=True)  # 在此时间前加入，若为空则为计划开始时间
    pub_username = models.CharField(u"发布者昵称", max_length=100)
    pub_name = models.CharField(u"发布者姓名", max_length=100)
    pub_no = models.CharField(u"发布者学号/工号", max_length=100)
    pub_wechat = models.CharField(u"发布者微信ID", max_length=100)
    pub_gender = models.CharField(u"发布者性别", max_length=100)
    pub_time = models.DateTimeField(u"发布日期", auto_now=True)  # 该条计划发布时间
    note = models.CharField(u"备注", max_length=255, null=True)
    num_need = models.IntegerField(u"需要人数")  # 除发起者外的需要人数
    num_have = models.IntegerField(u"已有人数", default=0)  # 默认已有0人
    full = models.BooleanField(u"是否人数已满", default=False)  # 默认False未满,当num_have==num_need时为True
    ended = models.BooleanField(u"是否已结束", default=False)  # 默认未结束(取消、已过出行时间、用户主动标记为结束,都算结束)
    canceled = models.BooleanField(u"是否已取消", default=False)  # 默认未取消(指用户主动取消此次行程)
    auth_gender = models.IntegerField(u"允许加入者性别")  # 0-均可加入,1-仅男性,2-仅女性
