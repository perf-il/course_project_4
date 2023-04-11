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


class GetReguestError(Exception):
    """Класс-исключение для обработки ошибок при запросе к сайту"""
    def __init__(self, status_code, platform):
        self.status_code = status_code
        self.platform = platform

    def __str__(self):
        return f'Ошибка запроса к площадке {self.platform}. Код ошибки: {self.status_code}'


class HH(Engine):
    """Класс для парсинга платформы HeadHunter"""
    def get_request(self, keyword: str, page: int):
        """
        метод отправки запроса и получения информации с сайта https://api.hh.ru/vacancies
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param page: текущая страница с результатами
        :return: список с данными вакансий с текущей страницы или исключение GetReguestError
        """
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
            raise GetReguestError(response.status_code, 'HeadHunter')

    def get_vacancies(self, keyword: str, count: int = 1000):
        """
        метод для добавления всех найденных вакансий в общий список
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param count: общее количество вакансий (округляется кратно 100 в большую сторону), не более 1000
        :return: список с данными вакансий со всех страниц или исключение GetReguestError
        """
        pages = count // 100 if count % 100 == 0 else count // 100 + 1
        all_vacancies = []
        for page in range(pages):
            print('Парсинг страницы', page + 1)
            vacancies_per_page = self.get_request(keyword, page)
            if type(vacancies_per_page) is str:
                return vacancies_per_page
            all_vacancies.extend(vacancies_per_page)
        return all_vacancies

    def save_to_json(self, keyword: str, path: str):
        """
        метод для сохранения полученных вакансий в файл .json
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param path: путь, по которому будет сохранен файл .json
        :return: None
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.get_vacancies(keyword), f, ensure_ascii=False, indent=4)


class SuperJob(Engine):
    def get_request(self, keyword: str, page: int):
        """
        метод отправки запроса и получения информации с сайта https://api.superjob.ru/2.0/vacancies/
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param page: текущая страница с результатами
        :return: список с данными вакансий с текущей страницы или исключение GetReguestError
        """
        url = 'https://api.superjob.ru/2.0/vacancies/'
        token = 'v3.r.117534731.e77433e8cea532f82a8b4705bb091839d01c48e7.fa0b7fdd9d180f28a4fe7c99c13a1a1909b59dbd'
        headers = {
            'Host': 'api.superjob.ru',
            'X-Api-App-Id': token,
            'Authorization': 'Bearer r.000000010000001.example.access_token',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            "count": 100,
            "keyword": keyword,
            "page": page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['objects']
        else:
            raise GetReguestError(response.status_code, 'SuperJob')

    def get_vacancies(self, keyword: str, pages: int = 5):
        """
        метод для добавления всех найденных вакансий в общий список
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param pages: текущая страница с результатами
        :return: список с данными вакансий со всех страниц или исключение GetReguestError
        """
        all_vacancies = []
        for page in range(pages):
            print('Парсинг страницы', page + 1)
            vacancies_per_page = self.get_request(keyword, page)
            if type(vacancies_per_page) is str:
                return vacancies_per_page
            all_vacancies.extend(vacancies_per_page)
        return all_vacancies

    def save_to_json(self, keyword: str, path: str):
        """
        метод для сохранения полученных вакансий в файл .json
        :param keyword: слово/слова, которые необходимо найти в тексте вакансии
        :param path: путь, по которому будет сохранен файл .json
        :return: None
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.get_vacancies(keyword), f, ensure_ascii=False, indent=4)


class Vacancies:
    """Класс для представления вакансий. Атрибут класса all - список, который содержит все экземпляры класса"""
    all = list()

    @staticmethod
    def get_select_json_hh(path) -> list:
        """
        метод для выбора полей из файла .json с результатами парсинга с платформы HeadHunter,
        неообходимых для инициализации экземпляра класса
        :param path: путь до файла .json с результатами парсинга
        :return: список словарей
        """
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
        """
        метод для выбора полей из файла .json с результатами парсинга с платформы SuperJob,
        неообходимых для инициализации экземпляра класса
        :param path: путь до файла .json с результатами парсинга
        :return: список словарей
        """
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
        """
        метод инициализации экземпляра класса, данными из файлов .json с результатами парсинга для двух платформ.
        при вызове данного метода, атрибут класса all предварительно очищается
        :param path_hh: путь до файла .json с результатами парсинга с HeadHunter
        :param path_sj: путь до файла .json с результатами парсинга с SuperJob
        :param is_hh: указатель на платформу HH -> True - учитывать данные с платформы / False - не учитывать
        :param is_sj: указатель на платформу SJ -> True - учитывать данные с платформы / False - не учитывать
        :return: None
        """
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
        """
        метод сортировки экземпляров класса Vacancies внутри метода all.
        :param reverse: True - сортировка от большей зарплаты к меньшей / False - от меньшей к большей
        :return: атрибут класса all -> list
        """
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

    def __str__(self):
        str_salary_min = f'от {self.salary_min}' if self.salary_min else ''
        str_salary_max = f'до {self.salary_max}' if self.salary_max else ''
        str_salary = f'{str_salary_min} {str_salary_max} {self.currency}' \
            if self.salary_min or self.salary_max else 'не указана'
        return f'Вакансия с {self.platform}: {self.name} от компании {self.employer}\n{self.url}\nЗарплата {str_salary}'
