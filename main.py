#-*- coding: utf8 -*-
import os
import time
import logging
import json
from Worker import *

cur_time = time.strftime( '%Y-%m-%d %X', time.localtime( time.time() ) ).replace(':','').replace(' ','_')
log_file = os.getcwd()+'./log/myapp'+cur_time+'.log'

class Manager(object):
    def __init__(self):
        try:
            self.logger_init()
            cfg = self.ReadConfig()
            self.websites = self.ReadWebsites(cfg[0])
            self.dics = self.ReadDics(cfg[1])
            self.thread_num = int(cfg[2])
            self.request_method = cfg[3]
        except Exception as e:
            logging.error('mysql_select_error : %s'%(str(e)))

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
            for site in self.websites:
                w = Worker(site,self.dics,self.thread_num,self.request_method)
                w.Start()

        except Exception as e:
            logging.error('mysql_select_error : %s'%(str(e)))

    def ReadConfig(self):
        try:
            fin = open('config.json','r')
            fulltext = fin.read()
            #print(fulltext)
            js = json.loads(fulltext)
            print(js)
            fin.close( )
            return [js["websites"] , js["dic_folder"] , js["thread_num"] , js["request_method"] ]
        except Exception as e:
            logging.error('ReadConfig error : %s'%(str(e)) )

    def ReadWebsites(self,webcfg):
        try:
            fin = open(os.getcwd()+'/'+webcfg ,'r')

            websites = []
            while 1:
                line = fin.readline()
                if not line: break

                site = line.replace('\n','').replace('\r','').strip()
                if len(site)>=1:
                    websites.append( site )

            fin.close()
            #print(websites)
            return websites
        except Exception as e:
            logging.error('ReadWebsites error : %s'%(str(e)) )

    def ReadDics(self,diccfg):
        try:
            dics = []
            doclist = os.listdir(os.getcwd() + '/'+diccfg)
            doclist.sort()
            for filename in doclist:
                try:
                    fin = open(os.getcwd() + '/'+diccfg+'/'+filename,'r')
                    while 1:
                        line = fin.readline()
                        if not line:break
                        record = line.replace('\n','').replace('\r','').strip()
                        if len(record)>1:
                            dics.append(record)

                    fin.close()

                    return dics
                except Exception as e:
                    logging.error('dic error : %s , dicname:%s'%(str(e),filename) )

        except Exception as e:
            logging.error('ReadDics error : %s'%(str(e)) )

def main():
    w = Manager()
    w.Start()

if __name__=='__main__':
    main()
    