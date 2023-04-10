from abc import abstractmethod, ABC
import requests
import json

import utils as ut


class Engine(ABC):
    @abstractmethod
    def get_request(self, keyword: str, page: int) -> list | str:
        pass

    @staticmethod
    def get_connector(file_name):
        """ Возвращает экземпляр класса Connector """
        pass


class HH(Engine):

    def get_request(self, keyword, page):
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
        path = f'.\\requests\\{keyword}_hh.json'
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
            # "keywords": [{"keys": keyword, "srws": 1}],
            "count": 100,
            "keyword": keyword,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['objects']
        else:
            return f'Ошибка запроса {response.status_code}'

    def get_vacancies(self, keyword: str, pages: int = 5):
        all_vacancies = []
        for page in range(pages):
            print('Парсинг страницы', page + 1)
            vacancies_per_page = self.get_request(keyword, page)
            if type(vacancies_per_page) is str:
                return vacancies_per_page
            all_vacancies.extend(vacancies_per_page)
        return all_vacancies

    def save_to_json(self, keyword):
        path = f'.\\requests\\{keyword}_sj.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.get_vacancies(keyword), f, ensure_ascii=False, indent=4)


class Vacancies:
    all = list()

    @staticmethod
    def get_select_json_hh(path) -> list:
        all_select_hh = list()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            for vac in data:
                select_hh = dict()
                select_hh['name'] = vac["name"]
                if vac["salary"]:
                    select_hh['currency'] = ut.get_specific_code(vac["salary"]["currency"])
                    if select_hh['currency'] and select_hh['currency'] != 'RUR':
                        select_hh['salary_min'] = ut.convert_to_rubles(vac["salary"]["from"], select_hh['currency'])
                        select_hh['salary_max'] = ut.convert_to_rubles(vac["salary"]["to"], select_hh['currency'])
                        select_hh['currency'] = 'RUR'
                    else:
                        select_hh['salary_min'] = vac["salary"].get("from")
                        select_hh['salary_max'] = vac["salary"].get("to")
                else:
                    select_hh['salary_min'] = select_hh['salary_max'] = select_hh['currency'] = None
                select_hh['url'] = vac["alternate_url"]
                select_hh['employer'] = vac["employer"]["name"]
                select_hh['platform'] = 'HeadHunter'
                all_select_hh.append(select_hh)
        return all_select_hh

    @staticmethod
    def get_select_json_sj(path) -> list:
        all_select_sj = list()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            for vac in data:
                select_sj = dict()
                select_sj['name'] = vac["profession"]
                select_sj['salary_min'] = vac["payment_from"]
                select_sj['salary_max'] = vac["payment_from"]
                select_sj['currency'] = vac["currency"] if vac["currency"] != 'rub' else 'RUR'
                select_sj['url'] = vac["link"]
                select_sj['employer'] = vac["firm_name"]
                select_sj['platform'] = 'SuperJob'
                all_select_sj.append(select_sj)
        return all_select_sj

    @classmethod
    def instantiate_from_json(cls, path_hh, path_sj, is_hh=True, is_sj=True):
        cls.all.clear()
        if is_hh:
            for vac_hh in cls.get_select_json_hh(path_hh):
                cls(vac_hh['name'], vac_hh['salary_min'], vac_hh['salary_max'],
                    vac_hh['currency'], vac_hh['url'], vac_hh['employer'], vac_hh['platform'])
        if is_sj:
            for vac_sj in cls.get_select_json_sj(path_sj):
                cls(vac_sj['name'], vac_sj['salary_min'], vac_sj['salary_max'],
                    vac_sj['currency'], vac_sj['url'], vac_sj['employer'], vac_sj['platform'])

    @classmethod
    def sort_by_salary(cls, reverse=True):
        cls.all.sort(key=lambda x: x.salary_max if x.salary_max else 0, reverse=reverse)
        cls.all.sort(key=lambda x: x.salary_min if x.salary_min else 0, reverse=reverse)
        return cls.all

    def __init__(self, name, salary_min, salary_max, currency, url, employer, platform):
        self.name = name
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.currency = currency
        self.url = url
        self.employer = employer
        self.platform = platform
        Vacancies.all.append(self)

    # def __ge__(self, other):
    #     if self.salary_min and other.salary_min:
    #         return self.salary_min >= other.salary_min

    def __str__(self):
        str_salary_min = f'от {self.salary_min}' if self.salary_min else ''
        str_salary_max = f'до {self.salary_max}' if self.salary_max else ''
        str_salary = f'{str_salary_min} {str_salary_max} {self.currency}' if self.salary_min or self.salary_max else 'не указана'
        return f'Вакансия с {self.platform}: {self.name} - ({self.url}) Зарплата {str_salary}'

Vacancies.instantiate_from_json('.\\requests\\python.json', '.\\requests\\python_sj.json')
all_currency = set()
for i in Vacancies.sort_by_salary(reverse=True):
    all_currency.add(i.currency)
    #print(i.name, i.salary_min, i.salary_max, i.currency)
print(all_currency)
for i in range(15):
    print(Vacancies.all[i])
