import os
import requests
import json
import csv
from random import sample


def convert_to_rubles(value: int | float, cod: str) -> int | float | None:
    """
    Функция для перевода суммы в рубли по коду валюты
    :param value: сумма в валюте
    :param cod: код валюты
    :return: сумму в рублях или None при ошибке перевода
    """
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    if response.status_code == 200:
        data = response.json()
    else:
        print(f'Ошибка запроса конвертации. Код ошибки: {response.status_code}')
        return
    try:
        k = data['Valute'][cod]['Value'] / data['Valute'][cod]['Nominal']
        return value * k if value else None
    except KeyError:
        print('Неизвестный код валюты, конвертация невозможна')


def get_specific_code(cod: str) -> str:
    """
    Функция для унификации кодов валют
    :param cod: исходный код валюты
    :return: унифицированный код валюты (при отсутствии кода возвращает RUR)
    """
    if cod:
        if cod.lower() in ['rub', 'руб', 'руб.']:
            return 'RUR'
        elif cod == 'BYR':
            return 'BYN'
        else:
            return cod
    else:
        return 'RUR'


def print_all_list(all_list: list) -> None:
    """
    Функция для печати всех элементов списка в консоль
    :param all_list: исходный список
    :return: None
    """
    for i, j in enumerate(all_list):
        print(f"{'*' * 42}Вакансия №{i + 1}{'*' * 42}")
        print(j)


def print_top_n(all_list: list, n: int) -> None:
    """
    Функция для печати первых N элементов списка в консоль
    :param all_list: исходный список
    :param n: кол-во элементов, которые выводятся на печать
    :return: None
    """
    print_all_list(all_list[:n])


def print_random_n(all_list: list, n: int) -> list:
    """
    Функция для печати случайных N элементов списка в консоль
    :param all_list: исходный список
    :param n: кол-во элементов, которые выводятся на печать
    :return: список случайных вакансий
    """
    random_list = sample(all_list, k=n)
    print_all_list(random_list)
    return random_list


def get_path_to_save() -> str:
    """
    Функция создает дерикторию пользователя
    :return: путь до дериктории
    """
    user_name = input('Введите ваше имя: ').capitalize().strip()
    user_dir_path = os.path.join('resaults', f'{user_name}')
    if not os.path.isdir(user_dir_path):
        os.mkdir(user_dir_path)
    return user_dir_path


def save_to_json(user_select: list, keyword) -> None:
    """
    Функция для сохранения списка в формате json в папке пользователя внутри дириктории resaults
    :param user_select: список пользователя
    :param keyword: имя списка
    :return: None
    """
    path = os.path.join(get_path_to_save(), f'{keyword}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(user_select, f, indent=4, ensure_ascii=False)
    print(f'Результаты сохранены в формате .json\nПуть до файла: {path}')


def save_to_txt(user_select: list, keyword) -> None:
    """
    Функция для сохранения списка в формате txt в папке пользователя внутри дириктории resaults
    :param user_select: список пользователя
    :param keyword: имя списка
    :return: None
    """
    path = os.path.join(get_path_to_save(), f'{keyword}.txt')
    with open(path, 'w', encoding='utf-8') as f:
        for i, j in enumerate(user_select):
            print(f'{i + 1}. ', end='', file=f)
            for k, v in j.items():
                print(f'{k}: {v} ', end='', file=f)
            print('', file=f)
    print(f'Результаты сохранены в формате .txt\nПуть до файла: {path}')


def save_to_csv(user_select: list, keyword) -> None:
    """
    Функция для сохранения списка в формате csv в папке пользователя внутри дириктории resaults
    :param user_select: список пользователя
    :param keyword: имя списка
    :return: None
    """
    path = os.path.join(get_path_to_save(), f'{keyword}.csv')
    with open(path, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(user_select[0].keys())
        for dict_item in user_select:
            csv_writer.writerow(dict_item.values())
    print(f'Результаты сохранены в формате .csv\nПуть до файла: {path}')


def clear_requests() -> None:
    """
    Удаляет файлы из requests
    :return: None
    """
    clearing_dir = os.path.join('requests')
    for f in os.listdir(clearing_dir):
        os.remove(os.path.join(clearing_dir, f))


def check_n(user_list: list) -> int:
    """
    Функция для получения и проверки числа вакансий для вывода
    :param user_list: список всех вакансий
    :return: целое число вакансий для вывода
    """
    while True:
        n = input(f'Сколько вакансий вывести (введите число от 0 до {len(user_list)}): ')
        try:
            if 0 < int(n) <= len(user_list):
                return int(n)
        except ValueError:
            print('Неккоректный ввод: число не может быть отрицательным или первышать длину списка')
        else:
            print('Неккоректный ввод: введено не число')
