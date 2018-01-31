import requests
from requests.exceptions import RequestException
import re
from multiprocessing import Pool
import json
import csv

Agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
headers = {'User-Agent': Agent}


def get_noe_page(url):
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    partten = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?<a.*?data-src="(.*?)".*?</a>.*?<p.*?class="name".*?title="(.*?)".*?</a>.*?class="star">(.*?)</p>.*?"releasetime">(.*?)</p>.*?class="integer">(.*?)</i>.*?"fraction">(.*?)</i>',re.S)
    items = re.findall(partten,html)
    for item in items:
        yield {
            'index':item[0],
            'img':item[1],
            'title':item[2],
            'actor':item[3].strip()[3:],
            'time':item[4].strip()[5:],
            'rate':item[5]+item[6]
            }


def write_to_file(item):
    with open('Top100.csv','a',newline='',encoding='utf-8') as f:
        try:
            csv_writer = csv.writer(f)
            csv_writer.writerow([item['index'], item['img'], item['title'], item['actor'],item['time'],item['rate']])
        except Exception as e:
            print(e)
            print(item)

def main(num):
    url = 'https://maoyan.com/board/4?offset=' + str(num)
    html = get_noe_page(url)
    for i in parse_one_page(html):
        print(i)
        write_to_file(i)
if __name__ == '__main__':
    for item in range(10):
        main(item*10)
    #pool = Pool()
    #pool.map(main,[i*10 for i in range(10)])

