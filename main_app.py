from pathlib import Path
import json
import traceback
from filters import *


def load_config():
    # Про валидацию конфига речи не было - поэтому писать лишнего не буду.
    # Считаю, что:
    #   - он есть
    #   - параметры в нужном порядке и они валидные
    #   - и вообще с ним все ок, как и со всем остальным, если не сказано иначе
    # ну а так можно добавить проверки:
    #   - наличие папок для данных
    #   - это именно папки, а не файл
    #   - в них есть данные (входящие по-крайней мере)
    #   - наличие фильтров (сравнить конфиг и globals() например)
    #   - ...

    def get_param_value(string):
        return string.split('=')[1].strip()

    config_file = Path('config.txt')
    with config_file.open(mode='r', encoding='utf8') as f:
        input_data_dir = Path(get_param_value(f.readline()))
        output_data_dir = Path(get_param_value(f.readline()))
        filters_to_apply = [v.strip() for v in get_param_value(f.readline()).split(',')]

    return input_data_dir, output_data_dir, filters_to_apply


def validate_format(input_data, file_name):
    # Валидация формата json.
    # Для больших объемов можно написать генератор,
    # который будет через readline (ну или чанками) выдавать связку ключ-значение из файла.
    # Ее можно сразу прогонять по всем фильтрам,
    # при условии, что фильтры не работают со всеми данными (например, значение больше среднего во всем файле).
    # В общем варианты есть. Еще можно всякие marshmallow/pydantic подключить.

    result = None
    try:
        result = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(f'Некорректный формат данных в файле {file_name}. Ожидается JSON.')

    return result


def validate_data(input_data, file_name):
    # Валидация данных (ключ-значение).
    # Что-то более серьезное, например обрабатывать валидные строчки, а не пропускать весь файл - можно
    # написать свой валидатор или подключать библиотеки выше.

    result = None
    try:
        # По идее нам json.loads уже сделал словарь,
        # но для валидации ключ-значение надо что-то еще, ибо можем получить тот же список на входе.
        # Ожидаем ошибку в _fail_5.json - там валидный json-массив, а мы ждем словарь.
        #
        # Можно свой класс JSONDecode написать, или функцию для object_hook
        # чтобы валидировать данные прямо во время валидации формата.
        #
        # Я решил не городить, т.к. dict() хватит для задачи
        # и разделить валидации на две части для наглядности кода,
        # ну и чтобы допиливать следующие гипотетические хотелки было проще
        result = dict(input_data)
    except TypeError as e:
        print(f'Некорректные данные в файле {file_name}. Ожидаются пары "<ключ>: <значение>" в формате JSON.')

    return result


def filter_dict(filters, dct, file_name):
    # Снова уточню, что такой подход приемлем,
    # если фильтры не работают со всем набором данных (по типу среднего/медианы).
    #
    # Все таки весь набор - это больше аналитика, а не фильтрация, поэтому думаю, что все норм.

    result = dict()
    for k, v in dct.items():
        for filter_name in filters:
            if filter_name:  # на случай пустого списка фильтров
                # не самый безопасный вариант:
                # может сломаться, если напишем не ту функцию в конфиге
                # или перетрем функцию в процессе (всякое бывает)
                # НО! как я написал выше - считаю, что конфиг/код без таких вот багов
                filter_func = globals()[filter_name]
                try:
                    k, v = filter_func(k, v)
                    if not all((k, v)):  # если фильтр не пропустил - идем к следующей паре ключ-значение
                        break
                except Exception as e:
                    print(f'Возникла ошибка "{e}" при работе фильтра "{filter_name}" в файле "{file_name}". Работа будет прекращена. Детали:'
                          f'\nkey={k!r}'
                          f'\nvalue={v!r}'
                          f'\n\n{traceback.format_exc()}')
                    raise SystemExit(1)
        else:
            result.update({k: v})
    return result


def main():
    input_data_dir, output_data_dir, filters_to_apply = load_config()
    # Фильтр расширения можно конечно убрать,
    # но я это считаю бонусом, т.к. разные редакторы и IDE могут подчеркивать
    # некорректный синтаксис, что может уменьшить кол-во ошибок.
    # Хотя подозреваю, что расчет на программное заполнение, а не на то, что кто-то руками будет файл наполнять
    for input_file in input_data_dir.glob('*.json'):
        file_name = input_file.name
        output_file = output_data_dir / input_file.name
        with input_file.open(mode='r', encoding='utf8') as in_f:
            raw_data = validate_format(in_f.read(), file_name)
            if not raw_data:  # если возникла предвиденная ошибка - продолжаем со следующим файлом
                continue

            raw_dict = validate_data(raw_data, file_name)
            if not raw_dict:
                continue

            # тут мы можем получить пустой словарь как итог всех фильтров
            # поэтому в итоге может быть пустой файл (точнее там будет просто {})
            filtered_dict = filter_dict(filters_to_apply, raw_dict, file_name)
            with output_file.open(mode='w', encoding='utf8') as out_f:
                json.dump(filtered_dict, out_f)


if __name__ == '__main__':
    main()
