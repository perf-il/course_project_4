import requests


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

