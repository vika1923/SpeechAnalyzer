import os

api_keys = os.getenv("API_KEYS").split()
number_of_keys = len(api_keys)

i = 0


def choosevalidkey():
    global i
    i += 1
    return api_keys[(i - 1)%number_of_keys]

