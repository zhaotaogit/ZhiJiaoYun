# -*- coding = utf-8 -*-
# @Time : 2021/9/24 17:07
# @File : loginterst.py
# @Software: PyCharm
import random
import time
import requests
from PIL import Image
from matplotlib import pyplot as plt

null = None


def main():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
    }
    session = requests.session()
    session.headers = headers
    login_url = 'https://zjy2.icve.com.cn/api/common/login/login'
    with open('1.jpg', 'wb') as f:
        resp = session.get(url='https://zjy2.icve.com.cn/api/common/VerifyCode/index?t=' + str(random.random()))
        f.write(resp.content)
    img = Image.open('1.jpg')
    plt.figure()
    plt.imshow(img)
    plt.show()
    veri = input('请输入验证码:')
    veridata = {
        'userName': '20202030305',
        'userPwd': 'Zhaodeyu5',
        'verifyCode': veri
    }
    resplogin = session.post(url=login_url, data=veridata)
    print(resplogin.status_code)
    headers['Cookie'] = 'Hm_lvt_a3821194625da04fcd588112be734f5b=1637124660,1638336563; acw_tc=707c9fcf16383466785207068e3c6305f5aa7b0e1d96a5160b6edaf535d000; ASP.NET_SessionId=5u4dq0opas4lmdt300ikmhf4; verifycode=0A38229669C2FB363D11929A5AD98088@637739722788523764; Hm_lpvt_a3821194625da04fcd588112be734f5b=1638346657; auth=01024F942C1BA3B4D908FE4FA4D8ECF6B4D9080115760067006C00320061006E0073007000350035006300630074007300710034006700730070006900770000012F00FFA813D447A3A1BF8BDB76F58152BB8C37ABDE21D2; token=zkymafgtcyhmeypzn26ta'
    getLearnningCourseList = session.post(url='https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList',headers=headers)
    print(getLearnningCourseList.text)
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
    print(getProcessresp.json())
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
            print(getCellByTopicId.json())
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
                    'moduleId': i,
                }
                while True:
                    viewresp = session.post(url='https://zjy2.icve.com.cn/api/common/Directory/viewDirectory',
                                            data=viewDirectorydata)
                    print('---------------', end='')
                    print(viewresp.json())
                    print(viewresp.json()['code'])
                    if viewresp.json()['code'] == 1:
                        time.sleep(2)
                        print(1)
                        break
                    else:
                        changeStuStudyProcessCellData = {
                            'courseOpenId': courseList[courseNum]['courseOpenId'],
                            'openClassId': courseList[courseNum]['openClassId'],
                            'moduleId': i,
                            'cellId': z,
                            'cellName': viewresp.json()['currCellName']
                        }
                        changeStuStudyProcessCellresp = session.post(
                            url='https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData',
                            data=changeStuStudyProcessCellData)
                # print('*' * 50)
                # print(viewDirectorydata)
                # a = eval(viewresp.text.replace('false', 'False').replace('true', 'True'))
                # print(a)
                # print(a['guIdToken'])
                # print(type(a))
                token = viewresp.json()['guIdToken']
                # return
                print('*' * 50)
                # 判断是否已经看完
                if viewresp.json()['cellPercent'] == 100:
                    time.sleep(5)
                    continue
                # 判断是否是视频
                if viewresp.json()['categoryName'] == '视频':
                    audioVideoLong = viewresp.json()['audioVideoLong']
                    studyNewlyTime = viewresp.json()['stuStudyNewlyTime']
                    cellName = viewresp.json()['cellName']
                    while True:
                        studyNewlyTime = float(studyNewlyTime)
                        if audioVideoLong - studyNewlyTime > 10:
                            rt = random.random()
                            studyNewlyTime += rt
                            studyNewlyTime += 10
                            studyNewlyTime = format('%.6f' % (studyNewlyTime))
                            stuProcessCellLogurl = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'
                            stuProcessCellLogdata = {
                                'courseOpenId': courseList[courseNum]['courseOpenId'],
                                'openClassId': courseList[courseNum]['openClassId'],
                                'cellId': z,
                                'picNum': 0,
                                'studyNewlyTime': studyNewlyTime,
                                'studyNewlyPicNum': 0,
                                'token': token
                            }
                            resp1 = session.post(url=stuProcessCellLogurl, data=stuProcessCellLogdata)
                            if float(studyNewlyTime) >= audioVideoLong:
                                print(cellName + '\t\t\t\t此节已完成!')
                                break
                            print(cellName + '\t\t\t\t当前观看进度:' + str(studyNewlyTime) + ',' + '视频总长度' + str(
                                audioVideoLong))
                            print(resp1.text)
                            time.sleep(list(range(int(rt) + 11))[-1])
                        else:
                            stuProcessCellLogdata['studyNewlyTime'] = audioVideoLong
                            resp1 = session.post(url=stuProcessCellLogurl, data=stuProcessCellLogdata)
                            print(cellName + '\t\t\t\t当前观看进度:' + str(audioVideoLong) + ',' + '视频总长度' + str(
                                audioVideoLong))
                            print(resp1.json())
                            time.sleep(2)
                            break


if __name__ == '__main__':
    main()
