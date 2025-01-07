from src.crawlers.jobinja import JobinjaCrawler
from src._core import project_configs
import os
from src._core.database import prisma
from src._core.utils import load_cookies

prisma.connect()


cookie_file = f"{project_configs.CONFIG_PATH}{os.sep}jobinja_cookies.json"
crawler = JobinjaCrawler(
    username=project_configs.JOBINJA_USERNAME,
    password=project_configs.JOBINJA_PASSWORD,
    cookies_file=cookie_file,
)
# crawler.login()
load_cookies(crawler.client, cookie_file)
crawler._crawled_links = [
    "https://jobinja.ir/companies/yadakchi-1/jobs/AdCk/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-back-end-net-%D8%AF%D8%B1-%DB%8C%D8%AF%DA%A9%DA%86%DB%8C?_ref=16&_t=352e3131322e3131362e313935"
]
crawler.extract()
crawler.save()

# crawler.run(allow_calculate_end_page=False)
