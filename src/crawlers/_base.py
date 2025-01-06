from abc import ABC,abstractmethod


class CralwerBase(ABC):
    @abstractmethod
    def crawl(self):
        pass

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def save(self):
        pass

    def run(self):
        self.crawl()
        self.extract()
        self.save()
