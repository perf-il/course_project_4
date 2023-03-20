from abc import abstractmethod, ABC
import requests


class Engine(ABC):
    @abstractmethod
    def get_request(self):
        pass

    @staticmethod
    def get_connector(file_name):
        """ Возвращает экземпляр класса Connector """
        pass


class HH(Engine):
    def get_request(self):
        pass


class SuperJob(Engine):
    def get_request(self):
        pass


url = 'https://api.hh.ru/'
par = {'per_page': '10', 'page': id}
a = requests.get(url, params=par)
print(a.json)