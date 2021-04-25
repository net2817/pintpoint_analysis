# -*- coding: utf-8 -*-

# noinspection PyInterpreter,PyInterpreter

import sys
import requests
import time
import datetime
import json
import numpy as np

sys.path.append('../Golf')
import db #db.py

PPURL = "http://pinpoint.weixing-tech.com/"


From_Time = datetime.datetime.now() + datetime.timedelta(seconds=-60)
To_Time = datetime.datetime.now()
From_TimeStamp = int(time.mktime(From_Time.timetuple()))*1000
To_TimeStamp = int(time.mktime(datetime.datetime.now().timetuple()))*1000


class PinPoint(object):
    """docstring for PinPoint"""
    def __init__(self, db):
        self.db = db
        super(PinPoint, self).__init__()

    """获取pinpoint中应用"""
    def get_applications(self):
        '''return application dict
        '''
        applicationListUrl = PPURL + "/applications.pinpoint"
        res = requests.get(applicationListUrl)
        if res.status_code != 200:
            print("请求异常,请检查")
            return
        applicationLists = []
        for app in res.json():
            applicationLists.append(app)
        applicationListDict={}
        applicationListDict["applicationList"] = applicationLists
        return applicationListDict
    def getAgentList(self, appname):
        AgentListUrl = PPURL + "/getAgentList.pinpoint"
        param = {
            'application':appname
        }
        res = requests.get(AgentListUrl, params=param)
        if res.status_code != 200:
            print("请求异常,请检查")
            return
        return len(res.json().keys()),json.dumps(list(res.json().keys()))

    def update_servermap(self, appname, from_time=From_TimeStamp,
                         to_time=To_TimeStamp):
        '''更新app上下游关系
        :param appname: 应用名称
        :param from_time: 起始时间
        :param to_time: 终止时间
        :
        '''
        #https://pinpoint.*****.com/getServerMapData.pinpoint?applicationName=test-app&from=1547721493000&to=1547721553000&callerRange=1&calleeRange=1&serviceTypeName=TOMCAT&_=1547720614229
        #http://pinpoint.weixing-tech.com/getScatterData.pinpoint?application=daimler-manage-admin-pro&from=1618992044000&to=1618992104000&limit=5000&filter=&xGroupUnit=130&yGroupUnit=0&backwardDirection=true
        param = {
            'application':appname,
            'from':from_time,
            'to':to_time,
            'limit':5000,
            'filter':'',
            'xGroupUnit':130,
            'yGroupUnit':0,
            'backwardDirection':'true'
        }

        # serverMapUrl = PPURL + "/getScatterData.pinpoint"
        serverMapUrl = "{}{}".format(PPURL, "/getScatterData.pinpoint")
        res = requests.get(serverMapUrl, params=param)
        if res.status_code != 200:
            print("请求异常,请检查")
            return
        timetemp = float(from_time/1000)
        time_local = time.localtime(timetemp)
        update_time = time.strftime('%Y-%m-%d %H:%M:%S',time_local)
        time_analysis_list = []
        time_analysis_error = []
        links = res.json()["scatter"]["dotList"]
        for link in links :
            #时间戳，应用名，总请求数，错误请求数，中位数，平均数，95值（每分钟一次定时任务）
            time_analysis_list.append(link[1])
            time_analysis_error.append(link[4])
        if len(time_analysis_list) != 0:
            totalcount = int(len(time_analysis_list))
            errorcount = time_analysis_error.count(0)
            median = round(np.percentile(time_analysis_list,50))
            average = round(sum(time_analysis_list)/len(time_analysis_list))
            distribution95 = round(np.percentile(time_analysis_list,95))
        else:
            totalcount = 0
            errorcount = 0
            median = 0
            average = 0
            distribution95 = 0

        sql = """
    REPLACE into time_analysis( datetime, application_name, totalcount,errorcount, median, average, distribution95)
    VALUES ("{}", "{}", {}, {}, {}, {}, {});""".format(update_time,appname,totalcount,errorcount,median,average,distribution95)
        self.db.db_execute(sql)

    def update_app(self):
        """更新application
        """
        appdict = self.get_applications()
        apps = appdict.get("applicationList")
        update_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        for app in apps:
            if app['applicationName'].startswith('test'):
                continue
            agents, agentlists = self.getAgentList(app['applicationName'])
            sql = """
    REPLACE into application_list( application_name, 
    service_type, code, agents, agentlists, update_time) 
    VALUES ("{}", "{}", {}, {}, '{}', "{}");""".format(
                app['applicationName'], app['serviceType'],
                app['code'], agents, agentlists, update_time)
            self.db.db_execute(sql)
        return True

    def update_all_servermaps(self):
        """更新所有应用数
        """
        appdict = self.get_applications()
        apps = appdict.get("applicationList")
        for app in apps:
            self.update_servermap(app['applicationName'])
        ###删除3600天前数据
        Del_Time = datetime.datetime.now() + datetime.timedelta(days=-3600)

        sql = """delete from application_server_map where update_time <= "{}"
  """.format(Del_Time)
        self.db.db_execute(sql)
        return True


def connect_db():
    """ 建立SQL连接
    """
    mydb = db.MyDB(
        host="rm-bp149403qep6s9wt8.mysql.rds.aliyuncs.com",
        user="root",
        passwd="Weixing@1818",
        db="pp_analysis"
    )
    mydb.db_connect()
    mydb.db_cursor()
    return mydb

def main():
    db = connect_db()
    pp = PinPoint(db)
    pp.update_app()
    pp.update_all_servermaps()
    db.db_close()


if __name__ == '__main__':
    main()