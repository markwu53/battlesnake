from battlesnakes.snake import info


def test_info() -> None:
    result = info()
    assert result["apiversion"] == "1"
