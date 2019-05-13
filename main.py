from jobinja import *
from crawlRepo import *

import time
while True:
    try:
        crawl = jobinjaParser(page_limit=30)
        crawl.login()
        crawl.crawl(allowInsert=True)
    except Exception as err:
        logging.error('error occured at scrape {}'.format(err))
    finally:
        time.sleep(15 * 60)
