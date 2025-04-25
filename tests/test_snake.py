from battlesnakes.snake import info, get_up_coord


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ({"x": 1, "y": 1}, {"x": 1, "y": 2}),
        ({"x": 9, "y": 9}, {"x": 9, "y": 10}),
    ],
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
