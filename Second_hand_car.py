import requests
import time
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import pandas as pd

headers = {'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
url = 'http://changsha.taoche.com/all/'

def get_brands_urls():
    try:
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text,'lxml')
            # 按照字母排序，抓取二手车的品牌名称和链接
            car_brands = soup.find_all('ul',{'class':'ul_C'})
            #print(car_brands)
            #列表生成式中，第一层循环把所有的字母代表的品牌选出来
            #第二层循环把改字母下的品牌选出来
            #第三层循环把<a /a>选出来
            car_brands = [k for i in car_brands for j in i for k in j] #提取<a .. /a>的内容
            brands = [i.text for i in car_brands] #得到每个品牌的文本
            urls = ['http://changsha.taoche.com' + i['href'] for i in car_brands] #得到每个品牌的url
            return brands,urls
        return None
    except RequestException:
        print('请求出错')
        return None

def get_every_page_urls():
    try:
        target_urls = []
        target_brands = []  # 用来存放每辆二手车页面的链接 和品牌名称
        brands,urls = get_brands_urls()
        for brand, url in zip(brands, urls):
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                if len(soup.findAll('div', {'class': 'the-pages'})) == 0:
                    pages = 1
                else:
                    pages = int([page.text for page in soup.findAll('div', {'class': 'paging-box the-pages'})[0].findAll('a')][-2])
                time.sleep(1)
                for i in range(1, pages + 1):
                    target_brands.append(brand)
                    target_urls.append(url + '?page=' + str(i) + '#pagetage')
        return target_brands,target_urls
    except RequestException:
        return None

def get_detail():
    brand = []  # 品牌名称
    title = []  # 车型名称
    boarding_time = []  # 上牌时间
    driving_distance = []  # 行驶里程
    emission = []  # 二手车排放标准
    second_price = []  # 二手车价格
    first_price = []  # 新车价格
    count = 1
    target_brands ,target_urls =get_every_page_urls()
    for b,url in zip(target_brands,target_urls):
        response = requests.get(url,headers=headers)
        if response.status_code == 200 :
            soup = BeautifulSoup(response.text,'lxml')
            print('爬取第%s页...succeed!' %count)
            #统计每个页码二手车的数量
            N = len([i.findAll('a')[0]['title'] for i in soup.find_all('div',{'class':'item_main clearfix'})])
            try:
                #二手车品牌
                brands = (b + '-')*N
                print(brands)
                brand.extend(brands.split('-')[:-1])  # 创建相同数目的 该品牌 存入brand中
                print(brand)
                info = [i.findAll('span') for i in soup.findAll('div', {'class': 'item_main clearfix'})]
                # 二手车的名称
                title.extend([j[0].text for j in info])
                # 二手车的上牌时间
                boarding_time.extend([j[2].text for j in info])
                # 二手车的行驶里程
                driving_distance.extend(j[4].text for j in info)
                # 二手车的排量标准
                emission.extend([j[8].text for j in info])
                # 二手车的价格
                second_price.extend(j[9].text for j in info)
                # 新车价格
                first_price.extend([i.text.split()[2][:6]  for i in soup.findAll('p',{'class':'p_price'})])
            except IndexError:
                print('索引错误')
            time.sleep(0.5)
            count+=1
    data_car = pd.DataFrame({'Brand': brand, 'Name': title, 'Boarding_time': boarding_time,
                             'Driving_distance': driving_distance, 'Emission': emission,
                             'First_price': first_price, 'Second_price': second_price})

    data_car.to_csv('data_car.csv', index=False, encoding='utf-8')  # 保持到本地


def main():
    get_detail()

if __name__ == '__main__':
    main()


