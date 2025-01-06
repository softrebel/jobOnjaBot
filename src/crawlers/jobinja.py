from ._base import BaseCrawler

class JobinjaCrawler(BaseCrawler):
    name = 'jobinja'
    # other methods and attributes

    def login(self):
        # login code
        pass


    def crawl(self):
        pass

    def extract(self):
        pass

    def save(self):
        pass

    def run(self):
        self.crawl()
        self.extract()
        self.save()

