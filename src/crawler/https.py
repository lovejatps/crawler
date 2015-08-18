#!/usr/bin/env python
#coding=utf-8

import urllib2 ,sys
from bs4 import  BeautifulSoup
from json import *
from bson.objectid import ObjectId
import pymongo 
import __main__
from __builtin__ import str
from test.test_socket import try_address

reload(sys)
sys.setdefaultencoding('utf8')

# page = urllib2.urlopen('http://album.ximalaya.com/').read()
# 
# soup = BeautifulSoup(page)
#soup =  soup.prettify('utf-8')
# print soup.decode('utf-8')

# print soup.title
#print soup.haed

# print soup.name
# print soup.head.name
# 
# 
# print soup.find_all('ul','sort_list').countents[0]

# for i in soup.body.find_all('ul','sort_list'):
#     print i

#li = soup.find('ul','sort_list')
#divli = li.find('div')
#print li
# licon =str(li.find_next('li'))
# print licon
#soup_t = BeautifulSoup(li)

########## 顶级类-->细类-->节目[节目信息]-->音频信息及下载地址

def connectDB():
    try:
        client = pymongo.MongoClient("mongodb://192.168.102.154:27017")
        db = client.radio   #创建 radio 数据库
        return db
    except Exception, e:
        print 'Mongodb连接错误',e
        connectDB()


###############存储分类
def serversort(jsondata,types):
    db = connectDB()
    if types == 0:
        result = db.heading.insert(jsondata)   #顶级分类
    else:
        result = db.subclass.insert(jsondata)  #细类



def getPage(url):          ####################获取页面
    try:
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        return soup
    except Exception, e:
        print '服务器错误' ,e
        return None


def getclassify(url):           ####################获取分类
    soup = getPage(url)
    if None != soup:
        li = soup.find('ul','sort_list')
        heading=[]
        sunnames = []
        for i in li.find_all('li'):
           cid =  i['cid']
           url =  i.a['href']
           name = i.a.text
           limap ={'cid':cid,'url':url,'name':name,"_id":ObjectId()}
           heading.append(limap)
        
        # for heads in heading:
        #     print heads.get('cid')
              
        divli = li.find('div','tag_wrap')
        for d in divli.find_all('div'):   
            datacache = d['data-cache']
            for subs in d.find_all('a'):
                suburl = subs['href']
                sunName = subs.text
                sunmaps = {'suburl':suburl,'sunName':sunName,'datacache':datacache,"_id":ObjectId()}
                sunnames.append(sunmaps)
        return heading, sunnames
    else:
        return heading,sunnames

def getpagenumber(soup):  #####################获取总页数
    try:
        page = soup.find('div','pagingBar_wrapper')
        if None == page:
            return '1'
        a = 0
        if None != page.find_all('text','下一页'):
            pages = []
            for i in page.find_all('a'):
                p = i.text
                a = a + 1
                pages.append(p)
                if '下一页' == p:
                    a = a -1
                    break;
            return str(pages[a-1])
        else:
            return '1'
    except Exception, e:
        print '获取总页数错误',e


def getclassifyList(url):  #####################获取节目列表的URL【每一页的URL】
    soup = getPage(url)
    if None != soup:
        pages = getpagenumber(soup)
        urls = []
        for page in range(int(pages)):
            print url + str(page+1)
            urls.append(url + str(page+1))
        if len(urls) < 1:
            urls.append(url)
        return urls
    else:
        return urls


def getvoiceURL(url): #####################获取每一页的各个节目URL
    urls =[]
    soup = getPage(url)
    if None != soup:
        divs = soup.find('div','discoverAlbum_wrapper')
        if None != divs:
            for li in divs.find_all('div','albumfaceOutter'):
                urls.append(li.a['href'])
            return urls
        else:
            return urls
    else:
        return urls

