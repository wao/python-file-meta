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

@pytest.fixture
def tmp_files():
    tmp_path = Path("./tests/fake_datas/case1/tmp_files")
    shutil.rmtree(tmp_path, ignore_errors=True)
    tmp_path.mkdir(0o755)
    return tmp_path

    

def test_same_file(tmp_repo):
    file_name = Path("./tests/fake_datas/case1/files/same_file")
    assert tmp_repo.query(file_name) == QueryResult.NEW
    tmp_repo.file_helper(file_name).create_infos()
    assert tmp_repo.query(file_name) == QueryResult.SAME
    assert file_name.absolute() in tmp_repo.file_helper(file_name).object_info.paths


def test_dirty_file(tmp_files, tmp_repo):
    path = tmp_files / "dirty_file"
    with path.open("w") as fd:
        fd.write("hello1")
    tmp_repo.file_helper(path).create_infos()
    with path.open("w") as fd:
        fd.write("hello2")
    assert tmp_repo.query(path) == QueryResult.DIRTY


def test_new_name_and_added(tmp_files, tmp_repo):
    path = tmp_files / "old_file"
    new_path = tmp_files / "new_file"
    with path.open("w") as fd:
        fd.write("hello1")
    tmp_repo.file_helper(path).create_infos()
    shutil.move(path, new_path)
    assert tmp_repo.query(new_path) == QueryResult.NEW_NAME

    tmp_repo.file_helper(new_path).add_staging_info()
    assert tmp_repo.query(new_path) == QueryResult.SAME
    assert new_path.absolute() in tmp_repo.file_helper(new_path).object_info.paths

def test_meta_vars(tmp_files, tmp_repo):
    path = tmp_files / "dirty_file"
    with path.open("w") as fd:
        fd.write("hello1")
    tmp_repo.file_helper(path).create_infos()
    assert not "url" in tmp_repo.file_helper(path).metas
    
    tmp_repo.file_helper(path).add_meta("url", "www.google.com")

    assert tmp_repo.file_helper(path).metas["url"] == "www.google.com"

def test_tag(tmp_files, tmp_repo):
    path = tmp_files / "dirty_file"
    with path.open("w") as fd:
        fd.write("hello1")
    tmp_repo.file_helper(path).create_infos()

    assert not "url" in tmp_repo.file_helper(path).tags

    tmp_repo.file_helper(path).add_tag("url")

    assert "url" in tmp_repo.file_helper(path).tags

