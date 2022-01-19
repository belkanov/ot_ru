_DEFAULT_FALSE = (False, False)

# Такой формат выбрал только потому, что второй фильтр из задачи меняет значение
# это так же может повлиять на дальнейшие фильтры (если вдруг им будет важен регистр)
# иначе бы сократил до возврата одного True/False

# ### VALUE FILTER EXAMPLE ###
# def value_<condition_name>(key, value):
#     if <condition>:
#         return key, value
#     return _DEFAULT_FALSE

# ### KEY FILTER EXAMPLE ###
# def key_<condition_name>(key, value):
#     if <condition>:
#         return key, value
#     return _DEFAULT_FALSE


# Нам известен формат валидных данных.
# Будем надеяться, что он таким и останется =)
# Для гибкости кончено можно и через *args, **kwargs все писать
def value_only_even(key, value):
    if value % 2 == 0:
        return key, value
    return _DEFAULT_FALSE


def key_only_alpha(key, value):
    if key.isalpha():
        return key.lower(), value  # по мне - фильтр преобразований делать не должен, я бы этот момент обговорил с заказчиком
    return _DEFAULT_FALSE


def value_not_none(key, value):
    if value is not None:
        return key, value
    return _DEFAULT_FALSE


def fail_filter(key, value):
    return key, value / 0


def f1(*args, **kwargs):
    print('f1')


def f2(*args, **kwargs):
    print('f2')
    return True
