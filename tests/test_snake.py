from battlesnakes.snake import info, get_up_coord, get_direction_coord


def test_info() -> None:
    result = info()
    assert result["apiversion"] == "1"

def test_get_up_coord():  # The function name starts with "test_"
    # Given: The initial conditions
    head_coord = {"x": 1, "y": 1}

    # When: The action being tested. In this case, executing a function
    up_coord = get_up_coord(head_coord=head_coord)

    # Then: The expected outcome. In this case, we expect the return value of that function to be an explicit value.
    assert up_coord == {"x": 1, "y": 2}

def test_get_up_coord_2():  # The function name starts with "test_"
    # Given: The initial conditions
    head_coord = {"x": 9, "y": 9}

    # When: The action being tested. In this case, executing a function
    up_coord = get_up_coord(head_coord=head_coord)

    # Then: The expected outcome. In this case, we expect the return value of that function to be an explicit value.
    assert up_coord == {"x": 9, "y": 10}

import pytest

def name_coordinate_test_cases(value):
    if isinstance(value, dict):
        return f"({value['x']}, {value['y']})"
    return value

@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"x": 1, "y": 1}, {"x": 1, "y": 2}),
        ({"x": 9, "y": 9}, {"x": 9, "y": 10}),
    ],
    #ids = name_coordinate_test_cases,
)
def test_get_up_coord_parameterized(test_input, expected):
    up_coord = get_up_coord(head_coord=test_input)
    assert up_coord == expected

def test_get_up_coord_not_a_valid_coordinate():
    head_coord = {"y": 9}

    with pytest.raises(
            ValueError, match="head_coord must have both 'x' and 'y' keys: .*"
    ):
        get_up_coord(head_coord=head_coord)

@pytest.mark.parametrize(
    "test_input, direction, expected",
    [
        ({"x": 1, "y": 1}, "up", {"x": 1, "y": 2}),
        ({"x": 9, "y": 9}, "up", {"x": 9, "y": 10}),
    ],
    ids = name_coordinate_test_cases,
)
def test_get_direction_coord(test_input, direction, expected):
    coord = get_direction_coord(direction=direction, head_coord=test_input)
    assert coord == expected

@pytest.mark.parametrize(
    "direction, head_coord,expected",
    [
        ("up", {"x": 1, "y": 1}, {"x": 1, "y": 2}),
        ("down", {"x": 1, "y": 1}, {"x": 1, "y": 0}),
        ("left", {"x": 1, "y": 1}, {"x": 0, "y": 1}),
        ("right", {"x": 1, "y": 1}, {"x": 2, "y": 1}),
        ("up", {"x": 9, "y": 9}, {"x": 9, "y": 10}),
        ("down", {"x": 9, "y": 9}, {"x": 9, "y": 8}),
        ("left", {"x": 9, "y": 9}, {"x": 8, "y": 9}),
        ("right", {"x": 9, "y": 9}, {"x": 10, "y": 9}),
    ],
    ids=name_coordinate_test_cases,
)
def test_get_direction_coord_parameterized(direction, head_coord, expected):
    up_coord = get_direction_coord(direction=direction, head_coord=head_coord)
    assert up_coord == expected

def test_get_direction_coord_not_a_valid_coordinate():
    with pytest.raises(
            ValueError, match="head_coord must have both 'x' and 'y' keys: .*"
    ):
        get_direction_coord(direction="up", head_coord={"y": 9})


def test_get_direction_coord_not_a_valid_direction():
    with pytest.raises(
            ValueError, match="invalid direction:.*"
    ):
        get_direction_coord(direction="not a direction", head_coord={"x": 9, "y": 9})


