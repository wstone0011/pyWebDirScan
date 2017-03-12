# pyWebDirScan
Web目录扫描，字典用的御剑的字典。

python版本  2.7
在Win7下测试，没啥大问题


配置文件为config.json，按照json格式存储。
websites          要扫描的站点列表
dic_folder        字典文件存放目录，扫描时会使用此目录下的所有字典
thread_num        扫描时所开启的线程数
request_method    请求方式，支持：HEAD,GET 。其中HEAD的速度快很多。


工作原理：
构造url，通过GET方式访问，如果应答状态是200，...，则认为此目录存在，记录到out.txt


所有文本均使用UTF-8编码
路径不要有中文

