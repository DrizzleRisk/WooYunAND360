#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import re
import sys
import time
import random
import logging
from bs4 import BeautifulSoup
from Common import mail , filehandle

reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig()

class FreeBuf(filehandle.FileHandle,mail.MailCreate):
    """docstring for FreeBuf"""
    def __init__(self, keysfile,eventsIdfile):
        super(FreeBuf, self).__init__('漏洞盒子监看机器人',keysfile,eventsIdfile)
        self.freeBufurl = 'https://www.vulbox.com/board/internet/page/'
        self.freeBufbaseurl = 'https://www.vulbox.com'
        self.eventsIdlist = self.eventsIdread()
        self.keyWordlist = self.keyWordsread()
        self.fileMd5 = self.fileMd5get()
        self.html = 0
        self.count = 0

    def __del__(self):
        print '漏洞盒子监看机器人 is shutdown'

    def dataRequest(self):
        '''
        从漏洞盒子获取最新的10页事件
        返回一个存储网页的list
        '''
        print 'freebuf_dataRequest'
        urls = []
        htmls = []
        for num in range(1,11):
            urls.append(self.freeBufurl + '%s' % num )
        for url in urls:
            while True:
                try:
                    page = requests.get( url , timeout =30 , verify=True )
                except requests.exceptions.ConnectionError:
                    time.sleep(30)
                    continue
                except requests.exceptions.ConnectTimeout:
                    time.sleep(60)
                    continue
                except requests.exceptions.HTTPError as e:
                    errortext = "\
                    Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Important Program Exception' , errortext , 'ExceptionInfo' )
                    time.sleep(600)
                    continue
                except Exception as e:
                    errortext = "\
                    Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
                    continue
                else:
                    if page.status_code == 200:
                        htmls.append(page.content)
                        #time.sleep(random.randint(0,60))
                        break
                    else:
                        errortext = "Page Code %s " % page.status_code
                        self.sendTextEmail( 'Page Error' , errortext , 'ExceptionInfo' )
                        continue
        return htmls

    def dataAchieve(self,pages):
        '''
        获取事件名和链接
        返回一个{链接:事件名}型的字典
        '''
        print 'freebuf_dataAchieve'
        events = {}
        for page in pages:
            while True:
                try:
                    soup = BeautifulSoup(page)
                except Exception as e:
                    errortext = "\
                    Error in function : \" %s \" ,\n \
                    Error name is : \" %s \" ,\n \
                    Error type is : \" %s \" ,\n \
                    Error Message is : \" %s \" ,\n \
                    Error doc is : \" %s \" \n" % \
                    (sys._getframe().f_code.co_name,\
                     e.__class__.__name__,\
                     e.__class__,\
                     e,\
                     e.__class__.__doc__)
                    self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
                    self.dataRequest()
                else:
                    titles = soup.find_all(href=re.compile("/bugs/vulbox"),target="_blank")
                    for title in titles:
                        events[ title['href'] ] = title.string.strip()
                    break
        return events

    def keyWordscheck(self,events):
        '''
        检查获得的标题中是否含有要监看的关键字
        函数内调用sendRecord()
        没有返回值
        '''
        print 'freebuf_keyWordscheck'
        tempFileMd5 = self.fileMd5check(self.fileMd5)
        if tempFileMd5:
            self.fileMd5 = tempFileMd5
            self.keyWordlist = self.keyWordsread()
        try:
            for (freeBufurl,freeBuftitle) in events.items():
                for Key in self.keyWordlist:
                    if Key in freeBuftitle:
                        pass
                        self.sendRecord( freeBuftitle , self.freeBufbaseurl + freeBufurl , freeBufurl.split('/')[-1] )
        except Exception as e:
            errortext = "\
            Error in function : \" %s \" ,\n \
            Error name is : \" %s \" ,\n \
            Error type is : \" %s \" ,\n \
            Error Message is : \" %s \" ,\n \
            Error doc is : \" %s \" \n" % \
            (sys._getframe().f_code.co_name,\
             e.__class__.__name__,\
             e.__class__,\
             e,\
             e.__class__.__doc__)
            self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )

    def sendRecord(self,eventTitle,eventURL,eventID):
        '''
        调用邮件发送函数并记录被发送的事件ID
        没有返回值
        函数内调用sendTextEmail()
        '''
        print 'freebuf_sendRecord'
        checkresult = self.eventsIdCheck(eventID,self.eventsIdlist)
        if 0 not in checkresult:
            try:
                #pass #test to use
                self.sendTextEmail(eventTitle,eventURL,'securityInfo')
            except Exception as e:
                errortext = "\
                Error in function : \" %s \" ,\n \
                Error name is : \" %s \" ,\n \
                Error type is : \" %s \" ,\n \
                Error Message is : \" %s \" ,\n \
                Error doc is : \" %s \" \n" % \
                (sys._getframe().f_code.co_name,\
                e.__class__.__name__,\
                e.__class__,\
                e,\
                e.__class__.__doc__)
                print errortext
                #self.sendTextEmail( 'Program Exception' , errortext , 'ExceptionInfo' )
            else:
                self.eventsIdlist.append( eventID )
                self.eventsIdadd( eventID )
        else:
            print eventTitle," Same thing was sent,did not send same mail to everyone"


if __name__ == '__main__':
    robot = FreeBuf('keyWords.txt' , './Events/EventsIDfreebuf.txt')
    robot.keyWordscheck(robot.dataAchieve(robot.dataRequest()))



