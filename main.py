from classes import HH, SuperJob, Vacancies

keyword = input('Ведите ключевое слово, по которому будет производиться поиск вакансий: ')
path_hh = f'.\\requests\\{keyword}_hh.json'
path_sj = f'.\\requests\\{keyword}_sj.json'
print("Выберите площадку для поиска вакансий\n1. HeadHunter\n2. SuperJob\n3. Обе площадки")

is_hh = None
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

if is_hh:
    searh_hh = HH()
    print('*** HeadHanter ***')
    searh_hh.save_to_json(keyword=keyword, path=path_hh)
if is_sj:
    searh_sj = SuperJob()
    print('*** SuperJob ***')
    searh_sj.save_to_json(keyword=keyword, path=path_sj)

Vacancies.instantiate_from_json(path_hh=path_hh, path_sj=path_sj, is_hh=is_hh, is_sj=is_sj)
all_sort_vac = Vacancies.sort_by_salary()
for i in range(20):
    print(Vacancies.all[i])