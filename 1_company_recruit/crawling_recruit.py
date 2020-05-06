import pandas as pd
import time
import re
import json
from selenium import webdriver
import requests 
import scrapy
from scrapy.http import TextResponse
from bs4 import BeautifulSoup
import pymongo
import configparser


class JobRecruit():
    
    def __init__(self, query='데이터사이언스'):
        self.query = query
        
        
    def get_jp_recruit(self):
        config = configparser.ConfigParser()
        config.read('login.ini')
        
        queries = ['데이터사이언스', '데이터엔지니어','데이터애널리스트', '데이터분석']
        for query in queries:
            print(query)
            start_url = 'https://www.jobplanet.co.kr/job_postings/search?_rs_act=index&_rs_con=search&_rs_element=see_more_job_postings_bottom&order_by=recent&query={}&page={}'.format(query, 1)
            login_url = 'https://www.jobplanet.co.kr/users/sign_in'
            login_data = {'user': {'email': config.get('section1', 'ID'), 
                               'password': config.get('section1', 'PW'), 
                               'remember_me':'true'}}

            session = requests.session()
            req = session.post(login_url, json=login_data)
            req = session.get(start_url)
            response=TextResponse(req.url, body=req.text, encoding='utf-8')
            link_ = response.xpath('//*[@id="search_form"]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div/div/div[1]/a/@href').extract()
            links = list(map(lambda x: 'https://www.jobplanet.co.kr' + x, link_))

            pages = response.xpath('//*[@id="search_form"]/div[2]/div[1]/div[2]/div[2]/div/article/a/text()').extract()
            pages = list(map(lambda x: int(x), pages))

            for page in pages:
                start_url = 'https://www.jobplanet.co.kr/job_postings/search?_rs_act=index&_rs_con=search&_rs_element=see_more_job_postings_bottom&order_by=recent&query={}&page={}'.format(query, page)
                req = session.get(start_url)
                response=TextResponse(req.url, body=req.text, encoding='utf-8')
                link_p = response.xpath('//*[@id="search_form"]/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div/div/div/div[1]/a/@href').extract()
                linkp = list(map(lambda x: 'https://www.jobplanet.co.kr' + x, link_p))
                links += linkp

            datas_ls = []
            for link in links:
                response = requests.get(link)
                dom = BeautifulSoup(response.content, 'html.parser')
                elements = dom.select('.block_content.block_job_posting > div.paragraph')

                datas = {}

                corp = dom.select('.company_name > h1 > a')[0].text
                if corp == '잡플래닛 매칭서비스':
                    continue
                else:
                    datas['company_name'] = corp
                    datas['company_name2'] = re.findall('[가-힣]+', corp.replace('(주)', '').replace(' ', '').replace('(', '').replace(')', ''))[0]
                try:
                    datas['industry'] = dom.select('.info > span:nth-child(1)')[0].text
                except:
                    datas['industry'] = '-'

                datas['title'] = dom.select('.ttl')[0]['title'].strip()
                datas['title2'] = dom.select('.ttl')[0]['title'].strip().replace(' ', '').replace('/', '').replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('&', '').replace('★', '')
                try:
                    datas['homepage'] = dom.select('.link_to')[0].text
                except:
                    datas['homepage'] = '-'

                period2 = dom.select('.date_box > span:nth-of-type(2)')[0].text
                period1 = dom.select('.date_box > span:nth-of-type(1)')[0].text
                datas['duration'] = period1 if (period1 == '상시채용') else period2 + " " + period1
                datas['registration'] = dom.select('.indate')[0].text.split(' ')[0]


                for element in elements:
                    try:
                        datas[element.select_one('h3').text] = element.select_one('div').text.strip().replace('\r', '').replace('\n', '')

                        if element.select_one('h3').text == '자격 요건':
                            if element.select('h4')[0].text == '핵심 직무 역량':
                                datas['ability'] = element.select('div')[0].text.strip().replace('\r', '').replace('\n', '')
                            if element.select('h4')[1].text == '우대 사항':
                                datas['treatment'] = element.select('div')[1].text.strip().replace('\r', '')

                        if datas in datas_ls:
                            continue
                        else:
                            datas_ls.append(datas)

                    except:
                        continue

        for ls_ in datas_ls:
            # 참고자료, 문의처 키 삭제
            if '참고자료' in ls_.keys():
                del ls_['참고자료']
            if '문의처' in ls_.keys():
                del ls_['문의처']
            if '자격 요건' in ls_.keys():
                del ls_['자격 요건']
                
            # 컬럼명은 영어로, 없는 키는 추가해서 '-'으로 채우기
            ls_['task'] = ls_.pop('주요 업무')

            ls_['introduction'] = ls_.pop('기업 소개') if '기업 소개' in ls_.keys() else '-'
            ls_['process'] = ls_.pop('채용절차') if '채용절차' in ls_.keys() else '-'
            ls_['welfare'] = ls_.pop('복리후생') if '복리후생' in ls_.keys() else '-'
            ls_['etc'] = ls_.pop('기타') if '기타' in ls_.keys() else '-'
            ls_['treatment'] = ls_['treatment'] if 'treatment' in ls_.keys() else '-'

        return datas_ls
    
    
    def get_wanted_recruit(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')

        driver = webdriver.Chrome(options=options)
        driver.get('https://www.wanted.co.kr/')
        driver.set_window_size(1920, 1080)

        nums = ['1024', '655', '1634']

        for num in nums:
            url = f'https://www.wanted.co.kr/wdlist/518/{num}?country=kr&job_sort=job.latest_order&years=0&locations=all'
            driver.get(url)
            time.sleep(1.3)
            lists = driver.find_elements_by_css_selector('ul.clearfix > li > div > a')
            links = []
            for list_ in lists:
                links.append(list_.get_attribute('href'))
            print(num)

        driver.quit()

        datas_ls = []

        for link in links:
            response = requests.get(link)
            dom = BeautifulSoup(response.content, 'html.parser')

            elements = dom.select('script#__NEXT_DATA__')[0].text
            element = json.loads(elements)

            id_ = link.split('/')[-1]
            content = element['props']['serverState']['jobDetail']['head'][id_]

            datas = {}

            datas['company_name'] = content['company_name']
            datas['company_name2'] = re.findall('[가-힣]+', content['company_name'].replace('(주)', '').replace(' ', '').replace('(', '').replace(')', ''))[0]
            
            datas['registration'] = content['confirm_time'][:10]
            datas['task'] = content['main_tasks'].replace('\n', ' ')
            datas['title'] = content['position']
            datas['title2'] = content['position'].replace(' ', '').replace('/', '').replace('-', '').replace('_', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace(',', '').replace('.', '').replace('&', '').replace('★', '')
            
            
            cons = content['jd'].split('\n\n')

            for con in cons:
                if '주요업무' in con:
                    ti = cons.index(con)
                elif '자격요건' in con:
                    abi = cons.index(con)
                elif '우대사항' in con:
                    tri = cons.index(con)
                elif '혜택 및 복지' in con:
                    wi = cons.index(con)

            datas['introduction'] = ' '.join(cons[:abi]).replace('\n', ' ').replace('  ', '')
            datas['task'] = ' '.join(cons[ti:abi]).replace('주요업무', '').replace('\n', ' ').replace('  ', '')       
            datas['ability'] = ' '.join(cons[abi:tri]).replace('자격요건', '').replace('\n', ' ').replace('  ', '')
            datas['treatment'] = ' '.join(cons[tri:wi]).replace('우대사항', '').replace('\n', ' ').replace('  ', '')
            datas['welfare'] = ' '.join(cons[wi:]).replace('혜택 및 복지', '').replace('\n', ' ').replace('  ', '')

            datas_ls.append(datas)
        
        return datas_ls
    
  
    def save_to_mongodb_j(self, section):
        config = configparser.ConfigParser()
        config.read('login.ini')
        user = config.get(section, 'ID')
        pwd = config.get(section, 'PW')
        ip = config.get(section, 'IP')
        
        account = f'mongodb://{user}:{pwd}@{ip}'
        server = pymongo.MongoClient(account, 27017) 
        db = server.jobplanet
        
        collection_c = db.recruit_jp
        datas = self.get_jp_recruit()
        ids = collection_c.insert(datas)
        
    
    def save_to_mongodb_w(self, section): 
        config = configparser.ConfigParser()
        config.read('login.ini')
        user = config.get(section, 'ID')
        pwd = config.get(section, 'PW')
        ip = config.get(section, 'IP')
        
        account = f'mongodb://{user}:{pwd}@{ip}'
        server = pymongo.MongoClient(account, 27017) 
        db = server.jobplanet
        
        collection_c = db.recruit_w
        datas = self.get_wanted_recruit()
        ids = collection_c.insert(datas)
