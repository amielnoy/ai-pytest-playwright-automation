import pytest

def test_force_failure(page):
    page.goto('/')
    assert False, 'forced failure for attachment debug'
