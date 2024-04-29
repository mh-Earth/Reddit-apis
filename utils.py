import string
import random
import time

def gen_random_string(lenght:int):
    char_lists = []
    char_lists.extend(string.ascii_letters + string.digits)
    random.shuffle(char_lists)
    password = ''.join(char_lists[0:lenght])
    return password

def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        # print(f"Execution time of {func.__name__}: {execution_time} seconds")
        return result
    return wrapper



# if __name__ == "__main__":
#     print(gen_password(16))


