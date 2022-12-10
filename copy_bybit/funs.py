from re import search


def pcheck(password):
    res = [search(r"[a-z]", password), search(r"[A-Z]", password), search(r"[0-9]", password), len(password)]
    if all(res):
        return True
    return ("Пароль слабый. " +
            "Нет строчных букв. " * (res[0] is None) +
            "Нет заглавных букв. " * (res[1] is None) +
            "Нет цифр. " * (res[2] is None)
            + "Пароль меньши 8 символов. " * (res[3] < 8))
