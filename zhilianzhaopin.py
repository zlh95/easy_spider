import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pymongo
from requests.exceptions import RequestException
from threading import Thread
from queue import Queue

q = Queue()
NUM = 360
JOBS = 6

client = pymongo.MongoClient('localhost')
db = client['ÕÐÆ¸ÍøÕ¾']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Host': 'sou.zhaopin.com',
    'Referer': 'https://www.zhaopin.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

def get_one_page(city,keyword,page):
    paras = {
        'jl': city,
        'kw': keyword,
        'sm':'0',
        'p': page,
    }
    try:
        url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?' + urlencode(paras)
        response = requests.get(url,verify=False,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('»ñÈ¡Ê×Ò³Ê§°Ü£¡')

def parse_one_page(html):
    soup = BeautifulSoup(html,'lxml')
    content = soup.find('div',attrs={'class':'newlist_list_content'})
    #print(content)
    company = content.find_all('td',{'class':'gsmc'})
    companies = (i.text for i in company)
    salary = content.find_all('td',{'class':'zwyx'})
    salary_level = (i.text for i in salary)
    localtion = content.find_all('td',{'class':'gzdd'})
    localtions = (i.text for i in localtion)
    position = content.find_all('div',{'style':'width: 224px;*width: 218px; _width:200px; float: left'})
    positions = (i.text.strip() for i in position)
    for a,b,c,d in zip(positions,salary_level,companies,localtions):
        result = {
            'position':a,
            'salary_level':b,
            'company':c,
            'localtion':d
        }
        save_to_mongo(result)

def save_to_mongo(result):
    if db['ÖÇÁªÕÐÆ¸'].insert(result):
        print('³É¹¦´æ´¢µ½MongoDB',result)
        return True
    return False


def main(num):
    html = get_one_page(city='³¤É³',keyword='python',page=num)
    parse_one_page(html)

def working():
    while True:
        arguments = q.get()
        main(arguments)
        q.task_done()
for i in range(NUM):
    t = Thread(target=working)
    t.setDaemon(True)
    t.start()
for i in range(JOBS):
    q.put(i)
q.join()
