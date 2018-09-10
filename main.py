#encoding:utf8
import sys
reload(sys); sys.setdefaultencoding('utf8')
import os
import time
import logging
import json
from Worker import *

cur_time = time.strftime( '%Y-%m-%d %X', time.localtime( time.time() ) ).replace(':','').replace(' ','_')
log_file = './log/myapp'+cur_time+'.log'

'''
{
    "websites" : "websites.txt",
    "dic_folder" : "dic",
    "request_method" : "HEAD",
    "thread_num" : "16"
}
'''
class Manager(object):
    cfg = None
    
    def __init__(self):
        try:
            self.logger_init()
            j = json.load(open('config.json'))
            self.cfg = {}
            self.cfg['websites'] = self.ReadWebsites(j['websites'])
            self.cfg['dics']       = self.ReadDics(j['dic_folder'])
            self.cfg['request_method'] = j['request_method'].strip().upper()
            self.cfg['thread_num']     = j['thread_num']
            
        except Exception as e:
            logging.error('Manager __init__ error: %s'%e)

    def logger_init(self):
        if False == os.path.exists('./log'):
            os.mkdir('./log')

        logging.basicConfig(level=logging.ERROR,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_file,
                            filemode='w')

    def Start(self):
        try:
            for site in self.cfg['websites']:
                w = Worker(site, self.cfg)
                w.Start()

        except Exception as e:
            logging.error('Manager Start error: %s'%e)
    
    def ReadWebsites(self,webcfg):
        try:
            fin = open(webcfg ,'rb')

            websites = []
            while 1:
                line = fin.readline()
                if not line: break

                site = line.strip()
                if len(site)>=3 and site not in websites:
                    websites.append( site )

            fin.close()
            
            return websites
        except Exception as e:
            logging.error('ReadWebsites error : %s'%e )
    
    def ReadDics(self,diccfg):
        try:
            dics = []
            doclist = os.listdir(diccfg)
            doclist.sort()
            for filename in doclist:
                try:
                    fin = open(diccfg+'/'+filename,'rb')
                    while 1:
                        line = fin.readline()
                        if not line:break
                        record = line.strip()
                        if len(record)>1:
                            dics.append(record)

                    fin.close()

                    return dics
                except Exception as e:
                    logging.error('dic error : %s , dicname:%s'%(e, filename) )

        except Exception as e:
            logging.error('ReadDics error : %s'%e )

def main():
    w = Manager()
    w.Start()

if __name__=='__main__':
    main()
    