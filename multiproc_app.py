import multiprocessing
from random import randint
from timeit import default_timer as timer

NUM_CORE = multiprocessing.cpu_count()


def chunk_list(lst, parts=NUM_CORE):
    step = int(len(lst) / parts)
    for i in range(parts - 1):
        yield lst[i * step:(i + 1) * step]  # тут еще и на итератор можно переделать, вместо слайсов
    else:
        i += 1
        yield lst[i * step:]


def worker(value):
    res = sorted(value)
    return res


def main():
    # почитал еще про методы запуска (spawn, fork, forkserver)
    # т.к. я под виндой - то мне ничего кроме spawn недоступно, а виртуалку ради такого я разворачивать не стал,
    # поэтому писал через with - удобней.

    start_time = timer()
    some_list = [randint(1, 100) for x in range(100_000_000)]
    print(f'create list: {timer() - start_time}')
    with multiprocessing.Pool(NUM_CORE) as pool:  # NUM_CORE в данном случае особо не нужен, по дефолту os.cpu_count()
        # почитал про возможные проблемы с памятью.
        # Для таких ситуаций есть imap, но тогда worker надо переписывать под работу с генератором
        # нашел еще async всякие (map_async например) - тут они ни к чему
        sorted_lists = []

        start_time = timer()
        for sorted_list in pool.map(worker, chunk_list(some_list)):  # знаю про chunksize, решил так
            sorted_lists.extend(sorted_list)
        result = sorted(sorted_lists)  # делать с ним ничего не стал, не выводить же 20кк записей)
    print(f'multicore sort: {timer() - start_time}')

    start_time = timer()
    result = sorted(some_list)
    print(f'single-core sort: {timer() - start_time}')


if __name__ == '__main__':
    main()


