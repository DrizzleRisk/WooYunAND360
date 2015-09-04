#! usr/bin/env python
# -*- coding=utf-8 -*-
import requests
import sys
import time
import json
from Common import mail , filehandle

reload(sys)
sys.setdefaultencoding('utf8')

class WooYun(filehandle.FileHandle,mail.MailCreate):
    """docstring for WooYun"""
    def __init__(self,keysfile,eventsIdfile):
        super(WooYun, self).__init__('WooYun监看机器人',keysfile,eventsIdfile)
        self.wooyun_url = 'http://api.wooyun.org/bugs/submit'
        self.eventsIdlist = self.eventsIdread()
        self.keyWordlist = self.keyWordsread()
        self.fileMd5 = self.fileMd5get()
        self.count = 0

    def __del__(self):
        print 'WooYun监看机器人 is shutdown'

    def dataRequest(self):
        '''
        从乌云API获取json格式的数据
        返回json格式的数据
        '''
        print 'dataRequest'
        while True:
            try:
                text = requests.get(self.wooyun_url , timeout = 30 )
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                continue
            except requests.exceptions.ConnectTimeout:
                time.sleep(30)
                continue
            except Exception as e:
                errortext = "Error in function : \" %s \" ,\n \
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
                if text.status_code == 200:
                    text = text.content
                break
        return text

    def dataAchieve(self,text):
        '''
        将json格式的数据取出
        '''
        print 'dataAchieve'
        try :
            data = json.loads(text)
            #raise Exception("data is not json")
        except Exception as e:
            errortext = "Error in function : \" %s \" ,\n \
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
            md5value = self.fileMd5check(self.fileMd5)
            if md5value:
                self.keyWordsread()
                self.fileMd5 = md5value
        return data

    def keyWordscheck(self,data):
        '''
        检查获得的标题中是否含有要监看的关键字
        内部调用sendRecord()
        没有返回值
        '''
        print 'keyWordscheck'
        try:
            for detail in data:
                for Key in self.keyWordlist:
                    if detail.get('title').find(Key) != -1:
                        self.sendRecord(detail.get('title'),detail.get('link'),detail.get('id'))
                        break
        except Exception as e:
            errortext = "Error in function : \" %s \" ,\n \
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
        print 'sendRecord'
        checkresult = self.eventsIdCheck(eventID,self.eventsIdlist)
        if 0 not in checkresult:
            try:
                #pass #test to use
                self.sendTextEmail(eventTitle,eventURL,'securityInfo')
                #aise Exception("Mail send error") #test
            except Exception as e:
                errortext = "Error in function : \" %s \" ,\n \
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
    test = WooYun('KeyWords.txt' , 'EventsID.txt')
    robot = test.dataRequest()
    data = test.dataAchieve(robot)
    test.keyWordscheck(data)