def getvoiceInfo(url,datacache):#####################获取一个节目信息与下载地址
    voiceInfomap = {}
    print url
    soup = getPage(url)
    if None != soup:
        plays = soup.find('div','detailContent_playcountDetail')
        if None != plays:
            plays= plays.find('span').text
        if None != plays:
            if plays.find('万') > 0:
               plays = float(plays.rstrip('万')) * 10000    
        else:
             plays = 0 
        try:    
            voiceInfomap['playcount'] = str(plays)                ##########播放数量
            if None!= soup.find('div','detailContent_title'):
                voiceName =soup.find('div','detailContent_title').text
            else:
                voiceName =''
            voiceInfomap['voiceName'] = voiceName                           ##########节目名称
            if None !=soup.find('div','detailContent_category'):
                if None != soup.find('div','detailContent_category').find('span','mgr-5'):
                    updatetime = soup.find('div','detailContent_category').find('span','mgr-5').text
                else:
                    updatetime =''
            else:
                updatetime =''
            voiceInfomap['updatetime'] = updatetime  ##########最后更新时间
            if None != soup.find('div','detailContent_category'):
                if None != soup.find('div','detailContent_category').find('a'):
                    voicesort = soup.find('div','detailContent_category').find('a').text.lstrip('【').rstrip('】') 
                else:
                    voicesort =''
            else:
                voicesort=''           
            voiceInfomap['voicesort'] =voicesort              ##########分类名称
            voiceInfomap['voicepages'] = getpagenumber(soup)                                                  ##########节目的音频总页数
            voiceInfomap['voiceurl'] = url +'?page=' 
            voiceInfomap['datacache'] = datacache
            voiceInfomap['_id'] = ObjectId()
            db = connectDB()
            result = db.showInfo.insert(voiceInfomap)   #节目信息存储
            if result == None:
                result = db.showInfo.insert(voiceInfomap)   #重e新存储节目信息
            return result
        except Exception, e :
            print 'HTML 解析错误~',e
            return None
    else:
        return None



#classifyInfo()

def classifyInfo():  ###########下载分类【顶级分类与细类】
    headings ,sublist=getclassify('http://album.ximalaya.com/')
    if len(headings) > 0:
        for heading in headings:
            #print 'JSON:',JSONEncoder().encode(heading)
            serversort(heading, 0)
    if len(sublist) > 0:
        for subclass in sublist:
            serversort(subclass, 1)

def selectVoidceclassify():  ##查询分类
    headings = []
    subclasss= []
    db = connectDB()
    for item in db.heading.find():#顶级分类
        headings.append(item) 
    for item in db.subclass.find():#细分类
        subclasss.append(item) 
    return headings,subclasss


def servershowInfo():
    heads,sublist=selectVoidceclassify()
    try:
        for x in sublist:
            print x 
            suburl = x.get('suburl',None)
            datacache = x.get('datacache',-1)
            if None != suburl :
               urls = getclassifyList(suburl)#获取节目列表的URL【每一页的URL】
               if len(urls) > 0:
                    for u in urls:
                        urlps = getvoiceURL(u)#获取每一页的各个节目URL
                        if len(urlps) > 0:
                            for urlp in urlps:
                                getvoiceInfo(urlp,datacache)
    except Exception, e:
        print '出错整理结束',e
        
if __name__ == '__main__':
    servershowInfo()

#classifyInfo()

#getvoiceInfo('http://www.ximalaya.com/6572365/album/343042',2)

#print getclassifyList('http://album.ximalaya.com/dq/all-%E4%B8%9C%E5%B9%BF%E6%96%B0%E9%97%BB%E5%8F%B0')

#print getvoiceURL('http://album.ximalaya.com/dq/all-%E4%B8%9C%E5%B9%BF%E6%96%B0%E9%97%BB%E5%8F%B0/5')


# ll = 'http://album.ximalaya.com/dq/all-郭德纲相声/1'
# urls = getvoiceURL(ll)  
# for url in urls:
#     getvoiceInfo(url)

# urls = getclassifyList('http://album.ximalaya.com/dq/book-青春校园/')#获取节目列表的URL【每一页的URL】
# if len(urls) > 0:
#     for u in urls:
#         urlps = getvoiceURL(u)#获取每一页的各个节目URL
#         if None != urlps:
#             if len(urlps) > 0:
#                 for urlp in urlps:
#                     getvoiceInfo(urlp, 2)
  
    
       
   
   
