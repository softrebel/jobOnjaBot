import requests
from config import *
from bs4 import BeautifulSoup
import json, time
import mechanize
from http.cookiejar import CookieJar
from crawlRepo import *
from datetime import datetime, timedelta

class jobinjaParser():
    def __init__(self, repo=None, page_limit=3):
        self.page_limit = page_limit
        self.repo = repo if repo else crawlRepo()
        self.result = []
        self.first_page = default_page
        self.path = default_path
        self.webSiteID = default_website_id
        self.cj = CookieJar()
        self.br = mechanize.Browser()
        self.br.set_cookiejar(self.cj)

    def login(self):
        self.br.open(jobinja_login_url)
        self.br.select_form(nr=0)
        self.br.form['identifier'] = jobinja_user_name
        self.br.form['password'] = jobinja_password
        self.br.submit()

    def crawl(self, first_page=None, allowInsert=False):
        first_page = first_page if first_page else self.first_page
        for page in range(first_page, self.page_limit + 1):
            logging.info('scraping page {} started'.format(page))
            self.br.open(base_url + str(page))
            # page = requests.get(base_url + str(page))
            # soup = BeautifulSoup(page.content, 'html.parser')
            soup = BeautifulSoup(self.br.response().read().decode('utf-8'), 'html.parser')

            x = soup.find_all('li', class_=css_add_item)
            for item in x:
                out = {}
                out['title'] = item.find('a', class_=css_ad_title).get_text().strip()
                out['url'] = item.find('a', class_=css_ad_title).get('href')
                out['company'] = item.find('li', class_=css_ad_meta).get_text().strip()
                if self.repo.checkExistRecord(out, self.webSiteID):
                    logging.info('record already exist {}'.format(out['url']))
                    continue
                else:
                    result = self.pageParse(out['url'])
                    out.update(result)
                    self.result.append(out)
                    logging.info('parsing record completed')
                    if allowInsert:
                        flag = self.insertRecordToDb(out)
                        if flag:
                            logging.info('inserting record done')
                        else:
                            logging.info('inserting record Failed')
                    time.sleep(sleep_time_for_page)
        logging.info('scraping page {} done'.format(page))

    def pageParse(self, url):
        import re
        out = {}
        self.br.open(url)
        soup = BeautifulSoup(self.br.response().read().decode('utf-8'), 'html.parser')
        expiration = re.findall(r'\d+', soup.find('p', class_=expiration_css).get_text())
        if expiration:
            current_datetime = datetime.now()
            out['expiration_date'] = current_datetime + timedelta(days=int(expiration[0]))
        x = soup.find_all('li', class_='c-infoBox__item')
        tags_list = []
        for item in x:
            tags = item.find_all('span', class_='black')
            tag_values = []
            if len(tags) == 1:
                value = re.sub('\n|\r|\t|\s\s', '', tags[0].get_text().strip()).replace('تومان', 'تومان ').strip()
            else:
                for tag in tags:
                    tag_values.append(re.sub('\n|\r|\t|\s\s', '', tag.get_text().strip()))
                value = tag_values
            key = item.find(class_='c-infoBox__itemTitle').get_text()
            if key in tags_priority.keys():
                key = tags_priority[key]
                out[key] = value
            else:
                tags_list.append({key: value})
        out['tags'] = tags_list
        out['content'] = soup.find(class_='o-box__text').get_text()
        return out

    def saveToFile(self, mode='w', path=None):
        path = path if path else self.path
        with open(path, mode, encoding='utf-8') as f:
            f.write(json.dumps(self.result, ensure_ascii=False))

    def insertRecordToDb(self, record):
        if 'price' not in record:
            record['price'] = ''
        return self.repo.insertEntity(record, self.webSiteID)

    def insertResultToDb(self):
        for item in self.result:
            flag = self.insertRecordToDb(item)
            if flag:
                logging.info('inserting record done')
            else:
                logging.info('inserting record Failed')

    def getFeedBySkill(self, skill, paging_id=None, mode='next'):
        return self.repo.getRecordsBySkill(skill, paging_id, mode)
