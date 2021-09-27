# -*- coding = utf-8 -*-
# @Time : 2021/9/23 13:13
# @File : 职教云.py
# @Software: PyCharm
import requests
from lxml import etree
from selenium.webdriver import Chrome
import time
from PIL import Image
from matplotlib import pyplot as plt


def main(username, password):
    web = Chrome()
    web.get('https://zjy2.icve.com.cn/')
    web.find_element_by_xpath('//*[@id="login-tabs"]/div/div[1]/div/div[1]/div/input').send_keys(username)
    web.find_element_by_xpath('//*[@id="x-modify"]/div/input[1]').send_keys(password)
    # web.find_element_by_xpath('//*[@id="x-modify"]/div/img[2]').screenshot_as_png
    veri_img = web.find_element_by_xpath('//*[@id="x-modify"]/div/img[2]').screenshot_as_png  # 将验证码区域保存为png图片
    with open('1.jpg', 'wb') as f:
        f.write(veri_img)
    img = Image.open('1.jpg')
    plt.figure()
    plt.imshow(img)
    plt.show()
    veri = input('请输入验证码:')
    web.find_element_by_xpath('//*[@id="x-modify"]/div/input[2]').send_keys(veri)
    web.find_element_by_xpath(
        '/html/body/div[2]/div/div[1]/div/div[1]/div/div[1]/div[1]/div/div/div/div[1]/div/div[4]/a').click()
    # time.sleep(20)
    time.sleep(1)
    web.get(
        'https://zjy2.icve.com.cn/study/process/process.html?courseOpenId=uk6cagcrbzpgy77ie3rpjg&openClassId=jhrpaastrpaugbcqmvbya')
    page = web.page_source
    # print(page)
    # web.close()
    html = etree.HTML(page)
    data_moduleids = html.xpath('//*[@id="process_container"]/div')
    lst = []
    for i in data_moduleids:
        lst.append(i.xpath('./@data-moduleid')[0])
    # print(lst)

    # 生成每一单元字典
    dit = {}
    for i in lst:
        dit[i] = {}

    # 获取每一单元的小节信息
    for i in lst:
        url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'Cookie': 'acw_tc=2f624a1116325529291992714e03c0e9b4c36a2a6a0f9a39b63403af4e0312; verifycode=D2693F4EF2333F786392DB7548937061@637681785295096502; Hm_lvt_a3821194625da04fcd588112be734f5b=1632552927; Hm_lpvt_a3821194625da04fcd588112be734f5b=1632552927; auth=01025307E877F17FD908FE531794494580D9080115740067006C00320061006E00730030006C0066006800720070007600660062007200760076006200710000012F00FFB20D01B468CE2F77AAB9AE2E6AAFBB6697244302; token=zpf1ak6t4jtffpwn6snr1a'
        }
        data = {
            'courseOpenId': 'uk6cagcrbzpgy77ie3rpjg',
            'moduleId': i
        }
        resp = requests.post(url=url, headers=headers, data=data)
        for j in resp.json()['topicList']:
            # print(j)
            dit[i][j['id']] = []
            url1 = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'
            data = {
                'courseOpenId': 'uk6cagcrbzpgy77ie3rpjg',
                'openClassId': 'jhrpaastrpaugbcqmvbya',
                'topicId': j['id']
            }
            # print(j['id'])
            resp1 = requests.post(url=url1, headers=headers, data=data)
            for z in resp1.json()['cellList']:
                if z['categoryName'] != "视频":
                    continue
                dit[i][j['id']].append(z['Id'])
    print(dit)
    print('*' * 50)
    url_list = []
    for i in dit:
        for j in dit[i]:
            for z in dit[i][j]:
                url = ''
                url_list.append(
                    'https://zjy2.icve.com.cn/common/directory/directory.html?courseOpenId=uk6cagcrbzpgy77ie3rpjg&openClassId=jhrpaastrpaugbcqmvbya&cellId=' + z + '&flag=s&moduleId=' + i)

    for i in url_list:
        web.get(i)
        t = 1
        while t <= 20:
            try:
                time1 = web.find_element_by_xpath(
                    '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/span').text
                time2 = web.find_element_by_xpath(
                    '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[3]/span').text
                if time2 == '00:00':
                    raise '123'
                start = time.time()
                break
            except Exception as e:
                time.sleep(3)
                try:
                    web.find_element_by_xpath(
                        '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/div[1]').click()
                    web.find_element_by_xpath(
                        '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/div[1]').click()
                except:
                    pass
                t += 1
                print(f'第{t}次检测视频视频是否已开始正常播放!')
                time.sleep(1)
                if t >= 20:
                    web.refresh()
                    t = 1
        # 计算视频总秒数
        s = int(time2.split(':')[0]) * 60 + int(time2.split(':')[1])
        print(s)
        # 判断当前播放的视频是否已经播放完
        a = int(time1.split(':')[0]) * 60 + int(time1.split(':')[1])
        b = int(time2.split(':')[0]) * 60 + int(time2.split(':')[1])
        if a >= b and time2 != '00:00':
            continue
        up = time1
        time.sleep(2)
        # 不断获取进度条时间，判断是否已播放完或卡住
        while True:
            try:
                time1 = web.find_element_by_xpath(
                    '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/span').text
                a = int(time1.split(':')[0]) * 60 + int(time1.split(':')[1])
            except Exception as e:
                print('正在检测视频播放进度条!')
                time.sleep(1)
                continue
            if up == a:
                web.refresh()
                print('视频可能卡住!正在尝试刷新!')
                try:
                    web.find_element_by_xpath(
                        '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/div[1]').click()
                    web.find_element_by_xpath(
                        '/html/body/div/div[3]/div/div/div[1]/div/div/div[7]/div[3]/div[1]/div[1]').click()
                except:
                    pass
                time.sleep(10)
            if a >= b:
                break
            up = a
            time.sleep(2)


if __name__ == '__main__':
    main('用户名', '密码')
