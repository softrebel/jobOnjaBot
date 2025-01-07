from ._base import BaseCrawler
import httpx
import lxml.html
from src._core.utils import (
    save_cookies,
    get_xpath_first_element,
    remove_extra_spaces,
    load_cookies,
    get_hash,
)
from pydantic import BaseModel
from lxml.html import Element
import logging
import time, random
import json, os
from src._core.schemas import JobCreate, JobMetaCreate, JobInput, CompanyCreate
from lxml.etree import tostring
from src.services.company_services import create_company, get_company_by_name
from src.services.job_platform_services import get_job_platform_by_name
from prisma.models import Company, Job
from src.services.job_services import create_job, get_job_by_link, get_job_by_job_id
import os


class JobinjaCrawledLink(BaseModel):
    job_id: str
    photo_url: str
    title: str
    link: str


class JobinjaCrawler(BaseCrawler):
    name: str = "jobinja"
    LOGIN_PAGE_URL: str = "https://jobinja.ir/login/user?redirect_url=https%3A%2F%2Fjobinja.ir%2Fjobs%3Ffilters%255Bjob_categories%255D%2"
    LOGIN_URL: str = "https://jobinja.ir/login/user"
    HOME_PAGE_URL: str = "https://jobinja.ir/jobs/category/it-software-web-development-jobs/%D8%A7%D8%B3%D8%AA%D8%AE%D8%AF%D8%A7%D9%85-%D9%88%D8%A8-%D8%A8%D8%B1%D9%86%D8%A7%D9%85%D9%87-%D9%86%D9%88%DB%8C%D8%B3-%D9%86%D8%B1%D9%85-%D8%A7%D9%81%D8%B2%D8%A7%D8%B1"

    def __init__(
        self,
        username: str,
        password: str,
        start_url: str | None = None,
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
        self.start_url: str = start_url or self.HOME_PAGE_URL
        self.cookies_file: str = cookies_file or f"{self.name}.cookies"

        self.paginator_xpath = '//div[@class="paginator"]/ul/li[last()-1]/a/text()'  # xpath to get the last page number

        self.save_path = save_path
        self._crawled_links: list[str] = []
        self._extracted_jobs: list[JobInput] = []
        self._saved_jobs: list[Job] = []

        self.job_platform = get_job_platform_by_name(self.name)
        if not self.job_platform:
            raise ValueError(f"Job platform {self.name} not found")
        super().__init__(*args, **kwargs)

    @property
    def saved_jobs(self) -> list[Job]:
        return self._saved_jobs

    @property
    def extracted_jobs(self) -> list[JobInput]:
        return self._extracted_jobs

    @property
    def crawled_links(self) -> list[str]:
        return self._crawled_links

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

    def request_with_bypass_cdn(
        self,
        method: str = "GET",
        url: str = "",
        headers: dict = {},
        params: dict = {},
        data: dict = {},
    ):
        response = self.request(
            method=method, url=url, headers=headers, params=params, data=data
        )
        content = response.text
        if "error-section__title" in content:
            hash = get_hash(content)
            if not hash:
                logging.error("hash error")
                return None
            headers = {"cookie": f"__arcsjs={hash};"}
            response = self.request(
                method=method, url=url, headers=headers, params=params, data=data
            )
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

    def crawl_job_link(self, node: Element) -> str | None:
        return get_xpath_first_element(
            node,
            '*/*/h2[contains(@class,"o-listView__itemTitle c-jobListView__title")]/a/attribute::href',
        )

    def _check_link_exists(self, link: str) -> bool:
        return get_job_by_link(link) is not None

    def crawl(
        self,
        start_page: int = 1,
        end_page: int = 1,
        allow_calculate_end_page: bool = True,
    ) -> list[str]:
        load_cookies(self.client, self.cookies_file)
        crawld_links: list[str] = []
        jobs_url = self.start_url
        page = start_page
        cnt = 0
        while page <= end_page:
            cnt += 1
            logging.info("Crawling page %s", page)
            jobs_params = {"page": page, "sort_by": "published_at_desc"}
            response = self.request_with_bypass_cdn(
                method="GET", url=jobs_url, headers=self.headers, params=jobs_params
            )
            response.raise_for_status()
            tree = lxml.html.fromstring(response.content)
            jobs = tree.xpath('//li[contains(@class,"o-listView__item__application")]')
            for item in jobs:
                logging.info(f"Crawling {cnt} job link ")
                link: str = self.crawl_job_link(item)
                exists: bool = self._check_link_exists(link)
                if exists:
                    logging.info(f"Job link already exists: {link}")
                    continue
                crawld_links.append(link)
            if allow_calculate_end_page:
                end_page = get_xpath_first_element(tree, self.paginator_xpath)
                if end_page is None:
                    break
                else:
                    end_page = int(end_page)
            page += 1
            rnd = random.randint(0, 2)
            logging.info(f"Page {page} done, waiting for {rnd} seconds")
            time.sleep(rnd)

        self._crawled_links += crawld_links
        return self._crawled_links

    def extract_job_title(self, node: Element) -> str | None:
        return get_xpath_first_element(
            node,
            '//div[@class="c-jobView__titleText"]/h1/text()',
        )

    def extract_job_metas(self, job_id: str, node: Element) -> list[JobMetaCreate]:
        lis = node.xpath("//ul[contains(@class,'c-infoBox')]/li")
        output: list[JobMetaCreate] = []
        for li in lis:
            items: list[JobMetaCreate] = []
            key = li.xpath("h4")[0].text.strip()
            tags = [
                remove_extra_spaces(span.text.strip().replace("\n", " "))
                for span in li.xpath('div[@class="tags"]/span')
            ]
            for tag in tags:
                items.append(JobMetaCreate(job_id=job_id, key=key, value=tag))
            output += items

        return output

    def extract_job_id(self, url: str):
        return url.split("/jobs/")[-1].split("/")[0]

    def extract_job_description(self, node: Element) -> str:
        return (
            node.xpath('//div[contains(@class,"s-jobDesc")]')[0].text_content().strip()
        )

    def extract_job_body(self, node: Element) -> str:
        el = node.find("body")
        body = tostring(el).decode("utf-8")
        return body

    def extract_company_name(self, node: Element) -> str:
        return node.xpath("//h2[@class='c-companyHeader__name']")[0].text_content()

    def extract_company_description(self, node: Element) -> str:
        description: str = "\n".join(
            [
                x.text_content().strip()
                for x in node.xpath("//span[@class='c-companyHeader__metaItem']")
            ]
        )
        return description

    def extract_company_photo_url(self, node: Element) -> str | None:
        return node.xpath("//img[@class='c-companyHeader__logoImage']/attribute::src")[
            0
        ]

    def extract_company_link(self, node: Element) -> str | None:
        return node.xpath("//a[@class='c-companyHeader__logoLink']/attribute::href")[0]

    def extract_company(self, node: Element) -> CompanyCreate:
        name: str = self.extract_company_name(node)
        description: str = self.extract_company_description(node)
        photo_url: str = self.extract_company_photo_url(node)
        link: str = self.extract_company_link(node)

        company = CompanyCreate(
            description=description,
            job_platform_id=self.job_platform.id,
            link=link,
            name=name,
            photo_url=photo_url,
        )
        return company

    def extract_job(self, link: str, node: Element) -> JobCreate:
        title: str = self.extract_job_title(node)
        job_id: str = self.extract_job_id(link)
        job_metas: list[JobMetaCreate] = self.extract_job_metas(
            job_id=job_id, node=node
        )
        description: str = self.extract_job_description(node)
        body: str = self.extract_job_body(node)

        # get company
        company = self.extract_company(node)

        return JobInput(
            job_id=job_id,
            title=title,
            link=link,
            description=description,
            body=body,
            job_platform_id=self.job_platform.id,
            job_metas=job_metas,
            company=company,
        )

    def _check_job_exists(self, job_id: str) -> bool:
        return get_job_by_job_id(job_id) is not None

    def extract(self):
        _extracted_jobs: list[JobInput] = []
        for link in self.crawled_links:
            try:
                logging.info(f"Extracting job {link}")
                response = self.request_with_bypass_cdn(
                    method="GET", url=link, headers=self.headers
                )
                response.raise_for_status()
                tree = lxml.html.fromstring(response.content)

                job_id: str = self.extract_job_id(link)
                exists: bool = self._check_job_exists(job_id)
                if exists:
                    logging.info(f"Job id {job_id} already exists")
                    continue
                job = self.extract_job(link=link, node=tree)
                _extracted_jobs.append(job)
            except Exception as e:
                logging.error(f"Error in extracting job {link}")
                logging.error(e)
            finally:
                rnd = random.randint(0, 5)
                logging.info(f"waiting for {rnd} seconds")
                time.sleep(rnd)

        self._extracted_jobs = _extracted_jobs

    def save_job(self, job: JobInput) -> Job:
        company = get_company_by_name(job.company.name)
        if not company:
            company = create_company(job.company)
        job_create = JobCreate(
            job_id=job.job_id,
            title=job.title,
            description=job.description,
            link=job.link,
            photo_url=job.company.photo_url,
            body=job.body,
            company_id=company.id,
            job_platform_id=job.job_platform_id,
            job_metas=job.job_metas,
        )
        job = create_job(job_create)
        return job

    def save(self):
        for job in self.extracted_jobs:
            logging.info("Saving job %s", job.title)
            job: Job = self.save_job(job)
            self._saved_jobs.append(job)

    def run(self, start_page=1, end_page=1, allow_calculate_end_page=True):
        logging.info(f"Starting {self.name} crawler")
        self.crawl(
            start_page=start_page,
            end_page=end_page,
            allow_calculate_end_page=allow_calculate_end_page,
        )
        logging.info(f"Extracting {self.name} jobs")
        self.extract()
        logging.info(f"Saving {self.name} jobs")
        self.save()

    def __del__(self):
        if self.cookies_file:
            save_cookies(self.client, self.cookies_file)
        if self._client:
            self._client.close()
            del self._client
        del self
