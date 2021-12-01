# -*- coding = utf-8 -*-
# @Time : 2021/9/24 17:07
# @File : loginterst.py
# @Software: PyCharm
import random
import time

import requests
from PIL import Image
from matplotlib import pyplot as plt


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
    }
    session = requests.session()
    url = 'https://zjy2.icve.com.cn/api/common/login/login'
    with open('1.jpg', 'wb') as f:
        resp = session.get(url='https://zjy2.icve.com.cn/api/common/VerifyCode/index?t=' + str(random.random()))
        f.write(resp.content)
    img = Image.open('1.jpg')
    plt.figure()
    plt.imshow(img)
    plt.show()
    veri = input('请输入验证码:')
    # session.headers = headers
    veridata = {
        'userName': 'Gerahy',
        'userPwd': 'wang666!',
        'verifyCode': veri
    }
    resplogin = session.post(url='https://zjy2.icve.com.cn/api/common/login/login', data=veridata, headers=headers,
                             cookies=resp.cookies)
    cookies = resplogin.cookies
    getLearnningCourseList = session.post(url='https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList',
                                          cookies=cookies)
    print(getLearnningCourseList.text)
    print(getLearnningCourseList.json()['courseList'])
    courseList = []
    for i in getLearnningCourseList.json()['courseList']:
        courseList.append(
            {'courseOpenId': i['courseOpenId'], 'courseName': i['courseName'],
             'assistTeacherName': i['assistTeacherName'],
             'openClassId': i['openClassId']})
    print(courseList)
    n = 1
    for i in courseList:
        print("编号:%-10s课程名:%-30s教师名称:%-10s" % (n, i['courseName'], i['assistTeacherName']))
        n += 1
    courseNum = int(input('请输入你要刷课的编号：')) - 1

    # 获取课程单元信息
    getProcessurl = 'https://zjy2.icve.com.cn/api/study/process/getProcessList'
    data1 = {
        'courseOpenId': courseList[courseNum]['courseOpenId'],
        'openClassId': courseList[courseNum]['openClassId']
    }
    getProcessresp = session.post(url=getProcessurl, data=data1)
    print(getProcessresp.json()['progress']['moduleList'])
    data2 = {
        'courseOpenId': courseList[courseNum]['courseOpenId'],
        'moduleId': ''
    }
    dit = {}
    for i in getProcessresp.json()['progress']['moduleList']:
        data2['moduleId'] = i['id']
        dit[i['id']] = {}
        getTopicByModuleId = session.post(url='https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId',
                                          data=data2)
        for j in getTopicByModuleId.json()['topicList']:
            dit[i['id']][j['id']] = []
            data1['topicId'] = j['id']
            getCellByTopicId = session.post(url='https://zjy2.icve.com.cn/api/study/process/getCellByTopicId',
                                            data=data1)
            # print(getTopicByModuleId.json())
            for z in getCellByTopicId.json()['cellList']:
                dit[i['id']][j['id']].append(z['Id'])
    print(dit)
    for i in dit:
        for j in dit[i]:
            for z in dit[i][j]:
                viewDirectorydata = {
                    'courseOpenId': courseList[courseNum]['courseOpenId'],
                    'openClassId': courseList[courseNum]['openClassId'],
                    'cellId': z,
                    'flag': 's',
                    'moduleId': z,
                }
                viewresp = session.post(url='https://zjy2.icve.com.cn/api/common/Directory/viewDirectory',
                                        data=viewDirectorydata)

                # token = viewresp.json()['guIdToken']
                print(viewresp.json())
                return
                # 判断是否已经看完
                if viewresp.json()['cellPercent'] == 100:
                    time.sleep(15)
                    continue
                # 判断是否是视频
                if viewresp.json()['categoryName'] == '视频':
                    audioVideoLong = viewresp.json()['audioVideoLong']
                    stuStudyNewlyTime = viewresp.json()['stuStudyNewlyTime']
                    while True:
                        stuProcessCellLogurl = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'
                        stuProcessCellLogdata = {
                            'courseOpenId': courseList[courseNum]['courseOpenId'],
                            'openClassId': courseList[courseNum]['openClassId'],
                            'cellId': z,
                            'picNum': 0,
                            'studyNewlyTime': stuStudyNewlyTime,
                            'studyNewlyPicNum': 0,
                            'token': token
                        }
                        resp1 = session.post(url=stuProcessCellLogurl, data=stuProcessCellLogdata)
                        if float(stuStudyNewlyTime) >= audioVideoLong:
                            break
                        print(resp1.text)
                        t = format('%.6f' % (random.random() + 10))
                        t1 = float(t)
                        print('当前观看进度:' + str(stuStudyNewlyTime) + ',' + '视频总长度' + str(audioVideoLong))
                        stuStudyNewlyTime = format('%.6f' % (float(stuStudyNewlyTime) + t1))
                        time.sleep(t1 + 1)


if __name__ == '__main__':
    main()
