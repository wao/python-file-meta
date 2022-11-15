from file_meta.repo import Repo, QueryResult
from pathlib import Path
import pytest

@pytest.fixture
def case1_repo():
    repo = Repo(Path("./tests/fake_datas/case1/repo"))
    return repo

def test_new_file(case1_repo):
    assert case1_repo.query(Path("./tests/fake_datas/case1/files/README.rst")) == QueryResult.NEW 

def test_same_file(case1_repo):
    assert case1_repo.query(Path("./tests/fake_datas/case1/files/same_file")) == QueryResult.SAME
