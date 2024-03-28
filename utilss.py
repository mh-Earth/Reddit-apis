import string
import random


def gen_password(lenght:int):
    char_lists = []
    char_lists.extend(string.ascii_letters + string.digits)
    random.shuffle(char_lists)
    password = ''.join(char_lists[0:lenght])
    return password


if __name__ == "__main__":
    print(gen_password(16))


