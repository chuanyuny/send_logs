#-*- coding:utf-8 -*-
import json
import IP
import time
import requests
import random
import IP
import csv
from math import ceil
from multiprocessing import Pool
import os

global tiaoshu
tiaoshu=0

def read_json(path): 
    '''主要是为了读取ip_agent.csv文件，之所以把读取ip_agent.csv改成读取ip_agent.json是因为前者太慢了。'''
    fr=open(path,'r')
    aa=json.load(fr)
    fr.close()
    return aa #是dict类型

IPAGENT=read_json('ip_agent.json')  #dict

def open_txt(path):
    '''打开一个文本文档，返回文档内容列表'''
    fo=open(path,'r')
    content=fo.readlines()
    lenth=len(content)
    for i in range(lenth):
        content[i]=content[i].replace('\n','')
    fo.close()
    return content  #list

def read_json(path): 
    '''主要是为了读取ip_agent.csv文件，之所以把读取ip_agent.csv改成读取ip_agent.json是因为前者太慢了。'''
    fr=open(path,'r')
    aa=json.load(fr)
    fr.close()
    return aa #是dict类型

def return_dict(str): #传入的可以是province也可以是time_weight  是[{"name":"北京","level":"12"},{"name":"上海","level":"11"}] 这种格式的
    temp_dict={}

    for item in str:
        key=item.values()[0]
        value=item.values()[1]
        if value is not "": 
            temp_dict[key]=value
        else:
            temp_dict[key]='1'   #如果权重值为空，则设置默认权重为1

    return temp_dict  #返回的是字典是 {"北京":"12","上海":"13"} 这种格式的

def province_weight_sum(province):   #读入一个［{},{},{}］这种格式的province_weight json数据
    province_sum=0
    for each in province:
        if each['level'] is not "":
            province_sum=province_sum+float(each['level'])
        else:
            province_sum=province_sum+float('1')  #如果权重值为空，则设置默认权重为1

    return province_sum

def time_weight_sum(time_weight):   #读入一个［{},{},{}］这种格式的province_weight json数据
    time_sum=0
    for each in time_weight:
        if each['time'] is not "":
            time_sum=time_sum+float(each['time'])
        else:
            time_sum=time_sum+float('1') #如果权重值为空，则设置默认权重为1

    return time_sum


def get_all_ip(number,stime,time_weight,province):
    '''number为24小时内一共要发送多少次'''
    st1=time.time()
    all_ip=[]   #某个小时内应该发送的所有IP存在这个list中
    temp_dict=return_dict(time_weight)
    time_dict={}
    for each_key in temp_dict:
        time_dict[each_key.split(":")[0]]=temp_dict[each_key]
    one_hour_number=number*(float(time_dict[stime])/time_weight_sum(time_weight))  #此时的number为H这个小时内一共应该发送的请求数，返回结果是float类型的

    province_dict=return_dict(province)
    
    for each in province_dict:
        one_province_all_ip=open_txt(each+'.txt')  #得到一个省的所有ip,未经过权重处理,返回list
        one_province_weight=float(province_dict[each])   #得到一个省的对应的权重，int
        one_t_p_count=int(ceil(one_hour_number*one_province_weight/province_weight_sum(province))) #在一个确定的时间内，一个省应该发送的次数，时间权重后的数乘以地区权重。
        one_p_w_ip=[]  #一个省的经过时间和地区权重处理的所有ip
        try:
            one_p_w_ip=random.sample(one_province_all_ip,one_t_p_count)
        except:
            for i in range(one_t_p_count):
                one_p_w_ip.append(random.choice(one_province_all_ip))
        finally:
            all_ip=all_ip+one_p_w_ip
    sd1=time.time()
    print "get all ip 所需的时间是： %s 秒"%(sd1-st1)
    return all_ip #list，一个小时内应该发送的所有ip数

def get_one_ip(all_ip):
    return random.choice(all_ip) #返回一个ip,str类型

