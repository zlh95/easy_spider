import csv
import re
from urllib.parse import urlencode

from tqdm import tqdm
from requests.exceptions import RequestException
import requests




headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Host': 'sou.zhaopin.com',
    'Referer': 'https://www.zhaopin.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

def get_one_page(city,keyword,region,page):
    paras = {
        'jl': city,  # 搜索城市
        'kw': keyword,  # 搜索关键词
        'isadv': 0,  # 是否打开更详细搜索选项
        'isfilter': 1,  # 是否对结果过滤
        'p': page,  # 页数
        're': region  # region的缩写，地区，2005代表海淀
    }
    url = 'https://sou.zhaopin.com/jobs/searchresult.ashx?' + urlencode(paras)
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('解析首页失败')
        return None

def parse_one_page(html):
    pattern = re.compile('<a style=.*? target="_blank">(.*?)</a>.*?'
                         '<td class="gsmc"><a href="(.*?)" target="_blank">(.*?)</a>.*?'
                         '<td class="zwyx">(.*?)</td>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        job_name = item[0]
        job_name = job_name.replace('<b>', '')
        job_name = job_name.replace('</b>', '')
        yield {
            '职位': job_name,
            '公司网站': item[1],
            '公司名称': item[2],
            '薪水': item[3]
        }

def write_csv_file(path, headers, rows):
    '''
    将表头和行写入csv文件
    '''
    # 加入encoding防止中文写入报错
    # newline参数防止每写入一行都多一个空行
    with open(path, 'a', encoding='gb18030', newline='') as f:
        f_csv = csv.DictWriter(f, headers)
        f_csv.writeheader()
        f_csv.writerows(rows)


def write_csv_headers(path,headers):
    with open(path,'a',encoding='gb18030',newline='') as f:
        f_csv = csv.DictWriter(f,headers)
        f_csv.writeheader()


def write_csv_rows(path,headers,rows):
    with open(path,'a',encoding='gb18030',newline='') as f:
        f_csv = csv.DictWriter(f,headers)
        f_csv.writerows(rows)



def main(city,keyword,region,pages):
    file_name = 'zlzp_' + city + '_' + keyword + '.csv'
    headers = ['职位', '公司网站', '公司名称', '薪水']
    write_csv_headers(file_name,headers)
    for i in tqdm(range(pages)):
        jobs =[]
        html = get_one_page(city,keyword,region,i)
        for item in parse_one_page(html):
            jobs.append(item)
        write_csv_rows(file_name,headers,jobs)

if __name__ == '__main__':
    main('北京','爬虫工程师',2005,30)
