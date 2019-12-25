import random

P_SPLIT = 1 / 2
P_INSERT_PLAIN = 1 / 5
P_INSERT_JUMP = 1 / 8
LABEL_TEMPLATE = f"_L{random.randint(2**16 - 1, 2**32 - 1):X}_{{:X}}"


def insert_plain():
    return ["\tnop" for _ in range(random.randint(1, 2))]


def insert_jump():
    return [f"\t.byte 0x{random.randint(0, 255):X}" for _ in range(random.randint(1, 2))]


def should_process(function):
    return function.find("std") == -1  # skip standard library functions
