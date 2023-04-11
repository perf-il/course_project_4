import utils as ut
from classes import HH, SuperJob, Vacancies, GetReguestError


keyword = input('Ведите ключевое слово, по которому будет производиться поиск вакансий: ')
path_hh = f'.\\requests\\{keyword}_hh.json'
path_sj = f'.\\requests\\{keyword}_sj.json'
print("Выберите площадку для поиска вакансий\n1. HeadHunter\n2. SuperJob\n3. Обе площадки")

# блок выбора площадки для парсинга
is_hh, is_sj = None, None
while is_hh is None:
    user_choose = input().lower().strip()
    if user_choose == '1' or user_choose == 'headhunter':
        is_hh = True
        is_sj = False
    elif user_choose == '2' or user_choose == 'superjob':
        is_sj = True
        is_hh = False
    elif user_choose == '3' or user_choose == 'обе площадки':
        is_hh = is_sj = True
    else:
        print('Введите число 1, 3 или 3 чтобы выберать один из следующих вариантов: \n'
              '1 - HeadHunter, 2 - SuperJob, 3 - Обе площадки')

# по-страничный парсинг на площаках, выбранных пользователем и сохранение результатов в файл .json (папка requests)
if is_hh:
    searh_hh = HH()
    print('*** HeadHanter ***')
    try:
        searh_hh.save_to_json(keyword=keyword, path=path_hh)
    except GetReguestError:
        is_hh = False
        print('Ошибка запроса')
if is_sj:
    searh_sj = SuperJob()
    print('*** SuperJob ***')
    try:
        searh_sj.save_to_json(keyword=keyword, path=path_sj)
    except GetReguestError:
        is_sj = False
        print('Ошибка запроса')

# инициализация экземпляров класса Vacancies
Vacancies.instantiate_from_json(path_hh=path_hh, path_sj=path_sj, is_hh=is_hh, is_sj=is_sj)

# блок проверки на наличие экземпляров класса Vacancies
if Vacancies.all:
    print(f'\nПо ключевому слову "{keyword}" найдено {len(Vacancies.all)} вакансий')
    print('\nВыберите действия со списком вакансий: \n1. Вывести на печать весь список '
          '\n2. Вывести на печать топ-N по зарплате \n3. Вывести на печать N случайных')
    user_select = []
    # блок вывода на печать в консоль данных, выбранных пользователем
    while True:
        user_choose = input().lower().strip()
        if user_choose == '1':
            all_vac = Vacancies.all
            ut.print_all_list(all_vac)
            for vac in all_vac:
                vac_dict = {'Площадка': vac.platform, 'Название': vac.name, 'URL': vac.url, 'Компания': vac.employer,
                            'Зарплата от': vac.salary_min, 'Зарплата до': vac.salary_max, 'Валюта': vac.currency}
                user_select.append(vac_dict)
            keyword_save = f'{keyword}_all'
            break
        elif user_choose == '2':
            all_sort_vac = Vacancies.sort_by_salary()
            n = ut.check_n(all_sort_vac)
            ut.print_top_n(all_sort_vac, n)
            for vac in all_sort_vac[:n]:
                vac_dict = {'Площадка': vac.platform, 'Название': vac.name, 'URL': vac.url, 'Компания': vac.employer,
                            'Зарплата от': vac.salary_min, 'Зарплата до': vac.salary_max, 'Валюта': vac.currency}
                user_select.append(vac_dict)
            keyword_save = f'{keyword}_top_{n}'
            break
        elif user_choose == '3':
            all_vac = Vacancies.all
            n = ut.check_n(all_vac)
            random_vac = ut.print_random_n(all_vac, n)
            for vac in random_vac:
                vac_dict = {'Площадка': vac.platform, 'Название': vac.name, 'URL': vac.url, 'Компания': vac.employer,
                            'Зарплата от': vac.salary_min, 'Зарплата до': vac.salary_max, 'Валюта': vac.currency}
                user_select.append(vac_dict)
            keyword_save = f'{keyword}_random_{n}'
            break
        else:
            print('Введите число 1, 3 или 3 чтобы выберать один из следующих вариантов: \n'
                  '1 - Вывести на печать весь список, 2 - Вывести на печать топ-N, 3 - Вывести на печать N случайных')

    print('\nВыберите формат для сохранения выборки: \n1. JSON\n2. CSV\n3. TXT')

    # блок сохранения данных в формате, выбранном пользователем, в папку resaults
    while True:
        user_choose = input().lower().strip()
        if user_choose == '1' or user_choose == 'json':
            ut.save_to_json(user_select, keyword_save)
            break
        elif user_choose == '2' or user_choose == 'csv':
            ut.save_to_csv(user_select, keyword_save)
            break
        elif user_choose == '3' or user_choose == 'txt':
            ut.save_to_txt(user_select, keyword_save)
            break
        else:
            print('Введите число 1, 3 или 3 чтобы выберать один из следующих форматов: \n'
                  '1 - JSON, 2 - CSV, 3 - TXT')

# вывод, если не нашлось ни одной вакансии по ключевому слову
else:
    print(f'\nПо ключевому слову "{keyword}" вакансий не найдено')

# блок удаления файлов из папки requests
print('Очистить истоию запросов? (да/нет)')
while True:
    user_choose = input().lower().strip()
    if user_choose == 'да':
        ut.clear_requests()
        break
    elif user_choose == 'нет':
        break
    else:
        print('Введите "да" или "нет"')
