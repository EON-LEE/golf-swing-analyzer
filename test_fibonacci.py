import pytest
from fibonacci import fibonacci

def test_fibonacci_basic():
    assert fibonacci(0) == []
    assert fibonacci(1) == [0]
    assert fibonacci(2) == [0, 1]
    assert fibonacci(5) == [0, 1, 1, 2, 3]

def test_fibonacci_errors():
    with pytest.raises(TypeError):
        fibonacci("5")
    with pytest.raises(ValueError):
        fibonacci(-1)
