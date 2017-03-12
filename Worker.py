#-*- coding: utf8 -*-
import requests
import logging
import re
import threading
import os

g_mutex = threading.Lock()

class Worker(object):
    def __init__(self,site,dics,thread_num,request_method):
        self.site = site
        self.dics = dics
        self.thread_num = thread_num
        self.request_method = request_method

    def Start(self):
        try:
            length = len(self.dics)
            #print(len(self.dics))
            aver = len(self.dics)/self.thread_num
            #print(aver)
            paras = []
            for i in xrange(0,self.thread_num-1):
                paras.append( (0+i*aver,aver-1+i*aver) )
            paras.append( ((self.thread_num-1)*aver,length) )
            #print(paras)
            threads = []
            for pa in paras:
                argv = [self.site,self.dics[pa[0]:pa[1]+1],self.request_method]
                th = Scanner(len(argv),argv)
                th.start()
                threads.append(th)

            for th in threads:
                th.join()

        except Exception as e:
            logging.error('Start error: %s'%(str(e)))


class Scanner(threading.Thread):
    def __init__(self,argc,argv):
        try:
            threading.Thread.__init__(self)

            self.site = argv[0]
            self.dics = argv[1]
            self.request_method = argv[2]

        except Exception as e:
            logging.error('Scanner_init error: %s'%(str(e)))

    def run(self):
        if self.site.endswith('/'):
            self.site = self.site[:-1]
        if '://' not in self.site:
            self.site = 'http://'+self.site

        for dic in self.dics:
            self.ScanOne(self.site,dic,self.request_method)

    def ScanOne(self,site,dic,request_method):
        try:
            if not dic.startswith('/'):
                dic = '/'+dic

            url = site+dic

            #print(url)
            if 'HEAD' in request_method.upper() :
                payload = None
                res = requests.head(url,params=payload,timeout=8)
                print('%d    %s'%(res.status_code,url))
                if 200==res.status_code:
                    print(url)
                    self.WriteFile(os.getcwd()+'/out.txt',url)
            #elif 'GET' in request_method.upper():
            else:
                payload = None
                res = requests.get(url,params=payload,timeout=8)
                print('%d    %s'%(res.status_code,url))
                if 200==res.status_code:
                    data = res.content
                    if 'utf-8' not in res.encoding:
                        data = res.content.decode('gbk').encode('utf-8')
                    if not self.is_404page( data ):
                        print(url)
                        self.WriteFile(os.getcwd()+'/out.txt',url)
                        #print(data)


        except Exception as e:
            if 'Max retries exceeded with url' in str(e):
                pass
            else:
                logging.error('Start error: %s  ,  url:%s'%(str(e),url))

    def is_404page(self, data):
        try:
            bFlag = False
            pname = re.compile("(?<=\<title\>).*?(?=\<\/title\>)",re.I)    #不区分大小写
            sarr = pname.findall(data)
            if sarr:
                title = sarr[0]
                if -1!=title.find('404'):
                    bFlag = True

            if False==bFlag:
                if -1!=data.find('请求的信息不存在'):
                    bFlag = True

            return bFlag
        except Exception as e:
            return False

    def WriteFile(self,file,msg):
        try:
            g_mutex.acquire()
            if not os.path.exists(file):
                fout = open(file,'wb')
            else:
                fout = open(file,'ab')

            fout.write( '%s\r\n'%(str(msg)) )

            fout.close()
        except Exception as e:
            logging.error('WriteFile error : %s'%(str(e)) )
        finally:
            g_mutex.release()
            