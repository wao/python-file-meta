from file_meta.repo import Repo, QueryResult
from pathlib import Path
import pytest
import shutil

@pytest.fixture
def case1_repo():
    repo = Repo(Path("./tests/fake_datas/case1/repo"))
    return repo

def test_new_file(case1_repo):
    assert case1_repo.query(Path("./tests/fake_datas/case1/files/README.rst")) == QueryResult.NEW 

@pytest.fixture
def tmp_repo():
    repo_path = Path("./tests/fake_datas/case1/tmp_repo")
    shutil.rmtree(repo_path, ignore_errors=True)
    repo_path.mkdir(0o755)
    repo = Repo(repo_path)
    return repo

    

def test_same_file(tmp_repo):
    file_name = Path("./tests/fake_datas/case1/files/same_file")
    assert tmp_repo.query(file_name) == QueryResult.NEW
    tmp_repo.file_helper(file_name).create_infos()
    assert tmp_repo.query(file_name) == QueryResult.SAME
