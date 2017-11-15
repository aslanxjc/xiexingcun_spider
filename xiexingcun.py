#-*- coding:utf-8 -*-
import json
import random
import time
import chardet
import os,sys,io
import requests
from bs4 import BeautifulSoup
import requesocks
import socks
import socket

reload(sys)
sys.setdefaultencoding('utf-8')

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

from stem import Signal
from stem.control import Controller                                                                                                                                                                     
from redis import Redis                                                            


controller = Controller.from_port(port=9051)
Password = "mypassword"

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket


def renew_tor():
    global controller
    global Password
    print ('Renewing Tor Circuit')
    if "stem.control.Controller" not in str(controller):
        #if global controller exist no more
        controller = Controller.from_port()
    # debug output
    print (controller)
    # authenticare the connection with the server control port 
    controller.authenticate(Password)
    print ('Tor running version is : %s' % controller.get_version() )
    # force a new circuit
    controller.signal(Signal.NEWNYM)
    # wait for new circuit
    time.sleep(3)
    print ('New Tor circuit estabilished')


#def renew_tor():
#    """切换IP
#    """
#    global controller
#    if "stem.control.Controller" not in str(controller):
#        print 222222222222
#        #if global controller exist no more
#        controller = Controller.from_port()
#    controller.authenticate("mypassword")
#    controller.signal(Signal.NEWNYM)
                                                                                   
                                                                                   
class RedisClient(Redis):                                                          
    '''                                                                            
    '''                                                                            
    def __init__(self,host=None,port=None,db=None,password=None):                  
                                                                                   
        super(RedisClient,self).__init__(host,port,db)                             
                                                                                   
    def delete_like(self,key=None):                                                
        '''                                                                        
        '''                                                                        
        if key:                                                                    
            keys = filter(lambda x:key in x,self.keys())                           
            if keys:                                                               
                return self.delete(*keys)                                          
            else:                                                                  
                return 'nokeys'                                                    
        else:                                                                      
            return 'need keys'                                                     
                                                                                   
redis_cache = RedisClient(host="127.0.0.1", port=6379, db=0)



def getip_requesocks(url):
    print "(+) Sending request with requesocks..."
    session = requesocks.session()
    session.proxies = {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    #r = session.get(url, stream=True)
    r = session.get(url)
    return r


def get_random_ip():
    """
    """
    ip = redis_cache.get("random_ip")
    if not ip:
        url = "http://dev.kuaidaili.com/api/getproxy/?orderid=991070763711122&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&protocol=1&method=2&an_an=1&an_ha=1&sep=1"
        rsp = requests.get(url)
        ips = rsp.text.split("\r\n")
        ip = ips[random.randint(0,len(ips))]
        redis_cache.set("random_ip",ip,10)
        time.sleep(5)
    return ip



def change_ip_requests(url):
    """
    """
    rsp = None

    headers = {
                    "Referer":"http://www.xiexingcun.com",
                    "User-Agent":'''Mozilla/5.0 (Windows NT 6.1; WOW64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100''',
                    #"Cookie":self.cookie,
                    #"Upgrade-Insecure-Requests":1,
                    "Host":"www.xiexingcun.com" 
                    }

    purl = get_random_ip()
    proxy = {"http":"http://"+purl}

    print proxy
    print u"开始下载{}...".format(url)

    #connectTor()

    try:
        #url = "http://115.28.186.27:12005/test/"
        #print 111111111
        rsp = requests.get(url,proxies=proxy,timeout=10,headers=headers)
        print rsp.status_code
        if rsp.status_code == 200:
            return rsp
        print "status error"
        change_ip_requests(url)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print 'error digui...'
        #renew_tor()
        change_ip_requests(url)

    #return rsp



def parse_grade_html(_html):
    """解析年级返回年级版本上下册相关内容
    """
    ids = []
    urls = []
    soup = BeautifulSoup(_html,"html5lib")
    tb4 = soup.find_all("td",class_="main_tdbg_575")

    #获取该版本改年级下的资源ID
    for _td in tb4:
        _as = _td.find_all("a")
        #找链接
        for _a in _as:
            id = _a.attrs.get("href")
            ids.append(id)
    for _id in ids:
        _id = _id.split("/")[-1].split(".")[0]
        url = "http://xiexingcun.com/xy1/abShowSoftDown.asp?UrlID=1&SoftID={}".format(_id)
        urls.append(url)

    return urls


def download_zip(url,path):
    local_filename = url.split('/')[-1]
    local_filename = url.split('/')[-1]+".zip"

    local_filename = os.path.join(path,local_filename)

    r = change_ip_requests(url)
    if r:
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from J.F.Sebastian
        print u"下载完成!"
        return True
        #return local_filename
    print u"下载失败!!!!"
    return None


def check_url(data="data.json",url=None):
    """
    """
    with open(data,"r") as f:
        org_list = json.load(f)
        if url in org_list:
            return True
        else:
            #org_list.append(url)
            #with open(data,"w+") as nf:
            #    nf.write(json.dumps(org_list))
            #    nf.close()
            return None

def update_url(data="data.json",url=None):
    """
    """
    with open(data,"r") as f:
        org_list = json.load(f)
        org_list.append(url)
        with open(data,"w+") as nf:
            nf.write(json.dumps(org_list))
            nf.close()



def get_bb_grades():
    """获取版本和版本下的年级
    """
    root_url = "http://www.xiexingcun.com/"
    urls = [
        {"rj":["xy1","xy2","xy3","xy4","xy5","xy6","xy7","xy8","xy9","xy10","xy11","xy12"]},
        {"sj":["sxy1","sxy2","sxy3","sxy4","sxy5","sxy6","sxy7","sxy8","sxy9","sxy10","sxy11","sxy12"]},
        {"ywab":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"ywsb":["11","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"bsdb":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"jjb":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"xsdb":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"ejb":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
        {"ccb":["1a","1b","2a","2b","3a","3b","4a","4b","5a","5b","6a","6b"]},
    ]

    for _url in urls:
        key = _url.keys()[0]
        for _u in _url.get(key):
            #_url = root_url+key+"/"+_u+"/Index.html"
            _url = root_url+"/"+_u+"/Index.html"
            #print _url
            path = os.path.join(BASE_PATH,key)
            path = os.path.join(path,_u)
            #print path
            if not os.path.exists(path):
                os.makedirs(path)

            #_ghtml = requests.get(_url).text
            rsp = change_ip_requests(_url) 
            #if rsp:
            _ghtml = rsp.text

            #print _ghtml
            urls = parse_grade_html(_ghtml)
            print len(urls)
            for _url in urls:
                #pass
                if check_url("data.json",_url):
                    print u"跳过:{}".format(_url)
                    continue
                #change_ip_requests(_url)
                if download_zip(_url,path):
                    update_url("data.json",_url)

                time.sleep(1)

                #break

            time.sleep(1)
            #break
        #break


def test():
    """
    """


if __name__ == "__main__":
    get_bb_grades()
