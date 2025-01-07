from ._base import BaseCrawler
import httpx
import lxml.html
from src._core.utils import (
    save_cookies,
    get_xpath_first_element,
    remove_extra_spaces,
    load_cookies,
)
from pydantic import BaseModel
from lxml.html import Element
import logging
import time, random
import json, os


class JobinjaMeta(BaseModel):
    organization: str
    place: str
    contract: str | None


class JobinjaItem(BaseModel):
    title: str
    tags: list[str] = []


class JobinjaJob(BaseModel):
    job_id: str
    photo_url: str
    title: str
    link: str
    meta: JobinjaMeta
    description: str | None
    items: list[JobinjaItem] | None


class JobinjaCrawler(BaseCrawler):
    name: str = "jobinja"
    LOGIN_PAGE_URL: str = "https://jobinja.ir/login/user?redirect_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D%2"
    LOGIN_URL: str = "https://jobinja.ir/login/user"
    HOME_PAGE_URL: str = "https://jobinja.ir/jobs?filters%5Bjob_categories%5D%2"

    def __init__(
        self,
        username: str,
        password: str,
        client: httpx.Client | None = None,
        headers: dict | None = None,
        cookies_file: str | None = None,
        save_path: str = "data",
        *args,
        **kwargs,
    ):
        self.username: str = username
        self.password: str = password
        self._client: httpx.Client | None = client
        self.headers: dict | None = headers or {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://jobinja.ir",
            "priority": "u=0, i",
            "referer": "https://jobinja.ir/login/user?redirect_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D%2",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

        self.cookies_file: str = cookies_file or f"{self.name}.cookies"

        self.paginator_xpath = '//div[@class="paginator"]/ul/li[last()-1]/a/text()'  # xpath to get the last page number

        self._output: list[JobinjaJob] = []
        self.save_path = save_path
        super().__init__(*args, **kwargs)

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(follow_redirects=True)
        return self._client

    @client.setter
    def client(self, value: httpx.Client):
        self._client = value

    def request(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = {},
        params: dict = {},
        data: dict = {},
    ):
        for i in range(3):
            try:
                response = self.client.request(
                    method, url, headers=headers, params=params, data=data
                )
            except Exception as e:
                print(f"Error in url {url}")
                print(e)
                continue
        response.raise_for_status()
        return response

    # other methods and attributes

    def login(self):
        response = self.client.get(self.LOGIN_PAGE_URL, headers=self.headers)
        response.raise_for_status()
        tree = lxml.html.fromstring(response.content)
        input_tags = tree.xpath('//input[@name="_token"]/attribute::value')
        if input_tags and len(input_tags) > 0:
            _token = input_tags[0]
        data = {
            "redirect_url": "https://jobinja.ir/jobs?filters%5Bjob_categories%5D%2",
            "remember_me": "on",
            "identifier": self.username,
            "password": self.password,
            "_token": _token,
        }
        post_response = self.request(
            method="POST", url=self.LOGIN_URL, headers=self.headers, data=data
        )
        post_response.raise_for_status()
        save_cookies(self.client, self.cookies_file)

    def crawl(
        self,
        start_page: int = 1,
        end_page: int = 1,
        allow_calculate_end_page: bool = True,
    ) -> list[JobinjaJob]:
        load_cookies(self.client, self.cookies_file)

        jobs_url = "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1"
        page = start_page
        while page <= end_page:
            output: list[JobinjaJob] = []
            logging.info("Crawling page %s", page)
            jobs_params = {"page": page, "sort_by": "published_at_desc"}
            response = self.request(
                method="GET", url=jobs_url, headers=self.headers, params=jobs_params
            )
            response.raise_for_status()
            tree = lxml.html.fromstring(response.content)
            jobs = tree.xpath('//li[contains(@class,"o-listView__item__application")]')
            for item in jobs:
                logging.info("Crawling job %s", item)
                job = self.get_job(item)
                output.append(job)
            if allow_calculate_end_page:
                end_page = get_xpath_first_element(tree, self.paginator_xpath)
                if end_page is None:
                    break
                else:
                    end_page = int(end_page)

            page += 1
            rnd = random.randint(0, 5)
            logging.info(f"Page {page} done, waiting for {rnd} seconds")
            time.sleep(rnd)

            self._output += output
        return self._output

    def extract(self):
        pass

    def save(self, file_name: str = "jobinja.json"):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        file = os.path.join(self.save_path, file_name)

        with open(file, "w", encoding="utf-8") as f:
            json.dump(
                [x.model_dump_json() for x in self._output],
                f,
                ensure_ascii=False,
                indent=4,
            )

    def run(self):
        self.crawl()
        self.extract()
        self.save()

    def get_photo_url(self, node: Element) -> str | None:
        return get_xpath_first_element(
            node, '*/*/*/img[@class="o-listView__itemIndicatorImage"]/attribute::src'
        )

    def get_title(self, node: Element) -> str | None:
        return get_xpath_first_element(
            node,
            '*/*/h2[contains(@class,"o-listView__itemTitle c-jobListView__title")]/a/text()',
        )

    def get_link(self, node: Element) -> str | None:
        return get_xpath_first_element(
            node,
            '*/*/h2[contains(@class,"o-listView__itemTitle c-jobListView__title")]/a/attribute::href',
        )

    def get_job_meta(self, node: Element) -> JobinjaMeta:
        construction = "c-icon--construction"
        place = "c-icon--place"
        resume = "c-icon--resume"
        output = {}
        for li in node.xpath("div/div/ul/li"):
            classes = set(li.xpath("i")[0].classes)
            if construction in classes:
                spans = [
                    remove_extra_spaces(span.text.strip().replace("\n", " "))
                    for span in li.xpath("span")
                ]
                output["organization"] = "|".join(spans)
            elif place in classes:
                spans = [
                    remove_extra_spaces(span.text.strip().replace("\n", " "))
                    for span in li.xpath("span")
                ]
                output["place"] = "|".join(spans)
            elif resume in classes:
                spans = [
                    remove_extra_spaces(span.text.strip().replace("\n", " "))
                    for span in li.xpath("span/span")
                ]
                output["contract"] = "|".join(spans)

        return JobinjaMeta(**output)

    def get_job_id(self, url: str):
        return url.split("/jobs/")[-1].split("/")[0]

    def get_job(self, node: Element) -> JobinjaJob:
        photo_url: str = self.get_photo_url(node)
        title: str = self.get_title(node)
        link: str = self.get_link(node)
        job_id: str = self.get_job_id(link)
        meta: JobinjaMeta = self.get_job_meta(node)

        # get link and parse the job page
        response = self.request(method="GET", url=link, headers=self.headers)
        response.raise_for_status()
        tree = lxml.html.fromstring(response.content)
        description = tree.xpath('//div[contains(@class,"s-jobDesc")]')[
            0
        ].text_content()
        lis = tree.xpath("//ul[contains(@class,'c-infoBox')]/li")
        items: list[JobinjaItem] = []
        for li in lis:
            title = li.xpath("h4")[0].text.strip()
            tags = [
                remove_extra_spaces(span.text.strip().replace("\n", " "))
                for span in li.xpath('div[@class="tags"]/span')
            ]
            items.append(JobinjaItem(title=title, tags=tags))

        return JobinjaJob(
            job_id=job_id,
            photo_url=photo_url,
            title=title,
            link=link,
            meta=meta,
            description=description,
            items=items,
        )

    def __del__(self):
        if self.cookies_file:
            save_cookies(self.client, self.cookies_file)
        if self._client:
            self._client.close()
            del self._client
        del self
