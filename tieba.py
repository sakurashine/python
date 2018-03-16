#根据帖号抓取百度贴吧帖子文字信息
# -*- coding:utf-8 -*-
from io import open
import urllib
import urllib2
import re
import os

#工具类，处理数据
class Tool:
    #去除img标签和7位长的空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删掉超链接
    removeAddr = re.compile('<a.*?>|</a>')
    #把<tr><div></div></p>这些会导致换行的标签/标签尾替换成\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD= re.compile('<td>')
    replacePara = re.compile('<p.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        return x.strip()

    #去除img标签,7位长空格
    removeImg = re.compile(u'<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile(u'<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile(u'<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile(u'<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile(u'<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile(u'<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile(u'<.*?>')

    @staticmethod
    def replace(x):
        x = re.sub(Tool.removeImg,u"",x)
        x = re.sub(Tool.removeAddr,u"",x)
        x = re.sub(Tool.replaceLine,u"\n",x)
        x = re.sub(Tool.replaceTD,u"\t",x)
        x = re.sub(Tool.replacePara,u"\n    ",x)
        x = re.sub(Tool.replaceBR,u"\n",x)
        x = re.sub(Tool.removeExtraTag,u"",x)
        #strip()将前后多余内容删除
        return x.strip()

class BDTB:

    def __init__(self,baseUrl,seeLZ=1):
        self.baseURL = baseUrl
        self.seeLZ = u'?see_lz=' + unicode(seeLZ)
        self.tool = Tool()
        self.file = None
        self.floor = 1
        self.defaultTitle = u"百度贴吧"

    def getPage(self,pageNum):
        try:
            url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            #print response.read()
            return response.read().decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e,'reason'):
                print "连接百度贴吧失败，错误原因是",e.reason
                return None

    def getTitle(self):
        page = self.getPage(1)
        #pattern = re.compile(ur'<h(\d)(\W)+class="core_title_txt.*>(.*)</h\1>')
        pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',re.S)
        result = re.search(pattern,page)
        if result:
            #print result.group(1)
            return result.group(1).strip()
        else:
            return None

    def getPageNum(self):
        page = self.getPage(1)
        pattern = re.compile('<li class="l_reply_num.*?<span class="red">(.*?)</span>',re.S)
        result = re.search(pattern,page)
        if result:
            #print result.group(1)
            return result.group(1).strip()
        else:
            return None

    def getContent(self,page):
        page = self.getPage(page)
        pattern = re.compile(u'<div id="post_content_.*?>(.*?)</div>')
        #pattern = re.compile('<div class="p_content  ">.*?<div id="post_content_.*?>(.*?)</div>',re.S)
        items = re.findall(pattern,page)
        contents=[]
        for item in items:
            content = "\n"+self.tool.replace(item)+"\n"
            contents.append(content)
        return contents
            #print floor,u"楼---------------------------------------------------------------------------\n"
            #print self.tool.replace(item)
            #floor += 1 

    def isEmoji(self,content):
        if not content:
            return False
        if u"\U0001F600" <= content and content <= u"\U0001F64F":  
            return True  
        elif u"\U0001F300" <= content and content <= u"\U0001F5FF":  
            return True  
        elif u"\U0001F680" <= content and content <= u"\U0001F6FF":  
            return True  
        elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":  
            return True  
        else:  
            return False  

    #写入txt文件，文件名
    def setFileTitle(self,title):
        if title is not None:
            self.file = open(title + ".txt","w+")
        else:
            self.file = open(self.defaultTitle + ".txt","w+")

    def writeData(self,contents):
        for item in contents:
            if self.isEmoji(item):
                continue
            else:
                floorLine = "\n" + str(self.floor) + u"楼----------------------------------------------------------------------\n"
                self.file.write(floorLine)
                self.file.write(item)
                self.floor += 1

    def start(self):
        pageNum = self.getPageNum()
        indexPage = self.getPage(1)
        title = self.getTitle()
        print title
        self.setFileTitle(title)
        if pageNum == None:
            print "URL已失效，请重试"
            return
        try:
            #print "这个帖子有"+str(pageNum)+"页"
            for i in range(1,int(pageNum)+1):
                #print "正在写入第"+str(i)+"页数据"
                #page = self.getPage(i)
                contents = self.getContent(i)
                #print contents
                #print i
                self.writeData(contents)
        except IOError,e:
            print "写入异常，原因是" + e.message
        finally:
            print "All Done."



baseURL = 'http://tieba.baidu.com/p/' + str(raw_input(u'http://tieba.baidu.com/p/'))
seeLZ = raw_input('see_lz only? Yes 1 No 0')
bdtb = BDTB(baseURL,seeLZ)
bdtb.start()


#3909007969
