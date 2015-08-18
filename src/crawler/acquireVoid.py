#!/usr/bin/env python
#coding=utf-8
import urllib2 ,sys,requests ,json,os
from bs4 import  BeautifulSoup
from bson.objectid import ObjectId
import pymongo 
from json import *
from gridfs import *
import StringIO 
from elasticsearch import Elasticsearch




def connectDB():  #####连接数据库
    try:
        client = pymongo.MongoClient("mongodb://192.168.102.154:27017")
        db = client.radio   #创建 radio 数据库
        return db
    except Exception , e:
        print 'Mongodb连接错误' ,e
        connectDB()
        
def selectVoidceclassify():  ##查询分类
    headings = []
    try:
        db = connectDB()
        for item in db.heading.find().sort('cid'):#顶级分类
            headings.append(item) 
        return headings
    except Exception ,e:
        print e
        return headings

def selectshowInfo(cid):
    showInfos = []
    try:
        db = connectDB()
        for item in db.showInfo.find({'datacache':cid}):
            showInfos.append(item)
        return showInfos
    except Exception ,e:
        print e
        return showInfos
    
def getPage(url):          ####################获取页面
    try:
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        return soup
    except Exception ,e:
        print '服务器错误',e
        return None


def elastics(audioInfo):
    try:
        es = Elasticsearch('192.168.100.134',sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
        headingName = audioInfo.get('cid')
        if headingName != None and ''!= headingName:
            if None != es:
                es.create('audio', headingName , audioInfo)
    except Exception ,e:
        print 'ES出错！',e


def saveaudio(void_id):
    url = 'http://www.ximalaya.com/tracks/'+void_id+'.json'
    file_dir = 'D:\\audio\\'
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    page = urllib2.urlopen(url).read()
    audios ={}
    compressedFile = StringIO.StringIO()     
    db = connectDB() 
    if page != None:
        try:
            date = json.loads(page)
            if date['play_path_64'] != None:
                duration = date['duration']   #音频时长
                audios['duration'] = duration
                play_count = date['play_count'] # 播放次数
                audios['play_count'] = play_count
                title = date['title']  #音频标题
                audios['title'] = title
                audios['void_id'] = void_id
                address = date['play_path_64']
                if None != address:
                    audios['address']=address
                    formatsrc = address.split('.')
                    if len(formatsrc)>0:
                        try:
                            outf =None
                            format =formatsrc[len(formatsrc)-1]
                            audios['format'] = format
                            audio = urllib2.urlopen(address)
                            dir = file_dir +void_id+'.'+ format
                            if os.path.exists(dir):
                                print '文件已经存在'
                                return None
                            audios['audios_dir'] = dir
                            outf = open(dir,'wb')               
                            while True:
                                s = audio.read(1024*32)
                                if len(s) == 0:
                                    break
                                outf.write(s)
                                compressedFile.write(s)                                    
                            fs = GridFS(db,collection='audio')
                            gf = fs.put(compressedFile.getvalue(),filename=title+'.'+format,format=format,playcount=play_count)                           
                            audios['audio_id'] = str(gf)
                            outf.flush()
                        except Exception,e:
                            print '文件操作错误' ,e 
                            audios['tag'] = '0'
                        finally:
                            if outf != None:
                                outf.close()   
                            compressedFile.close()
                            
                        audios['tag'] = '1'
                        return  audios
        except Exception,e:
            print e
            return None
    return None

def getVoidInfo(url,cid,headingName,voiceName):
    soup = getPage(url) 
    db = connectDB()
    if None != soup:
        try:
            if soup.find('div', 'album_soundlist'):
                pagediv  = soup.find('div','album_soundlist')
                if pagediv != None:
                    lis = pagediv.find_all('li')
                    if lis !=None:
                        for li in lis:
                            void_id =''
                            if None != li['sound_id']:
                                void_id = li['sound_id']
                            lidiv = li.find('div','miniPlayer3')
                            if lidiv != None:
                                void_name =''
                                if None != lidiv.find('a','title'):
                                    void_name = lidiv.find('a','title').text
                                void_time ='' 
                                if None != lidiv.find('div','operate').span:
                                    void_time = lidiv.find('div','operate').span.text
                                playcount ='' 
                                if None != lidiv.find('span','sound_playcount'):   
                                    playcount = lidiv.find('span','sound_playcount').text                               
                            if void_id !='':                                    
                                print void_id,void_name,void_time,playcount
                                audios = saveaudio(void_id)   
                                if None != audios:  
                                    if '1' == audios.get('tag'):
                                        audios['cid'] = cid
                                        audios['void_time'] = void_time
                                        audios['headingName'] = headingName
                                        audios['voiceName'] = voiceName                                
                                        #存到ES的方法
                                        elastics(audios)                                        
                                        result = db.audioInfo.insert(audios)   #存储音频信息
                                else:
                                    continue                          
        except Exception, e:
            print '解析出错～',e
            return None
        
def crawlerVoid():
    headings = selectVoidceclassify()
    if len(headings) > 0 :
        for heading in headings:
            cid = heading.get('cid')
            headingName = heading.get('name')
            if cid != None:
                showInfos = selectshowInfo(cid)
                if len(showInfos) > 0:
                    for showInfo in showInfos:
                        voiceurl = showInfo.get('voiceurl')
                        voicepages = showInfo.get('voicepages')
                        playcount = showInfo.get('playcount')
                        voiceName = showInfo.get('voiceName')
                        if playcount != None and playcount !='':
                            playcount = float(playcount)
                            if playcount > 1000000.0:   #优先下载播放数大的
                                if voicepages != None and voicepages !='':
                                    for i in range(int(voicepages)):
                                        try:
                                            url = voiceurl + str(i)
                                            getVoidInfo(url,cid,headingName,voiceName)
                                        except Exception, e:
                                            print e
                                            continue
                
if __name__ == '__main__':
    crawlerVoid()
    
#selectVoidceclassify()
#selectshowInfo('1')    
#getVoidInfo('http://www.ximalaya.com/1000202/album/2667276?page=1')
#saveaudio('8279299')