def get_user_agent(one_ip):
    
    user_agent=""
    try:
        user_agent=random.choice(IPAGENT[one_ip])
    except:
        print "ip_agent.json中没有相关ip" 
    return user_agent #返回的是一个useragent，str

def send_request(url,ip,user_agent):
    headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'X-Forwarded-For':ip,
    'User-Agent': user_agent
    }
    resp=requests.get(url,headers)
    
def write_json(path,content):
    f=open(path,'w')
    json.dump(content,f,ensure_ascii=False)
    f.close()

def run(url,number,province,time_weight):
    global tiaoshu
    start_time=time.strftime("%H")  # 时，str类型
    flag=0 #0表示之前没有执行过，1表示之前已经执行过
    equipment_PV={'iPhone':0,'Macintosh':0,'Android':0,'Windows NT':0,'Windows Phone':0,'Symbian':0}
    
    ip_header=[]  #存放所有的ip加agent

    while(True):
        if time.strftime("%H")==start_time and flag==0:
            equipment_UV={'iPhone':0,'Macintosh':0,'Android':0,'Windows NT':0,'Windows Phone':0,'Symbian':0}
            all_ip=get_all_ip(number,start_time,time_weight,province)  #list
            all_agent=[]
            
            st4=time.time()
            print "1111"
            p=Pool(5)
            for i in range(len(all_ip)):

                ip=get_one_ip(all_ip)        #得到一个ip
                user_agent=get_user_agent(ip)   #得到一个user_agent
                all_agent.append(user_agent)
                ip_header.append(ip+user_agent)
                p.apply_async(send_request,args=(url,ip,user_agent))
                tiaoshu=tiaoshu+1
            print '222'
            p.close()
            print '444'
            p.join()
            print '333'
            sd4=time.time()
            print "发送所有请求所需的时间：%s 秒"%(sd4-st4)

            print "所有的useragent数量是%d"%(len(all_agent))
            #所有设备的pv值
            for each in all_agent:
                for item in equipment_PV:
                    if item in each:
                        equipment_PV[item]=equipment_PV[item]+1
            write_json("equipment_pv.json",equipment_PV)

            #s所有设备的UV值
            only_ip_header_list=list(set(ip_header))  #存放不重复的ip+agent
            print "去重后，ip+useragent的数量是 %d"%(len(only_ip_header_list))
            
            for each in only_ip_header_list:
                for item in equipment_UV:
                    if item in each:
                        equipment_UV[item]=equipment_UV[item]+1
            write_json("equipment_uv.json",equipment_UV)


            #把每次要发送的各省多少条数写道一个json文件中
            dict2={}
            for each in all_ip:
                name=(IP.find(each).encode("utf8").split())[1]
                if name in dict2.keys():
                    dict2[name]=dict2[name]+1
                else:
                    dict2[name]=1
            

            aa=time.strftime('%H')
            write_json(aa+'.json',dict2)  #每个小时发送的各省的ip条数

            try:
                fo=open('province_total.json','r')  #读取一个json文件
                temp_dict=json.load(fo)  #temp_dict是unicode编码
                fo.close()

                temp_dict2={}
                for i in temp_dict:
                    temp_dict2[i.encode('utf8')]=temp_dict[i] #使temp_dict2的keys是utf8编码

                for each in all_ip:
                    name=(IP.find(each).encode("utf8").split())[1]  #此处的name是utf8编码
                    if name in temp_dict2:
                        temp_dict2[name]=temp_dict2[name]+1
                    else:
                        temp_dict2[name]=1   #province_total_dict的keys是utf8编码
                
                write_json('province_total.json',temp_dict2)
            except:
                write_json('province_total.json',dict2)
                

            flag=1
        elif time.strftime("%H")==start_time:
            pass
        else:
            print "ooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
            start_time=time.strftime("%H")
            flag=0

