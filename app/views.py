from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
import requests

# 创建会话对象（方便使用的全局变量）
from app.models import Class_Schedule

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66',
}
login_1_url = 'http://jxgl1.tyut.edu.cn/'
bjh_list = []
class_schedule_dict = {}


def main_page(request):
    global login_1_url
    global bjh_list
    global class_schedule_dict
    if request.method == 'POST':
        # 判断是否为登录操作
        if request.POST.get('userid'):
            username = request.POST.get('userid')
            password = request.POST.get('password')

            # 2021/07/02 “测速选取“功能
            # 根据timeout参数进行测试，确定最稳定的连接
            print("正在获取最快速的连接，请稍后。。。")
            login_1_url = 'http://jxgl1.tyut.edu.cn/'
            try:
                print("正在测试学生通道1。。。")
                requests.get(login_1_url, timeout=5)
            except:
                print("正在测试学生通道2.。。")
                login_1_url = 'http://jxgl2.tyut.edu.cn/'
                try:
                    requests.get(login_1_url, timeout=5)
                except:
                    print("正在测试太理同学的反代。。。")
                    login_1_url = 'https://jxgl20201105.tyutmate.cn/'
                    try:
                        res_tyut_mate = requests.get(login_1_url, timeout=10)
                        if res_tyut_mate.status_code != 200:
                            print("太理同学服务器错误！请避免高峰期访问！", res_tyut_mate.status_code)
                            exit(1)
                    except:
                        print("所有节点均无响应，请检查网络！")
                        exit(1)

            print("选择到节点：", login_1_url)
            login_2_url = login_1_url + 'Login/CheckLogin'
            # 创建会话，获取ASP.NET_SessionId的Cookies
            session.get(login_1_url, headers=headers)
            # 模拟登录请求
            data = {
                'username': RSA_username(username),
                'password': password,
                'code': '',
                'isautologin': 0,
            }
            headers_check_login = {
                'Accept': 'application / json, text / javascript, * / *; q = 0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': login_1_url,
                'Referer': login_1_url,
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            }
            login_res = session.post(url=login_2_url, data=data, headers=headers_check_login)
            login_info = login_res.text
            # 获取专业班级（bjh）列表
            get_njxszy_Tree_url = login_1_url + 'Tschedule/Zhcx/GetNjxszyTreeByrwbjJson'
            data = {
                'zxjxjhh': request.POST.get('xnxq')
            }
            njxszy_Tree = session.post(url=get_njxszy_Tree_url, data=data, headers=headers_check_login)
            # 结果Json化处理
            njxszy_Tree = njxszy_Tree.json()
            # 遍历，把所有bjh信息放在一个list里
            # 筛选出当前年级的条件
            njdm = request.POST.get('xnxq')[0:4]
            for info in njxszy_Tree:
                if info.get('bjh') and info.get('njdm') == njdm:
                    bjh_list.append(info['bjh'])

            context = {
                'login_info': login_info + '<br>' + '节点：' + login_1_url,
                'xnxq': request.POST.get('xnxq'),
                'bjh_list': bjh_list,
            }
            return render(request, 'class_schedule_homepage.html', context=context)
    else:
        if request.GET.get('get') == 'start':
            login_1_url = login_1_url
            headers_check_login = {
                'Accept': 'application / json, text / javascript, * / *; q = 0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.101 Safari/537.36 Edg/91.0.864.48',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': login_1_url,
                'Referer': login_1_url,
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            }
            # 发送请求的地址
            class_url = login_1_url + 'Tschedule/Zhcx/GetSjjsSjddByBjh'
            # 循环遍历
            # bjh_list2 = ['数科2004']   测试用，测试时只爬取这一个班级
            for bjh in bjh_list:
                print('正在爬取：【', bjh, '】')
                class_data = {
                    'zxjxjhh': request.GET.get('xnxq'),  # 好像跟学年还有学期有关系
                    'bjh': bjh,  # 这里填写专业班级简称信息
                }
                req_data = {
                    'pagination[conditionJson]': str(class_data),
                    'pagination[sort]': 'xsh,kch',
                    'pagination[order]': 'asc',
                }

                class_res = session.post(url=class_url, data=req_data, headers=headers_check_login)
                if '处理你的请求时出错。' in class_res.text:
                    print('爬取出错，正在重试。。。')
                    class_res = session.post(url=class_url, data=req_data, headers=headers_check_login)
                class_schedule_dict[bjh] = class_res.text
            context = {
                'class_schedule_dict': class_schedule_dict,
                'xnxq': class_data['zxjxjhh'],
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


# RSA 公钥加密，用于登录教务系统处理用户名信息
def RSA_username(username):
    import base64
    # 这里有可能出现导包导不进去的问题，把site-packages里面的crypto文件夹改为大写Crypto即可
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    # 公钥在页面里面
    key = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCoZG+2JfvUXe2P19IJfjH+iLmp
VSBX7ErSKnN2rx40EekJ4HEmQpa+vZ76PkHa+5b8L5eTHmT4gFVSukaqwoDjVAVR
TufRBzy0ghfFUMfOZ8WluH42luJlEtbv9/dMqixikUrd3H7llf79QIb3gRhIIZT8
TcpN6LUbX8noVcBKuwIDAQAB
-----END PUBLIC KEY-----
    '''
    rsakey = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(username.encode(encoding='utf-8')))
    value = cipher_text.decode('utf-8')
    return value
