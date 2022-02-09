from django.http import HttpResponse
from django.shortcuts import render
from time import sleep
# Create your views here.
import requests
from pytyut import Pytyut
# 创建会话对象（方便使用的全局变量）
from app.models import Class_Schedule, yunlu_class_schedule
pytyut_user = ''
bjh_list = []
class_schedule_dict = {}


def main_page(request):
    global pytyut_user
    global bjh_list
    global class_schedule_dict
    if request.method == 'POST':
        # 判断是否为登录操作
        if request.POST.get('userid'):
            username = request.POST.get('userid')
            password = request.POST.get('password')

            # 2022/2/9 升级为pytyut
            pytyut_user = Pytyut(username, password)
            Pytyut.node_link = pytyut_user.auto_node_chose(debug=True)
            if Pytyut.node_link is None:
                return HttpResponse('连不上教务系统qwq')
            print('当前节点：', Pytyut.node_link)
            login_info = pytyut_user.login(debug=True)

            njxszy_Tree = pytyut_user.get_major_class_tree(xnxq=request.POST.get('xnxq'))
            # 遍历，把所有bjh信息放在一个list里
            # 筛选出当前年级的条件
            # njdm = request.POST.get('xnxq')[0:4]
            njdm = request.POST.get('njdm')
            for info in njxszy_Tree:
                if info.get('bjh') and info.get('njdm') == njdm:
                    bjh_list.append(info['bjh'])

            context = {
                'login_info': str(login_info) + '<br>' + '节点：' + Pytyut.node_link,
                'xnxq': request.POST.get('xnxq'),
                'bjh_list': bjh_list,
            }
            return render(request, 'class_schedule_homepage.html', context=context)
    else:
        if request.GET.get('get') == 'start':
            # 2022/2/9 升级为pytyut
            # 循环遍历
            bjh_list2 = ['数科2004']  # 测试用，测试时只爬取这一个班级
            for bjh in bjh_list:
                print('正在爬取：【', bjh, '】')
                class_schedule_text = str(pytyut_user.get_class_schedule_by_bjh(xnxq=request.GET.get('xnxq'), bjh=bjh))
                # 判断爬取失败返回None的情况
                try_times = 0
                while not class_schedule_text:
                    print('爬取失败，5秒后重试...')
                    sleep(5)
                    class_schedule_text = str(pytyut_user.get_class_schedule_by_bjh(xnxq=request.GET.get('xnxq'), bjh=bjh))
                    try_times += 1
                    if try_times > 5:
                        print('正在尝试重新登录...')
                        pytyut_user.login()
                        class_schedule_text = str(pytyut_user.get_class_schedule_by_bjh(xnxq=request.GET.get('xnxq'), bjh=bjh))
                        break
                class_schedule_dict[bjh] = class_schedule_text
            context = {
                'class_schedule_dict': class_schedule_dict,
                'xnxq': request.GET.get('xnxq'),
            }
            return render(request, 'class_schedule_homepage.html', context=context)
        elif request.GET.get('get') == 'save':
            # 保存到数据库中
            xnxq = request.GET.get('xnxq')
            for key, value in class_schedule_dict.items():
                class_shchedule = Class_Schedule.objects.filter(s_bjh=key).first()
                if class_shchedule:
                    pass
                else:
                    class_shchedule = Class_Schedule()
                class_shchedule.s_bjh = key
                class_shchedule.s_xnxq = xnxq
                class_shchedule.s_schedule = value
                class_shchedule.save()
            return HttpResponse('<h1>写入数据库成功！<h1><a href=./>返回主页<a>')
        return render(request, 'class_schedule_homepage.html')


def convert(request):
    """
    根据云麓需求转换为0101的课程表信息
    0是没课，1是有课
    :param request:
    :return:
    """
    # 整体思路是先创建一个全都是无课的数据
    # 然后遍历课程表每一节课的信息，判断哪些地方有课并把它填充为1

    # 获取全部课程信息
    class_infos = Class_Schedule.objects.all()
    # 循环遍历每一个专业班级
    for class_info in class_infos:
        # 创建无课信息列表[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], ...]
        # 每一个列表代表一个week一共18周，每一串字符串代表每一周的20个大节
        class_week_list = [['0' for _ in range(20)] for _ in range(18)]
        # 开始遍历每一节课，并把有课的地方修改为1
        class_list = eval(class_info.s_schedule)['rows']
        for each_class in class_list:
            # 先判断是否是需要计算的课（有的课没写什么时候上课）
            if not each_class['Skjc']:
                # 如果没有什么时候上课的信息就跳过
                continue
            if each_class['Skxq'] > 5:
                # 如果上课星期大于5（也就是周末上课）就跳过
                continue
            if each_class['Skjc'] > 8:
                # 如果上课节次大于8（也就是晚自习的课）就跳过
                continue
            # 先计算在每一周中是哪几个地方需要把0改成1
            change_set = set([])
            jc_range = (int(each_class['Skjc']) + 1, int(each_class['Skjc'] + each_class['Cxjc']))
            change_set.add((each_class['Skxq'] - 1) * 4 + jc_range[0]//2 - 1)
            change_set.add((each_class['Skxq'] - 1) * 4 + jc_range[1]//2 - 1)
            # 再遍历上课周次，如果这周有课就把对应的那一周改了
            for i in range(18):
                if each_class['Skzc'][i] == '1':
                    for each_num in change_set:
                        class_week_list[i][each_num] = '1'

        # 创建云麓的数据库对象存储信息
        yunlu_schedule = yunlu_class_schedule()
        yunlu_schedule.bjh = class_info.s_bjh
        for i in range(18):
            # 使用exec指令就可以不用写18个赋值语句了
            exec(f'yunlu_schedule.week{i + 1} = "".join(class_week_list[{i}])')
        yunlu_schedule.save()
        # return HttpResponse(str(class_week_list))

    return HttpResponse('转换完成')

