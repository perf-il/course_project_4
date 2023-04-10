from abc import abstractmethod, ABC
import requests
import json


class Engine(ABC):
    @abstractmethod
    def get_request(self, keyword, page):
        pass

    @staticmethod
    def get_connector(file_name):
        """ Возвращает экземпляр класса Connector """
        pass


class HH(Engine):

    def get_request(self, keyword: str, page: int) -> list | str:
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": keyword,
            "page": page,
            "per_page": 100,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()['items']
        else:
            return f'Ошибка запроса {response.status_code}'

    def get_vacancies(self, keyword: str, count: int = 1000):
        pages = count // 100 if count % 100 == 0 else count // 100 + 1
        all_vacancies = []
        for page in range(pages):
            print('Парсинг страницы', page + 1)
            vacancies_per_page = self.get_request(keyword, page)
            if type(vacancies_per_page) is str:
                return vacancies_per_page
            all_vacancies.extend(vacancies_per_page)
        return all_vacancies

    def save_to_json(self, keyword):
        path = f'.\\requests\\{keyword}.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.get_vacancies(keyword), f, ensure_ascii=False, indent=4)


class SuperJob(Engine):
    def get_request(self, keyword, page):
        url = 'https://api.superjob.ru/2.0/vacancies/'
        token = 'v3.r.117534731.e77433e8cea532f82a8b4705bb091839d01c48e7.fa0b7fdd9d180f28a4fe7c99c13a1a1909b59dbd'
        headers = {
            'Host': 'api.superjob.ru',
            'X-Api-App-Id': token,
            'Authorization': 'Bearer r.000000010000001.example.access_token',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            #"keywords": [{"keys": keyword, "srws": 1}],
            "count": 100,
            "keyword": keyword,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        return response


a = HH()
b = SuperJob()
n = 0
for i in range(6):
    c = b.get_request('python', i).json()
    for j in c['objects']:
        print(j['profession'])
        n += 1
print(n)





#all_vac = a.save_to_json('python')

