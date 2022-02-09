from django.http import HttpResponse
from django.shortcuts import render
from time import sleep
# Create your views here.
import requests
from pytyut import Pytyut
# 创建会话对象（方便使用的全局变量）
from app.models import Class_Schedule
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

