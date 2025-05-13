import random


def generate_mac():
    return "fe:54:00:" + ":".join([('0'+hex(random.randint(0, 100))[2:])[-2:].upper() for _ in range(3)])
