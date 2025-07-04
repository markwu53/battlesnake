try:
    assert(1+1==3)
except AssertionError:
    print("assert error")
    raise AssertionError
