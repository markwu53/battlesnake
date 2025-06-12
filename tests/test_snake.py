#from battlesnakes.snake import info
#import pytest

def name_coordinate_test_cases(value):
    if isinstance(value, dict):
        return f"({value['x']}, {value['y']})"
    return value


