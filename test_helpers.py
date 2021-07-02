import pytest

from helpers import fix_apostroph, complex_name

def test_fix_apostroph():
    expected = "П'ятницька Г Т "
    result = fix_apostroph("П’ятницька Г Т ")
    assert expected == result

def test_complex_name():
    expected = "Сідорчук-Сідорова"
    result = complex_name("Сідорчук-сідорова")
    assert expected == result
    expected = "Иванов"
    result = complex_name("Иванов")
    assert expected == result
    expected = None
    result = complex_name(None)
    assert expected == result