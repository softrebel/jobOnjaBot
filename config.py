import os
import logging
from botConfig import *

FORMAT = '%(asctime)-15s %(levelname)-9s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler('log.txt', 'a', 'utf-8')])

jobinja_login_url = "https://jobinja.ir/login/user?redirect_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D%2" \
                    "55B0%255D%3D%25D9%2588%25D8%25A8%25D8%258C%25E2%2580%258C%2520%25D8%25A8%25D8%25B1%25D9%2586%25D8%25A7%25D9%258" \
                    "5%25D9%2587%25E2%2580%258C%25D9%2586%25D9%2588%25DB%258C%25D8%25B3%25DB%258C%2520%25D9%2588%2520%25D9%2586%25D8" \
                    "%25B1%25D9%2585%25E2%2580%258C%25D8%25A7%25D9%2581%25D8%25B2%25D8%25A7%25D8%25B1%26filters%255Bkeywords%255D%25" \
                    "5B0%255D%3D%26filters%255Blocations%255D%255B0%255D%3D%25D8%25AA%25D9%2587%25D8%25B1%25D8%25A7%25D9%2586%26page" \
                    "%3D2%26sort_by%3Dpublished_at_desc&return_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D" \
                    "%255B0%255D%3D%25D9%2588%25D8%25A8%25D8%258C%25E2%2580%258C%2520%25D8%25A8%25D8%25B1%25D9%2586%25D8%25A7%25D9%2" \
                    "585%25D9%2587%25E2%2580%258C%25D9%2586%25D9%2588%25DB%258C%25D8%25B3%25DB%258C%2520%25D9%2588%2520%25D9%2586%25" \
                    "D8%25B1%25D9%2585%25E2%2580%258C%25D8%25A7%25D9%2581%25D8%25B2%25D8%25A7%25D8%25B1%26filters%255Bkeywords%255D%" \
                    "255B0%255D%3D%26filters%255Blocations%255D%255B0%255D%3D%25D8%25AA%25D9%2587%25D8%25B1%25D8%25A7%25D9%2586%26" \
                    "page%3D2%26sort_by%3Dpublished_at_desc"
jobinja_user_name = 'username'
jobinja_password = 'password'
default_path = 'jobinja.txt'
default_page = 1
css_add_item = 'o-listView__item o-listView__item--hasIndicator c-jobListView__item'
css_ad_title = 'c-jobListView__titleLink'
css_ad_meta = 'c-jobListView__metaItem'

base_url = 'https://jobinja.ir/jobs?filters%5Bkeywords%5D%5B0%5D=&filters%5Bjob_categories%5D%5B0%5D=%D9%88%D8%A8%D8' \
           '%8C%E2%80%8C+%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87%E2%80%8C%D9%86%D9%88%DB%8C%D8%B3%DB%8C+%D9%88+%D9%86%D' \
           '8%B1%D9%85%E2%80%8C%D8%A7%D9%81%D8%B2%D8%A7%D8%B1&filters%5Blocations%5D%5B0%5D=%D8%AA%D9%87%D8%B1%D8%A7' \
           '%D9%86&sort_by=published_at_desc&page='
first_page_ad_title_xpath = '//*[contains(@class,"o-listView__item o-listView__item--hasIndicator c-jobListView__item ")]' \
                            '//a[contains(@class,"c-jobListView__titleLink")]'
first_page_ad_meta_tags_xpath = '//*[contains(@class,"o-listView__itemComplementInfo c-jobListView__meta")]//li/span'
first_page_ad_link_xpath = '//*[contains(@class,"o-listView__item o-listView__item--hasIndicator c-jobListView__item ")]' \
                           '//a[contains(@class,"o-listView__itemIndicator o-listView__itemIndicator--noPaddingBox")]'

tags_priority = {
    'دسته‌بندی شغلی': 'category',
    'موقعیت مکانی': 'location',
    'نوع همکاری': 'work_type',
    'حداقل سابقه کار': 'minimum_experience',
    'حقوق': 'price',
    'مهارت‌های مورد نیاز': 'skills',
    'حداقل مدرک تحصیلی': 'minimum_degree',
}
dbConfig = {
    'user': 'sa',
    'password': 'test',
    'host': 'localhost',
    'database': 'job',
    'raise_on_warnings': True
}
default_website_id = 1

skill_mapping = {
    'php': 'PHP',
    'python': 'Python',
}

feed_message = '''
🔺 عنوان آگهی: {title}
🔻شرکت: {company}
🔹موقعیت مکانی: {location}
🔸نوع همکاری: {workType}
▫️حداقل سابقه کار: {minExperience}

🔵 شرح موقعیت شغلی:
{pureContent}

<a href="{link}">🔸 لینک آگهی</>

'''
# [🔸 لینک آگهی]({link})


start_message = '''
🔺سلام این ربات دستیار شما برای استخدام شدن هست
🔻فعلا جابینجا اضافه شده است
'''

menu_message = '''
🔻 برای نمایش آگهی ها، یکی از دسته بندی های زیر را انتخاب کنید
'''

paging_limit = 10

paging_mode = {
    'next': '<',  # because of order by desc
    'prev': '>'
}
paging_message = '''
🔻 برای نمایش صفحات بیشتر، دکمه های زیر را انتخاب کنید
'''

expiration_css = 'u-textCenter u-textSmall u-mB0'
sleep_time_for_page = 10

next_page_message = '''
⏭ صفحه بعدی
_____________________________
'''
