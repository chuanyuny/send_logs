#-*- coding:utf-8 -*-
import json
import IP
import random
import requests
import datetime

'''在某一时刻发送给某个省某个设备多少条请求'''
def open_txt(path):
    '''打开一个文本文档，返回文档内容列表'''
    fo=open(path,'r')
    content=fo.readlines()
    lenth=len(content)
    for i in range(lenth):
        content[i]=content[i].replace('\n','')
    fo.close()
    return content  #list

def send_request(url,ip,user_agent):
    headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'X-Forwarded-For':ip,
    'User-Agent': user_agent
    }
    resp=requests.get(url,headers)  

def get_agent(ldevice):
	agents=[]
	all_agent=open_txt("useragent.txt")
	for each in all_agent:
		if ldevice[0] in each:
			agents.append(each)
	return agents #获取所有的包涵mac的agent


def run2(url,lnumber,lprovince,ldevice):
	starttime=datetime.datetime.now() #开始时间
	ips=open_txt(lprovince[0]+'.txt')
	agents=get_agent(ldevice[0])
	
	count=0
	for i in range(lnumber):
		ip=random.choice(ips)
		agent=random.choice(agents)
		send_request(url,ip,agent)
		print count,ip,IP.find(ip).split()[1],agent
		count=count+1

	print "%s:%d",(lprovince[0],count)
	endtime=datetime.datetime.now()
	print "运行时间是：%s秒"%(endtime-starttime).seconds

    

if __name__=="__main__":
	url="http://10.169.70.240"
	lnumber=100
	lprovince=["北京"]
	ldevice=["mac"]
	run2(url,lnumber,lprovince,ldevice)