if __name__=="__main__":
    global tiaoshu
    url="http://139.217.9.208"
    number=81600 #24小时一共发送的条数
    province=[
    {
        "name":"北京",
        "level":"1.5"
    },
    {
        "name":"上海",
        "level":"0.5"
    },
    {
        "name":"天津",
        "level":"1.2"
    },
    {
        "name":"重庆",
        "level":"0.8"
    },
    {
        "name":"黑龙江",
        "level":"0.3"
    },
    {
        "name":"吉林",
        "level":"1.7"
    },
    {
        "name":"辽宁",
        "level":"1"
    },
    {
        "name":"江苏",
        "level":"1"
    },
    {
        "name":"山东",
        "level":"1"
    },
    {
        "name":"安徽",
        "level":"1"
    },
    {
        "name":"河北",
        "level":"1"
    },
    {
        "name":"河南",
        "level":"1"
    },
    {
        "name":"湖北",
        "level":"1"
    },
    {
        "name":"湖南",
        "level":"1"
    },
    {
        "name":"江西",
        "level":"1"
    },
    {
        "name":"陕西",
        "level":"1"
    },
    {
        "name":"山西",
        "level":"1"
    },
    {
        "name":"四川",
        "level":"1"
    },
    {
        "name":"青海",
        "level":"1"
    },
    {
        "name":"海南",
        "level":"1"
    },
    {
        "name":"广东",
        "level":"1"
    },
    {
        "name":"贵州",
        "level":"1"
    },
    {
        "name":"浙江",
        "level":"1"
    },
    {
        "name":"福建",
        "level":"1"
    },
    {
        "name":"台湾",
        "level":"1"
    },
    {
        "name":"甘肃",
        "level":"1"
    },
    {
        "name":"云南",
        "level":"1"
    },
    {
        "name":"内蒙古",
        "level":"1"
    },
    {
        "name":"宁夏",
        "level":"1"
    },
    {
        "name":"新疆",
        "level":"1"
    },
    {
        "name":"西藏",
        "level":"1"
    },
    {
        "name":"广西",
        "level":"1"
    },
    {
        "name":"香港",
        "level":"1"
    },
    {
        "name":"澳门",
        "level":"1"
    }
]

    time_weight=[
    {
        "name":"00:00-00:59",
        "time":"1"
    },
    {
        "name":"01:00-01:59",
        "time":"1"
    },
    {
        "name":"02:00-02:59",
        "time":"1"
    },
    {
        "name":"03:00-03:59",
        "time":"1"
    },
    {
        "name":"04:00-04:59",
        "time":"1"
    },
    {
        "name":"05:00-05:59",
        "time":"1"
    },
    {
        "name":"06:00-06:59",
        "time":"1"
    },
    {
        "name":"07:00-07:59",
        "time":"1"
    },
    {
        "name":"08:00-08:59",
        "time":"1"
    },
    {
        "name":"09:00-09:59",
        "time":"1"
    },
    {
        "name":"10:00-10:59",
        "time":"1"
    },
    {
        "name":"11:00-11:59",
        "time":"1"
    },
    {
        "name":"12:00-12:59",
        "time":"1"
    },
    {
        "name":"13:00-13:59",
        "time":"1"
    },
    {
        "name":"14:00-14:59",
        "time":"1"
    },
    {
        "name":"15:00-15:59",
        "time":"1"
    },
    {
        "name":"16:00-16:59",
        "time":"1"
    },
    {
        "name":"17:00-17:59",
        "time":"1"
    },
    {
        "name":"18:00-18:59",
        "time":"1"
    },
    {
        "name":"19:00-19:59",
        "time":"1"
    },
    {
        "name":"20:00-20:59",
        "time":"1"
    },
    {
        "name":"21:00-21:59",
        "time":"1"
    },
    {
        "name":"22:00-22:59",
        "time":"1"
    },
    {
        "name":"23:00-23:59",
        "time":"1"
    }
]
    std=time.time()
    run(url,number,province,time_weight)
    ed=time.time()
    print "在 %0.2f 秒内，一共发送了 %d 条"%((ed-std),tiaoshu)

        

    



















