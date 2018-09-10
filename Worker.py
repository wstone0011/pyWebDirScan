#encoding:utf8
import sys
reload(sys); sys.setdefaultencoding('utf8')
import requests
import logging
import re
import threading
import os

g_mutex = threading.Lock()

class Worker(object):
    site = None
    cfg = None
    def __init__(self, site, cfg):
        self.site = site
        self.cfg  = cfg

    def Start(self):
        try:
            dic_len = len(self.cfg['dics'])
            if not dic_len:
                return
                
            average = dic_len/self.cfg['thread_num']
            lrs = []
            for i in xrange(0, self.cfg['thread_num']):
                lrs +=[[i*average, (i+1)*average-1]]     
            lrs[-1][1] = dic_len-1
            
            threads = []
            for _ in lrs:
                l = _[0]
                r = _[1]
                t = Scanner(self.site, self.cfg['dics'][l:r+1], self.cfg['request_method'])
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        except Exception as e:
            import pdb; pdb.set_trace()
            logging.error('Start error: %s'%e)


class Scanner(threading.Thread):
    site = None
    dics = None
    request_method = None
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36'}
    
    def __init__(self, site, dics, request_method):
        try:
            threading.Thread.__init__(self)
            self.site = site
            self.dics = dics
            self.request_method = request_method
            
            if self.site.endswith('/'):
                self.site = self.site[:-1]
            if '://' not in self.site:
                self.site = 'http://'+self.site
            
        except Exception as e:
            logging.error('Scanner_init error: %s'%e)

    def run(self):
        for _ in self.dics:
            self.ScanOne(self.site, _, self.request_method)

    def ScanOne(self, site, dic, request_method):
        try:
            if not dic.startswith('/'):
                dic = '/'+dic

            url = site+dic

            if 'HEAD'==request_method:
                res = requests.head(url , verify=False, headers=self.headers, timeout=8)
                print('%d    %s'%(res.status_code,url))
                if 200==res.status_code:
                    self.WriteFile('./out.txt',url)
            #elif 'GET'==request_method:
            else:
                res = requests.get(url , verify=False, headers=self.headers, timeout=8)
                print('%d    %s'%(res.status_code,url))
                if 200==res.status_code:
                    data = res.content
                    if 'utf-8' not in res.encoding:
                        data = res.content.decode('gbk').encode('utf-8')
                    if not self.is_404page( data ):
                        print(url)
                        self.WriteFile('./out.txt',url)

        except Exception as e:
            if 'Max retries exceeded with url' in str(e):
                pass
            else:
                logging.error('Start error: %s  ,  url:%s'%(e, url))

    def is_404page(self, data):
        try:
            bFlag = False
            pname = re.compile("(?<=\<title\>).*?(?=\<\/title\>)", re.I)    #不区分大小写
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
            logging.error('WriteFile error : %s'%e )
        finally:
            g_mutex.release()
            