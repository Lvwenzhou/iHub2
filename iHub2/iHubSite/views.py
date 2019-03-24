import datetime
import hashlib
import time

# import ET as ET
import xml.etree.cElementTree as ET
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Min, Count, Sum

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from iHubSite.models import Users, CarpoolPlans, JoinCarpoolPlan, StudyPlans, JoinStudyPlan, SportPlans, JoinSportPlan, \
    GamePlans, JoinGamePlan

from wechatpy import WeChatClient


def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'index.html', {'loged_in': True})
        else:
            return render(request, 'index.html', {'loged_in': False})


def my(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_no = request.user.username
            user = Users.objects.get(no=user_no)
            return render(request, 'my.html', {'user': user})
        else:
            return HttpResponseRedirect('/login/')


def login(request):  # 登录
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return render(request, 'login.html')
        else:
            return render(request, 'index.html', {'logged': True, 'loged_in': True})

    if request.method == 'POST':
        user_no = request.POST.get('user_no_input')
        password = request.POST.get('password_input')
        # 使用auth模块在数据库中查询信息，验证用户是否存在，以验证用户名和密码
        user = auth.authenticate(username=user_no, password=password)
        # 这里的username指的是User表中的学号，在Django的auth_user表中的username使用学号
        # 我们的superuser也是在auth_user表中，superuser的is_staff字段是1，这些普通的用户is_staff字段为0
        if user:
            auth.login(request, user)
            # 用于以后在调用每个视图函数前，auth中间件会根据每次访问视图前请求所带的SEESION里面的ID，去数据库找用户对像，并将对象保存在request.user属性中
            # 中间件执行完后，再执行视图函数
            return redirect('/index/')  # 登录成功，返回至主页
        else:
            return render(request, 'login.html', {'wrong': True})  # 密码或用户名错误，反正没登陆成功
        # 这段登录的代码我也是借鉴的。反正就是用auth模块实现的登录
        # 验证是否登录用if request.user.is_authenticated
        # 所以可以通过request.user.username获取当前用户的学号/工号,然后根据学号/工号去User表中查询当前用户的各种信息
        # 这是我(shl)的写法……期待好一点的方式……


def register(request):  # 注册
    # 注册页面
    if request.method == 'GET':
        return render(request, 'register.html')
    # 提交注册
    if request.method == 'POST':
        name = request.POST.get('name_input')  # 输入姓名
        no = request.POST.get('no_input')  # 输入学号/工号
        username = request.POST.get('username_input')  # 输入用户名
        password = request.POST.get('password_input')  # 输入密码
        password_again = request.POST.get('password_again_input')  # 第二遍输入密码
        gender = request.POST.get('gender_select')  # 选择性别(前端选择框)
        wechatid = request.POST.get('wechatid_input')  # 微信ID,能够添加好友的方式
        reg_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 自动生成的注册时间
        mail = request.POST.get('mail_input')  # 输入邮箱
        phone = request.POST.get('phone_input')  # 输入手机号
        major = request.POST.get('major_input')  # 输入专业
        credit = 100  # 默认100信誉积分
        # 还有头像……还不会做，先放着，以后再说

        if len(name) == 0 or len(no) == 0 or len(username) == 0 or len(password) == 0 or len(
                password_again) == 0 or len(gender) == 0 or len(mail) == 0 or len(wechatid) == 0 or len(
            major) == 0 or len(phone) == 0:
            return render(request, 'register.html', {'not_full': True})  # 填写信息不够完整,重来

        # 不允许一个学号/工号多次注册
        reg_tmp = Users.objects.filter(Q(no=no))
        if len(reg_tmp) != 0:
            return render(request, 'register.html', {'registered': True})  # 已注册过

        # 两次输入密码需一致
        if password == password_again:
            # 以下两句为创建Django的账户系统
            new_user = User.objects.create_user(username=no, password=password_again, email=mail)
            new_user.save()
            # 上述两句Django账户系统，使用用户学号/工号作为username
            password_md5 = make_password(password)  # MD5加密
            # 这里有个小问题……Django的账户系统有个库叫User,我们的账户系统起了个名叫Users……都用到了……比较像注意区分
            # 下面一句是向表User中添加一条数据
            Users.objects.create(username=username, no=no, gender=gender, name=name,
                                 password=password_md5, reg_time=reg_time, weChat_id=wechatid,
                                 phone=phone, mail=mail, major=major, credit=credit)
            return HttpResponseRedirect('/login/')  # 注册成功，跳转至登录界面
        else:
            return render(request, 'register.html', {'password_not_same': True})  # 两次密码输入不一致,重来


def logout(request):  # 登出
    if request.method == 'GET':
        # 以下一句为Django的账户系统
        auth.logout(request)
        response = HttpResponseRedirect('/index/')
        # response.delete_cookie('ticket')
        return response


def search(request):
    if request.method == 'GET':
        return redirect('/index/')
    if request.method == 'POST':
        search_word = request.POST.get('word_for_search')
        if len(search_word) == 0:
            return redirect('/index/')
        carpool_list = CarpoolPlans.objects.filter(
            Q(from_site=search_word) | Q(to_site=search_word) | Q(note=search_word) | Q(category=search_word))
        study_list = StudyPlans.objects.filter(
            Q(intro=search_word) | Q(category=search_word) | Q(study_mode=search_word) | Q(note=search_word))
        sport_list = SportPlans.objects.filter(Q(intro=search_word) | Q(category=search_word) | Q(note=search_word))
        game_list = GamePlans.objects.filter(
            Q(game_name=search_word) | Q(category=search_word) | Q(game_mode=search_word) | Q(note=search_word))
        return render(request, 'search.html',
                      {'key_word': search_word, 'carpool_list': carpool_list, 'study_list': study_list,
                       'sport_list': sport_list, 'game_list': game_list})


# 以下是约出行相关功能的函数:
# 拼车功能首页
def carpool_index(request):
    if request.method == 'GET':
        return render(request, 'carpool_index.html')
    if request.method == 'POST':
        pass


# 搜索结果页
def carpool_search(request):
    if request.method == 'GET':
        return render(request, 'carpool_search.html')
    if request.method == 'POST':
        from_site_input = request.POST.get('from_site_input')
        to_site_input = request.POST.get('to_site_input')
        auth_gender_select = request.POST.get('auth_gender_select')
        if len(from_site_input) == 0 or len(to_site_input) == 0 or len(auth_gender_select) == 0:
            return render(request, 'carpool_index.html', {'incomplete_input': True})
        search_result = CarpoolPlans.objects.filter(
            Q(ended=False) & Q(full=False) & Q(from_site=from_site_input) & Q(to_site=to_site_input) & Q(
                auth_gender=auth_gender_select))
        search_cnt = len(search_result)
        return render(request, 'carpool_search.html', {'search_result': search_result, 'search_cnt': search_cnt})


# 发起拼车
def carpool_start(request):
    if request.method == 'GET':
        # 登录了才能发帖
        if not request.user.is_authenticated:
            return redirect('/login/')
        else:
            return render(request, 'carpool_start.html')  # 已登录，跳转至发起拼车页面
    if request.method == 'POST':
        from_site = request.POST.get('from_site_input')  # 输入起始地点
        to_site = request.POST.get('to_site_input')  # 输入到达地点
        category = request.POST.get('category_select')  # 选择标签/分类
        trip_mode = request.POST.get('trip_mode_select')  # 选择出行方式
        deadline = request.POST.get('deadline_input')  # 输入截止时间
        trip_time = request.POST.get('trip_time_input')  # 输入计划出行时间
        note = request.POST.get('note_input')  # 输入备注
        num_need = request.POST.get('num_need_input')  # 输入除发起者外需要人数
        auth_gender = request.POST.get('auth_gender_select')  # 选择允许加入者性别(男性、女性、两者)
        pub_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 自动生成的发布时间

        user_no_now = request.user.username
        user_now = Users.objects.get(no=user_no_now)
        pub_username = user_now.username
        pub_name = user_now.name
        pub_no = user_now.no
        pub_wechat = user_now.weChat_id
        pub_gender = user_now.gender

        # 不允许输入小于等于零的需要人数
        if int(num_need) <= 0:
            return render(request, 'carpool_start.html', {'invaild_num': True})

        if len(from_site) == 0 or len(to_site) == 0 or len(trip_mode) == 0 or len(category) == 0 or len(
                trip_time) == 0 or len(num_need) == 0 or len(auth_gender) == 0:
            return render(request, 'carpool_start.html', {'no_input': True})  # 未输入完整
        else:
            if len(deadline) == 0:
                deadline = trip_time
            if len(note) == 0:
                note = ""
            CarpoolPlans.objects.create(from_site=from_site, to_site=to_site, category=category, trip_mode=trip_mode,
                                        pub_time=pub_time, deadline=deadline, trip_time=trip_time, note=note,
                                        num_need=num_need,
                                        auth_gender=auth_gender, pub_username=pub_username, pub_name=pub_name,
                                        pub_no=pub_no,
                                        pub_wechat=pub_wechat, pub_gender=pub_gender)
            return HttpResponseRedirect('/carpool_join/')  # 发起成功，返回查看拼车信息页面


# 查看已有拼车
def carpool_join(request):
    if request.method == 'GET':
        plan_list = CarpoolPlans.objects.filter(Q(ended=False) & Q(full=False))
        return render(request, 'carpool_join.html', {'plan_list': plan_list})


# 加入拼车(加入按钮)
def carpool_take_part(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:  # 若未登录
            return redirect('/login/')
        else:
            join_user_now = request.user.username
            join_user = Users.objects.get(no=join_user_now)

            join_plan_id = request.GET.get('plan_id')  # 返回参与事件在表Plan中的id
            join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            join_no = join_user.no
            join_username = join_user.username
            join_name = join_user.name
            join_wechat = join_user.weChat_id
            join_gender = join_user.gender

            plan_to_join = CarpoolPlans.objects.get(id=join_plan_id)
            join_plan_auth_gender = plan_to_join.auth_gender

            # 不可参加性别权限不符的事件
            if (join_gender == 'male' and join_plan_auth_gender == 2) or (
                    join_gender == 'female' and join_plan_auth_gender == 1):
                plan_list = CarpoolPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'carpool_join.html', {'have_no_gender_auth': True, 'plan_list': plan_list})

            # 不可参加自己发起的事件
            if plan_to_join.pub_no == join_user.no:
                plan_list = CarpoolPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'carpool_join.html', {'join_self': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            # 同一事件不可参加多次
            tmp = JoinCarpoolPlan.objects.filter(Q(join_plan_id=join_plan_id) & Q(join_no=join_no))
            if len(tmp) != 0:
                plan_list = CarpoolPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'carpool_join.html', {'have_joined': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            JoinCarpoolPlan.objects.create(join_no=join_no, join_username=join_username, join_name=join_name,
                                           join_wechat=join_wechat, join_gender=join_gender, join_plan_id=join_plan_id,
                                           join_time=join_time)

            plan_to_join.num_have = plan_to_join.num_have + 1  # 该事件参与人数加一
            plan_to_join.save()
            if plan_to_join.num_have == plan_to_join.num_need:  # 若该事件参与人数等于所需人数,full变为True,人数已满
                plan_to_join.full = True
                plan_to_join.save()

            return redirect('/carpool_my/')  # 参与成功，返回个人信息页面


# 高德地图路况
def carpool_map(request):
    return render(request, 'carpool_map.html')


# 查看我的拼车信息
def carpool_my(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('/login/')
        user = request.user.username
        my_start = CarpoolPlans.objects.filter(pub_no=user)  # 我发起的拼车
        my_join_tmp = JoinCarpoolPlan.objects.filter(join_no=user)
        my_join = []
        for i in my_join_tmp:
            if not i.canceled and not i.quitted:
                join_id = i.join_plan_id
                join_plan = CarpoolPlans.objects.get(id=join_id)
                my_join.append(join_plan)
        join_list = JoinCarpoolPlan.objects.all()
        return render(request, 'carpool_my.html', {'not_logged_in': False, 'join_list': join_list,
                                                   'my_start': my_start, 'my_join': my_join})


# 取消已发起的拼车事件
def carpool_cancel(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        plan_to_cancel = CarpoolPlans.objects.get(id=plan_id)
        plan_to_cancel.ended = True
        plan_to_cancel.canceled = True
        plan_to_cancel.save()
        related = JoinCarpoolPlan.objects.filter(join_plan_id=plan_id)
        for item in related:  # 此处不知道对不对,PyCharm没给提示,还需测试
            item.canceled = True
            item.ended = True
            item.save()
        return redirect('/carpool_my/')


# 退出已加入的拼车事件
def carpool_quit(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        user_no = request.user.username

        plan_to_quit = CarpoolPlans.objects.get(id=plan_id)
        plan_to_quit.num_have = plan_to_quit.num_have - 1
        plan_to_quit.save()
        if plan_to_quit.full:
            plan_to_quit.full = False
        plan_to_quit.save()

        related = JoinCarpoolPlan.objects.get(Q(join_plan_id=plan_id) & Q(join_no=user_no))
        related.quitted = True
        related.save()

        return redirect('/carpool_my/')


# 以下是约学习相关功能的函数:
# 约学习功能首页
def study_index(request):
    if request.method == 'GET':
        return render(request, 'study_index.html')
    if request.method == 'POST':
        pass


def study_search(request):
    if request.method == 'GET':
        return render(request, 'study_search.html')
    if request.method == 'POST':
        category_select = request.POST.get('category_select')
        duration_select = request.POST.get('duration_select')
        study_mode_select = request.POST.get('study_mode_select')
        auth_gender_select = request.POST.get('auth_gender_select')
        if len(category_select) == 0 or len(duration_select) == 0 or len(study_mode_select) == 0 or len(
                auth_gender_select) == 0:
            return render(request, 'study_index.html', {'incomplete_input': True})
        search_result = StudyPlans.objects.filter(
            Q(ended=False) & Q(full=False) & Q(category=category_select) & Q(duration=duration_select) & Q(
                study_mode=study_mode_select) & Q(auth_gender=auth_gender_select))
        search_cnt = len(search_result)
        return render(request, 'study_search.html', {'search_result': search_result, 'search_cnt': search_cnt})


# 发起
def study_start(request):
    if request.method == 'GET':
        # 登录了才能发帖
        if not request.user.is_authenticated:
            return redirect('/login/')
        else:
            return render(request, 'study_start.html')  # 已登录，跳转至发起拼车页面
    if request.method == 'POST':
        intro = request.POST.get('intro_input')  # 输入简介
        category = request.POST.get('category_select')  # 选择标签/分类
        duration = request.POST.get('duration_select')  # 选择持续时间
        study_mode = request.POST.get('study_mode_select')  # 选择学习方式
        study_place = request.POST.get('study_place_input')  # 输入学习地点
        start_time = request.POST.get('start_time_input')  # 输入计划开始时间
        end_time = request.POST.get('end_time_input')  # 输入计划结束时间(可不填)
        deadline = request.POST.get('deadline_input')  # 输入截止时间
        note = request.POST.get('note_input')  # 输入备注
        num_need = request.POST.get('num_need_input')  # 输入除发起者外需要人数
        auth_gender = request.POST.get('auth_gender_select')  # 选择允许加入者性别(男性、女性、两者)
        pub_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 自动生成的发布时间

        user_no_now = request.user.username
        user_now = Users.objects.get(no=user_no_now)
        pub_username = user_now.username
        pub_name = user_now.name
        pub_no = user_now.no
        pub_wechat = user_now.weChat_id
        pub_gender = user_now.gender

        # 不允许输入小于等于零的需要人数
        if int(num_need) <= 0:
            return render(request, 'carpool_start.html', {'invaild_num': True})

        if len(intro) == 0 or len(study_place) == 0 or len(duration) == 0 or len(study_mode) == 0 or len(
                start_time) == 0 or len(num_need) == 0 or len(category) == 0 or len(start_time) == 0 or len(
            end_time) == 0 or len(auth_gender) == 0:
            return render(request, 'study_start.html', {'no_input': True})  # 未输入完整
        else:
            if len(deadline) == 0:
                deadline = start_time
            if len(note) == 0:
                note = ""
            StudyPlans.objects.create(intro=intro, category=category, duration=duration,
                                      study_mode=study_mode, study_place=study_place,
                                      start_time=start_time, end_time=end_time, deadline=deadline,
                                      note=note, num_need=num_need,
                                      auth_gender=auth_gender, pub_time=pub_time,
                                      pub_username=pub_username, pub_name=pub_name, pub_no=pub_no,
                                      pub_wechat=pub_wechat, pub_gender=pub_gender)
            return HttpResponseRedirect('/study_join/')  # 发起成功，返回查看页面


# 查看已有
def study_join(request):
    if request.method == 'GET':
        plan_list = StudyPlans.objects.filter(Q(ended=False) & Q(full=False))
        return render(request, 'study_join.html', {'plan_list': plan_list})


# 加入(加入按钮)
def study_take_part(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:  # 若未登录
            return redirect('/login/')
        else:
            join_user_now = request.user.username
            join_user = Users.objects.get(no=join_user_now)

            join_plan_id = request.GET.get('plan_id')  # 返回参与事件在表Plan中的id
            join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            join_no = join_user.no
            join_username = join_user.username
            join_name = join_user.name
            join_wechat = join_user.weChat_id
            join_gender = join_user.gender

            plan_to_join = StudyPlans.objects.get(id=join_plan_id)
            join_plan_auth_gender = plan_to_join.auth_gender

            # 不可参加性别权限不符的事件
            if (join_gender == 'male' and join_plan_auth_gender == 2) or (
                    join_gender == 'female' and join_plan_auth_gender == 1):
                plan_list = StudyPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'study_join.html', {'have_no_gender_auth': True, 'plan_list': plan_list})

            # 不可参加自己发起的事件
            plan_to_join = StudyPlans.objects.get(id=join_plan_id)
            if plan_to_join.pub_no == join_user.no:
                plan_list = StudyPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'study_join.html', {'join_self': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            # 同一事件不可参加多次
            tmp = JoinStudyPlan.objects.filter(Q(join_plan_id=join_plan_id) & Q(join_no=join_no))
            if len(tmp) != 0:
                plan_list = StudyPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'study_join.html', {'have_joined': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            JoinStudyPlan.objects.create(join_no=join_no, join_username=join_username, join_name=join_name,
                                         join_wechat=join_wechat, join_gender=join_gender, join_plan_id=join_plan_id,
                                         join_time=join_time)

            plan_to_join.num_have = plan_to_join.num_have + 1  # 该事件参与人数加一
            plan_to_join.save()
            if plan_to_join.num_have == plan_to_join.num_need:  # 若该事件参与人数等于所需人数,full变为True,人数已满
                plan_to_join.full = True
                plan_to_join.save()

            return redirect('/study_my/')  # 参与成功，返回个人信息页面


# 查看我的信息
def study_my(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('/login/')
        user = request.user.username
        my_start = StudyPlans.objects.filter(pub_no=user)  # 我发起的
        my_join_tmp = JoinStudyPlan.objects.filter(join_no=user)
        my_join = []  # 我加入的
        for i in my_join_tmp:
            if not i.canceled and not i.quitted:
                join_id = i.join_plan_id
                join_plan = StudyPlans.objects.get(id=join_id)
                my_join.append(join_plan)
        join_list = JoinStudyPlan.objects.all()
        return render(request, 'study_my.html', {'not_logged_in': False, 'join_list': join_list,
                                                 'my_start': my_start, 'my_join': my_join})


# 取消已发起的
def study_cancel(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        plan_to_cancel = StudyPlans.objects.get(id=plan_id)
        plan_to_cancel.ended = True
        plan_to_cancel.canceled = True
        plan_to_cancel.save()
        related = JoinStudyPlan.objects.filter(join_plan_id=plan_id)
        for item in related:  # 此处不知道对不对,PyCharm没给提示,还需测试
            item.canceled = True
            item.ended = True
            item.save()
        return redirect('/study_my/')


# 退出已加入的
def study_quit(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        user_no = request.user.username

        plan_to_quit = StudyPlans.objects.get(id=plan_id)
        plan_to_quit.num_have = plan_to_quit.num_have - 1
        plan_to_quit.save()
        if plan_to_quit.full:
            plan_to_quit.full = False
        plan_to_quit.save()

        related = JoinStudyPlan.objects.get(Q(join_plan_id=plan_id) & Q(join_no=user_no))
        related.quitted = True
        related.save()

        return redirect('/study_my/')


# 以下是约健身相关功能的函数:
# 约健身功能首页
def sport_index(request):
    if request.method == 'GET':
        return render(request, 'sport_index.html')
    if request.method == 'POST':
        pass


# 搜索结果页
def sport_search(request):
    if request.method == 'GET':
        return render(request, 'sport_search.html')
    if request.method == 'POST':
        category_select = request.POST.get('category_select')
        duration_select = request.POST.get('duration_select')
        auth_gender_select = request.POST.get('auth_gender_select')
        if len(category_select) == 0 or len(duration_select) == 0 or len(auth_gender_select) == 0:
            return render(request, 'sport_index.html', {'incomplete_input': True})
        search_result = SportPlans.objects.filter(
            Q(ended=False) & Q(full=False) & Q(category=category_select) & Q(duration=duration_select) & Q(
                auth_gender=auth_gender_select))
        search_cnt = len(search_result)
        return render(request, 'sport_search.html', {'search_result': search_result, 'search_cnt': search_cnt})


# 发起
def sport_start(request):
    if request.method == 'GET':
        # 登录了才能发帖
        if not request.user.is_authenticated:
            return redirect('/login/')
        else:
            return render(request, 'sport_start.html')  # 已登录，跳转至发起拼车页面
    if request.method == 'POST':
        intro = request.POST.get('intro_input')  # 输入简介
        category = request.POST.get('category_select')  # 选择标签/分类
        duration = request.POST.get('duration_select')  # 选择持续时间
        place = request.POST.get('place_input')  # 输入学习地点
        start_time = request.POST.get('start_time_input')  # 输入计划开始时间
        end_time = request.POST.get('end_time_input')  # 输入计划结束时间(可不填)
        deadline = request.POST.get('deadline_input')  # 输入截止时间
        note = request.POST.get('note_input')  # 输入备注
        num_need = request.POST.get('num_need_input')  # 输入除发起者外需要人数
        auth_gender = request.POST.get('auth_gender_select')  # 选择允许加入者性别(男性、女性、两者)
        pub_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 自动生成的发布时间

        user_no_now = request.user.username
        user_now = Users.objects.get(no=user_no_now)
        pub_username = user_now.username
        pub_name = user_now.name
        pub_no = user_now.no
        pub_wechat = user_now.weChat_id
        pub_gender = user_now.gender

        # 不允许输入小于等于零的需要人数
        if int(num_need) <= 0:
            return render(request, 'carpool_start.html', {'invaild_num': True})

        if len(intro) == 0 or len(place) == 0 or len(start_time) == 0 or len(end_time) == 0 or len(
                num_need) == 0 or len(category) == 0 or len(duration) == 0 or len(duration) == 0:
            return render(request, 'sport_start.html', {'no_input': True})  # 未输入完整
        else:
            if len(deadline) == 0:
                deadline = start_time
            if len(note) == 0:
                note = ""
            SportPlans.objects.create(intro=intro, category=category, duration=duration, place=place,
                                      start_time=start_time, end_time=end_time, deadline=deadline,
                                      note=note, num_need=num_need,
                                      auth_gender=auth_gender, pub_time=pub_time,
                                      pub_username=pub_username, pub_name=pub_name, pub_no=pub_no,
                                      pub_wechat=pub_wechat, pub_gender=pub_gender)
            return HttpResponseRedirect('/sport_join/')  # 发起成功，返回查看页面


# 查看已有
def sport_join(request):
    if request.method == 'GET':
        plan_list = SportPlans.objects.filter(Q(ended=False) & Q(full=False))
        return render(request, 'sport_join.html', {'plan_list': plan_list})


# 加入(加入按钮)
def sport_take_part(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:  # 若未登录
            return redirect('/login/')
        else:
            join_user_now = request.user.username
            join_user = Users.objects.get(no=join_user_now)

            join_plan_id = request.GET.get('plan_id')  # 返回参与事件在表Plan中的id
            join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            join_no = join_user.no
            join_username = join_user.username
            join_name = join_user.name
            join_wechat = join_user.weChat_id
            join_gender = join_user.gender

            plan_to_join = SportPlans.objects.get(id=join_plan_id)
            join_plan_auth_gender = plan_to_join.auth_gender

            # 不可参加性别权限不符的事件
            if (join_gender == 'male' and join_plan_auth_gender == 2) or (
                    join_gender == 'female' and join_plan_auth_gender == 1):
                plan_list = SportPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'sport_join.html', {'have_no_gender_auth': True, 'plan_list': plan_list})

            # 不可参加自己发起的事件
            plan_to_join = SportPlans.objects.get(id=join_plan_id)
            if plan_to_join.pub_no == join_user.no:
                plan_list = SportPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'sport_join.html', {'join_self': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            # 同一事件不可参加多次
            tmp = JoinSportPlan.objects.filter(Q(join_plan_id=join_plan_id) & Q(join_no=join_no))
            if len(tmp) != 0:
                plan_list = SportPlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'sport_join.html', {'have_joined': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            JoinSportPlan.objects.create(join_no=join_no, join_username=join_username, join_name=join_name,
                                         join_wechat=join_wechat, join_gender=join_gender, join_plan_id=join_plan_id,
                                         join_time=join_time)

            plan_to_join.num_have = plan_to_join.num_have + 1  # 该事件参与人数加一
            plan_to_join.save()
            if plan_to_join.num_have == plan_to_join.num_need:  # 若该事件参与人数等于所需人数,full变为True,人数已满
                plan_to_join.full = True
                plan_to_join.save()

            return redirect('/sport_my/')  # 参与成功，返回个人信息页面


# 查看我的信息
def sport_my(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('/login/')
        user = request.user.username
        my_start = SportPlans.objects.filter(pub_no=user)  # 我发起的
        my_join_tmp = JoinSportPlan.objects.filter(join_no=user)
        my_join = []  # 我加入的
        for i in my_join_tmp:
            if not i.canceled and not i.quitted:
                join_id = i.join_plan_id
                join_plan = SportPlans.objects.get(id=join_id)
                my_join.append(join_plan)
        join_list = JoinSportPlan.objects.all()
        return render(request, 'sport_my.html', {'not_logged_in': False, 'join_list': join_list,
                                                 'my_start': my_start, 'my_join': my_join})


# 取消已发起的
def sport_cancel(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        plan_to_cancel = SportPlans.objects.get(id=plan_id)
        plan_to_cancel.ended = True
        plan_to_cancel.canceled = True
        plan_to_cancel.save()
        related = JoinSportPlan.objects.filter(join_plan_id=plan_id)
        for item in related:  # 此处不知道对不对,PyCharm没给提示,还需测试
            item.canceled = True
            item.ended = True
            item.save()
        return redirect('/sport_my/')


# 退出已加入的
def sport_quit(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        user_no = request.user.username

        plan_to_quit = SportPlans.objects.get(id=plan_id)
        plan_to_quit.num_have = plan_to_quit.num_have - 1
        plan_to_quit.save()
        if plan_to_quit.full:
            plan_to_quit.full = False
        plan_to_quit.save()

        related = JoinSportPlan.objects.get(Q(join_plan_id=plan_id) & Q(join_no=user_no))
        related.quitted = True
        related.save()

        return redirect('/sport_my/')


# 以下是约游戏相关功能的函数:
# 约游戏功能首页
def game_index(request):
    if request.method == 'GET':
        return render(request, 'game_index.html')
    if request.method == 'POST':
        pass


# 搜索结果页
def game_search(request):
    if request.method == 'GET':
        return render(request, 'game_search.html')
    if request.method == 'POST':
        category_select = request.POST.get('category_select')
        game_mode_select = request.POST.get('game_mode_select')
        auth_gender_select = request.POST.get('auth_gender_select')
        # print(category_select)
        # print(game_mode_select)
        # print(auth_gender_select)
        if len(category_select) == 0 or len(auth_gender_select) == 0 or len(game_mode_select) == 0:
            return render(request, 'game_index.html', {'incomplete_input': True})
        search_result = GamePlans.objects.filter(
            Q(ended=False) & Q(full=False) & Q(game_mode=game_mode_select) & Q(category=category_select) & Q(
                auth_gender=auth_gender_select))
        search_cnt = len(search_result)
        return render(request, 'game_search.html', {'search_result': search_result, 'search_cnt': search_cnt})


# 发起
def game_start(request):
    if request.method == 'GET':
        # 登录了才能发帖
        if not request.user.is_authenticated:
            return redirect('/login/')
        else:
            return render(request, 'game_start.html')  # 已登录，跳转至发起拼车页面
    if request.method == 'POST':
        game_name = request.POST.get('name_input')  # 输入游戏名称
        category = request.POST.get('category_select')  # 选择标签/分类
        game_mode = request.POST.get('game_mode_select')  # 选择游戏方式
        place = request.POST.get('place_input')  # 输入游戏地点
        start_time = request.POST.get('start_time_input')  # 输入计划开始时间
        deadline = request.POST.get('deadline_input')  # 输入截止时间
        duration = request.POST.get('duration_select')  # 选择持续时间
        note = request.POST.get('note_input')  # 输入备注
        num_need = request.POST.get('num_need_input')  # 输入除发起者外需要人数
        auth_gender = request.POST.get('auth_gender_select')  # 选择允许加入者性别(男性、女性、两者)
        pub_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 自动生成的发布时间

        user_no_now = request.user.username
        user_now = Users.objects.get(no=user_no_now)
        pub_username = user_now.username
        pub_name = user_now.name
        pub_no = user_now.no
        pub_wechat = user_now.weChat_id
        pub_gender = user_now.gender

        # 不允许输入小于等于零的需要人数
        if int(num_need) <= 0:
            return render(request, 'carpool_start.html', {'invaild_num': True})

        if len(game_name) == 0 or len(place) == 0 or len(start_time) == 0 or len(num_need) == 0 or len(
                category) == 0 or len(game_mode) == 0 or len(auth_gender) == 0 or len(duration) == 0:
            return render(request, 'game_start.html', {'no_input': True})  # 未输入完整
        else:
            if len(deadline) == 0:
                deadline = start_time
            if len(note) == 0:
                note = ""
            GamePlans.objects.create(game_name=game_name, category=category, game_mode=game_mode, place=place,
                                     start_time=start_time, deadline=deadline,
                                     note=note, num_need=num_need, duration=duration,
                                     auth_gender=auth_gender, pub_time=pub_time,
                                     pub_username=pub_username, pub_name=pub_name, pub_no=pub_no,
                                     pub_wechat=pub_wechat, pub_gender=pub_gender)
            return HttpResponseRedirect('/game_join/')  # 发起成功，返回查看页面


# 查看已有
def game_join(request):
    if request.method == 'GET':
        plan_list = GamePlans.objects.filter(Q(ended=False) & Q(full=False))
        return render(request, 'game_join.html', {'plan_list': plan_list})


# 加入(加入按钮)
def game_take_part(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:  # 若未登录
            return redirect('/login/')
        else:
            join_user_now = request.user.username
            join_user = Users.objects.get(no=join_user_now)

            join_plan_id = request.GET.get('plan_id')  # 返回参与事件在表Plan中的id
            join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            join_no = join_user.no
            join_username = join_user.username
            join_name = join_user.name
            join_wechat = join_user.weChat_id
            join_gender = join_user.gender

            plan_to_join = GamePlans.objects.get(id=join_plan_id)
            join_plan_auth_gender = plan_to_join.auth_gender

            # 不可参加性别权限不符的事件
            if (join_gender == 'male' and join_plan_auth_gender == 2) or (
                    join_gender == 'female' and join_plan_auth_gender == 1):
                plan_list = GamePlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'game_join.html', {'have_no_gender_auth': True, 'plan_list': plan_list})

            # 不可参加自己发起的事件
            plan_to_join = GamePlans.objects.get(id=join_plan_id)
            if plan_to_join.pub_no == join_user.no:
                plan_list = GamePlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'game_join.html', {'join_self': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            # 同一事件不可参加多次
            tmp = JoinGamePlan.objects.filter(Q(join_plan_id=join_plan_id) & Q(join_no=join_no))
            if len(tmp) != 0:
                plan_list = GamePlans.objects.filter(Q(ended=False) & Q(full=False))
                return render(request, 'game_join.html', {'have_joined': True, 'plan_list': plan_list})  # 返回查看拼车信息页面

            JoinGamePlan.objects.create(join_no=join_no, join_username=join_username, join_name=join_name,
                                        join_wechat=join_wechat, join_gender=join_gender, join_plan_id=join_plan_id,
                                        join_time=join_time)

            plan_to_join.num_have = plan_to_join.num_have + 1  # 该事件参与人数加一
            plan_to_join.save()
            if plan_to_join.num_have == plan_to_join.num_need:  # 若该事件参与人数等于所需人数,full变为True,人数已满
                plan_to_join.full = True
                plan_to_join.save()

            return redirect('/game_my/')  # 参与成功，返回个人信息页面


# 查看我的信息
def game_my(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return redirect('/login/')
        user = request.user.username
        my_start = GamePlans.objects.filter(pub_no=user)  # 我发起的
        my_join_tmp = JoinGamePlan.objects.filter(join_no=user)
        my_join = []  # 我加入的
        for i in my_join_tmp:
            if not i.canceled and not i.quitted:
                join_id = i.join_plan_id
                join_plan = GamePlans.objects.get(id=join_id)
                my_join.append(join_plan)
        join_list = JoinGamePlan.objects.all()
        return render(request, 'game_my.html', {'not_logged_in': False, 'join_list': join_list,
                                                'my_start': my_start, 'my_join': my_join})


# 取消已发起的
def game_cancel(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        plan_to_cancel = GamePlans.objects.get(id=plan_id)
        plan_to_cancel.ended = True
        plan_to_cancel.canceled = True
        plan_to_cancel.save()
        related = JoinGamePlan.objects.filter(join_plan_id=plan_id)
        for item in related:  # 此处不知道对不对,PyCharm没给提示,还需测试
            item.canceled = True
            item.ended = True
            item.save()
        return redirect('/game_my/')


# 退出已加入的
def game_quit(request):
    if request.method == 'GET':
        plan_id = request.GET.get('plan_id')  # 返回这一事件在Plan表中的id
        user_no = request.user.username

        plan_to_quit = GamePlans.objects.get(id=plan_id)
        plan_to_quit.num_have = plan_to_quit.num_have - 1
        plan_to_quit.save()
        if plan_to_quit.full:
            plan_to_quit.full = False
        plan_to_quit.save()

        related = JoinGamePlan.objects.get(Q(join_plan_id=plan_id) & Q(join_no=user_no))
        related.quitted = True
        related.save()

        return redirect('/game_my/')


# 以下为微信端所需函数
@csrf_exempt
def weChat(request):
    if request.method == 'GET':
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token = "sshhhll1"
        tmpArr = [token, timestamp, nonce]
        tmpArr.sort()
        string = ''.join(tmpArr).encode('utf-8')
        string = hashlib.sha1(string).hexdigest()
        if string == signature:
            return HttpResponse(echostr)
        else:
            return HttpResponse("false")
    if request.method == 'POST':
        if not check_sign(request):
            print('没连上???')
            return None
        request_xml = ET.fromstring(request.body)
        ToUserName = request_xml.find('ToUserName').text
        FromUserName = request_xml.find('FromUserName').text
        CreateTime = request_xml.find('CreateTime').text
        MsgType = request_xml.find('MsgType').text
        # MsgId = request_xml.find('MsgId').text
        if MsgType == 'text':
            Content = request_xml.find('Content').text
            Content = reply_text_msg(Content)
            return render(request, 'XMLtext.xml', {'FromUserName': ToUserName, 'ToUserName': FromUserName,
                                                   CreateTime: int(time.time()), 'MsgType': 'text', 'Content': Content})
        if MsgType == 'image':
            MediaId = request_xml.find('MediaId').text
            # PicUrl = request_xml.find('PicUrl').text
            return render(request, 'XMLimg.xml', {'FromUserName': ToUserName, 'ToUserName': FromUserName,
                                                  CreateTime: int(time.time()), 'MsgType': 'image', 'MediaId': MediaId})
        if MsgType == 'event':
            Event = request_xml.find('Event').text
            EventKey = request_xml.find('EventKey').text
            if Event == 'CLICK' and EventKey == 'help':
                Content = 'help'
                return render(request, 'XMLtext.xml', {'FromUserName': ToUserName, 'ToUserName': FromUserName,
                                                       CreateTime: int(time.time()), 'MsgType': 'text',
                                                       'Content': Content})


# check_sign函数检查微信签名
@csrf_exempt
def check_sign(request):
    signature = request.GET.get('signature')
    timestamp = request.GET.get('timestamp')
    nonce = request.GET.get('nonce')
    echostr = request.GET.get('echostr')
    token = "sshhhll1"
    tmpArr = [token, timestamp, nonce]
    tmpArr.sort()
    string = ''.join(tmpArr).encode('utf-8')
    string = hashlib.sha1(string).hexdigest()
    if string == signature:
        return True
    else:
        return False


# 处理文本回复信息
def reply_text_msg(content):
    if content == '帮助':
        return 'help'
    else:
        return content


# 微信公众号菜单
def create_menu(request):
    # 第一个参数是公众号里面的appID，第二个参数是appsecret
    client = WeChatClient("wx6cdf8d8ab887e73d", "595971790db2a0e87860d3a017600f37")
    client.menu.create({
        "button": [
            {
                "name": "!Hub",
                "sub_button": [
                    {
                        "type": "click",
                        "name": "帮助",
                        "key": "help"
                    },
                    {
                        "type": "view",
                        "name": "!Hub首页",
                        "url": "http://sshhhll1.natapp1.cc/index"
                    },
                    {
                        "type": "view",
                        "name": "登录",
                        "url": "http://sshhhll1.natapp1.cc/login"
                    },
                    {
                        "type": "view",
                        "name": "注册",
                        "url": "http://sshhhll1.natapp1.cc/register"
                    }
                ]
            },

            {
                "name": "查看",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "约出行",
                        "url": "http://sshhhll1.natapp1.cc/carpool_join"
                    },
                    {
                        "type": "view",
                        "name": "约学习",
                        "url": "http://sshhhll1.natapp1.cc/study_join"
                    },
                    {
                        "type": "view",
                        "name": "约健身",
                        "url": "http://sshhhll1.natapp1.cc/sport_join"
                    },
                    {
                        "type": "view",
                        "name": "约游戏",
                        "url": "http://sshhhll1.natapp1.cc/game_join"
                    }
                ]
            },

            {
                "name": "发起",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "约出行",
                        "url": "http://sshhhll1.natapp1.cc/carpool_start"
                    },
                    {
                        "type": "view",
                        "name": "约学习",
                        "url": "http://sshhhll1.natapp1.cc/study_start"
                    },
                    {
                        "type": "view",
                        "name": "约健身",
                        "url": "http://sshhhll1.natapp1.cc/sport_start"
                    },
                    {
                        "type": "view",
                        "name": "约游戏",
                        "url": "http://sshhhll1.natapp1.cc/game_start"
                    }
                ]
            }
        ],
    })
    return HttpResponse('ok')


# 数据可视化
# 数据分析导航页
def data_analyse_index(request):
    if request.method == 'GET':
        return render(request, 'data_analyse_index.html')
    else:
        pass


# 性别年级表
def echarts_gender(request):
    if request.method == 'GET':
        male1_number = Users.objects.filter(gender='male', no__startswith='1018').aggregate(Count('id'))
        female1_number = Users.objects.filter(gender='female', no__startswith='1018').aggregate(Count('id'))
        male2_number = Users.objects.filter(gender='male', no__startswith='1017').aggregate(Count('id'))
        female2_number = Users.objects.filter(gender='female', no__startswith='1017').aggregate(Count('id'))
        male3_number = Users.objects.filter(gender='male', no__startswith='1016').aggregate(Count('id'))
        female3_number = Users.objects.filter(gender='female', no__startswith='1016').aggregate(Count('id'))
        male4_number = Users.objects.filter(gender='male', no__startswith='1015').aggregate(Count('id'))
        female4_number = Users.objects.filter(gender='female', no__startswith='1015').aggregate(Count('id'))
        number = {'male1_number': male1_number['id__count'], 'female1_number': female1_number['id__count'],
                  'male2_number': male2_number['id__count'], 'female2_number': female2_number['id__count'],
                  'male3_number': male3_number['id__count'], 'female3_number': female3_number['id__count'],
                  'male4_number': male4_number['id__count'], 'female4_number': female4_number['id__count']}
        print(number)
        return render(request, 'echarts_gender.html', number)


# 旭日图
def echarts_sunburst(request):
    if request.method == 'GET':
        study_numall = StudyPlans.objects.filter().aggregate(Count('id'))  # 得到studyplans 所有的人数
        study_num1 = StudyPlans.objects.filter(pub_no__startswith='1018').aggregate(Count('id'))  # 得到studyplans中 大一的人数
        study_num2 = StudyPlans.objects.filter(pub_no__startswith='1017').aggregate(Count('id'))  # 得到studyplans中 大二的人数
        study_num3 = StudyPlans.objects.filter(pub_no__startswith='1016').aggregate(Count('id'))  # 得到studyplans中 大三的人数
        study_num4 = StudyPlans.objects.filter(pub_no__startswith='1015').aggregate(Count('id'))  # 得到studyplans中 大四的人数

        sport_numall = SportPlans.objects.filter().aggregate(Count('id'))  # 得到Sportplans 所有的人数
        sport_num1 = SportPlans.objects.filter(pub_no__startswith='1018').aggregate(Count('id'))  # 得到Sportplans中 大一的人数
        sport_num2 = SportPlans.objects.filter(pub_no__startswith='1017').aggregate(Count('id'))  # 得到Sportplans中 大二的人数
        sport_num3 = SportPlans.objects.filter(pub_no__startswith='1016').aggregate(Count('id'))  # 得到Sportplans中 大三的人数
        sport_num4 = SportPlans.objects.filter(pub_no__startswith='1015').aggregate(Count('id'))  # 得到Sportplans中 大四的人数

        game_numall = GamePlans.objects.filter().aggregate(Count('id'))  # 得到GamePlans 所有的人数
        game_num1 = GamePlans.objects.filter(pub_no__startswith='1018').aggregate(Count('id'))  # 得到GamePlans中 大一的人数
        game_num2 = GamePlans.objects.filter(pub_no__startswith='1017').aggregate(Count('id'))  # 得到GamePlans中 大二的人数
        game_num3 = GamePlans.objects.filter(pub_no__startswith='1016').aggregate(Count('id'))  # 得到GamePlans中 大三的人数
        game_num4 = GamePlans.objects.filter(pub_no__startswith='1015').aggregate(Count('id'))  # 得到GamePlans中 大四的人数

        carpool_numall = CarpoolPlans.objects.filter().aggregate(Count('id'))  # 得到CarpoolPlans所有的人数
        carpool_num1 = CarpoolPlans.objects.filter(pub_no__startswith='1018').aggregate(
            Count('id'))  # 得到CarpoolPlans中 大一的人数
        carpool_num2 = CarpoolPlans.objects.filter(pub_no__startswith='1017').aggregate(
            Count('id'))  # 得到CarpoolPlans中 大二的人数
        carpool_num3 = CarpoolPlans.objects.filter(pub_no__startswith='1016').aggregate(
            Count('id'))  # 得到CarpoolPlans中 大三的人数
        carpool_num4 = CarpoolPlans.objects.filter(pub_no__startswith='1015').aggregate(
            Count('id'))  # 得到CarpoolPlans中 大四的人数
        number = {'study_numall': study_numall['id__count'], 'study_num1': study_num1['id__count'],
                  'study_num2': study_num2['id__count'], 'study_num3': study_num3['id__count'],
                  'study_num4': study_num4['id__count'],
                  'carpool_numall': carpool_numall['id__count'], 'carpool_num1': carpool_num1['id__count'],
                  'carpool_num2': carpool_num2['id__count'], 'carpool_num3': carpool_num3['id__count'],
                  'carpool_num4': carpool_num4['id__count'],
                  'sport_numall': sport_numall['id__count'], 'sport_num1': sport_num1['id__count'],
                  'sport_num2': sport_num2['id__count'], 'sport_num3': sport_num3['id__count'],
                  'sport_num4': sport_num4['id__count'],
                  'game_numall': game_numall['id__count'], 'game_num1': game_num1['id__count'],
                  'game_num2': game_num2['id__count'], 'game_num3': game_num3['id__count'],
                  'game_num4': game_num4['id__count']
                  }
        return render(request, 'echarts_sunburst.html', number)
