#ecoding: utf-8

from selenium import webdriver
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import requests
from urllib.request import urlretrieve
import os
import shutil
import weibo
import webbrowser
import json
import time
from win32crypt import CryptUnprotectData
import sqlite3
import time

begin_time = time.time()

#另一种启动方法，不适用于微博
#dcap = dict(DesiredCapabilities.PHANTOMJS)
#dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) Waterfox/56.2" )
#driver = webdriver.PhantomJS(desired_capabilities=dcap)
#driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")


#启动浏览器
option=webdriver.ChromeOptions()
option.add_argument('headless') 
driver = webdriver.Chrome(chrome_options=option)


#打开页面
driver.get("https://twitter.com/_maeshima_ami")
source = driver.page_source
t=BeautifulSoup(source,'html.parser')


#获取近期推特（21条）
b=[]
for a in t.find_all("li",class_="js-stream-item stream-item stream-item"):
    b.append(a.get("data-item-id"))
print(b)
print(time.time())
top=t.find("li",class_="js-stream-item stream-item stream-item js-pinned")
if top is not None:
    top_twi=top.get("data-item-id")
else:
    top_twi="0"
print(top_twi)
if b[0]==top_twi:
    get_twi=b[1]
else:
    get_twi=b[0]


#进入推文详情页
driver.get("https://twitter.com/_maeshima_ami/status/"+get_twi)
source1 = driver.page_source
soup = BeautifulSoup(source1,'html.parser')	#lxml
cut=soup.find("div",class_="permalink-inner permalink-tweet-container")


#获取推文信息
name=cut.find("strong").get_text()
sendtime=cut.find("span",class_="metadata").find("span").get_text()
twi_box=cut.find("div", class_="js-tweet-text-container")
res=str(twi_box).replace("<s>","").replace("</s>","").replace("</a>","").replace("<b>","").replace("</b>","").replace("</p>","")
pattern=r'[>|<]'
result = re.split(pattern, res)
v=0
for item in result:
    if re.match('img alt',item):
        result[v]=re.findall('.*alt="(.*?)".*',item)[0]
    elif re.search(r'[div|class=|pic.twitter.com]',item):
        result[v]=""
    v=v+1
twitter=""
for i in result:
    twitter=twitter+i
print("name:")
print(name)
print("time:")
print(sendtime)
print("twi:")
print(twitter)
print("img:")


#获取和下载图片
c=cut.find("div",class_="AdaptiveMedia-container")
if c is not None:
    i=0
    os.mkdir(get_twi)
    os.chdir('C:\\Users\\jinshuai\\source\\repos\\TwitterToWeibo\\TwitterToWeibo\\'+get_twi)
    for img in c.find_all("img"):
        i=i+1
        urlretrieve(img.get("src"), str(i)+'.jpg') 
        print(img.get("src")+" is OK")



#获取谷歌浏览器cookie
def getcookiefromchrome(host='.weibo.com'):
  cookiepath=os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
  sql="select host_key,name,encrypted_value from cookies where host_key='%s'" % host
  with sqlite3.connect(cookiepath) as conn:
    cu=conn.cursor()    
    cookies={name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
    print(cookies)
    return cookies


#使用cookie打开微博
url='https://weibo.com'
httphead={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'}

cookie=getcookiefromchrome(host='.weibo.com')
driver.get("https://weibo.com")
for item in cookie:
    driver.add_cookie({'domain':'.weibo.com','name':item ,'value':cookie[item]})
driver.get("https://weibo.com") #写入cookie后再刷新一次


#定位输入框，写入微博
input_box=driver.find_elements_by_class_name('W_input')
try:
    input_box[1].send_keys('沙雕微博自动转推测试 v0.1\n\n'+twitter)
except Exception as e:
    print("fail")


#循环上传图片
num=i
for i in range(1,num+1):
    driver.find_element_by_name('pic1').send_keys('C:\\Users\\jinshuai\\source\\repos\\TwitterToWeibo\\TwitterToWeibo\\'+get_twi+'\\'+str(i)+'.jpg')


#暂停五秒后（暂定）点击上传
time.sleep(5)
try:
    js = 'document.getElementsByClassName("W_btn_a btn_30px ")[0].click()'
    driver.execute_script(js)
    print('成功')
except Exception as e:
    print('fail')


#切换文件夹，删除文件
os.chdir('C:\\Users\\jinshuai\\source\\repos\\TwitterToWeibo\\TwitterToWeibo')
shutil.rmtree(get_twi)
end_time =time.time()
run_time = end_time-begin_time
print("总用时：",run_time)
driver.close