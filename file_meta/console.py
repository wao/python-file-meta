import typer
from pathlib import Path
import os
from loguru import logger
import yaml
import hashlib

#app = typer.Typer()

class Md5sum:
    def __init__(self, md5sum : str):
        self.md5sum = md5sum

    @staticmethod
    def from_file(file_name : Path):
        m = hashlib.md5()
        with file_name.open("rb") as fd:
            while True: 
                buf = fd.read( 1024 * 1024 * 128 )
                if buf:
                    m.update(buf)
                else:
                    return Md5sum(m.hexdigest())

    def to_path(self):
        return Path("/".join([self.md5sum[0:2], self.md5sum[2:4] , self.md5sum[4:8] ,self.md5sum[8:-1]]))

    def __eq__(self, value)->bool:
        return self.md5sum == value.md5sum

class ObjectInfo:
    def __init__(self, md5sum : Md5sum,   ):
        self.md5sum = md5sum
        self.paths = []
        self.comment = "" 
        self.parent = None


class StagingInfo:
    def __init__(self, path : Path):
        self.path = path
        self.md5sum = Md5sum.from_file(path)
        self.track = False

class RepoFileHelper:
    def __init__(self, file_path : Path, root_path : Path ):
        self.md5sum = Md5sum.from_file(file_path)
        self._src_file_path = file_path
        self.root = root_path
        self._file_path = None
        self._object_path = None

    @staticmethod
    def from_file( file_path, root_path ):
        return RepoFileHelper(file_path, root_path)

    @property
    def object_path(self):
        if not self._object_path:
            self._object_path = self.root/ "objects" / self.md5sum.to_path() 
            self._object_path.parent.mkdir(parents=True, exist_ok=True) 

        return self._object_path

    @property
    def staging_path(self):
        if not self._file_path:
            self._file_path = self.root / "files" / self._src_file_path.absolute().relative_to("/")
            self._file_path.parent.mkdir(parents=True, exist_ok=True) 

        return self._file_path

    def has_staging_info(self):
        return self.staging_path.exists()

    def has_object_info(self):
        return self.object_path.exists()

    def staging_info(self) -> StagingInfo:
        assert self.has_staging_info()

        if not self._staging_info:
            with self.staging_path.open("r") as fd:
                self._staging_info = yaml.safe_load(fd) 

        return self._staging_info

    def object_info(self):
        assert self.has_object_info()

        if not self._object_info:
            with self.object_path.open("r") as fd:
                self._object_info = yaml.safe_load(fd) 

        return self._object_info


class RepoProcessCallback:
    def on_same_file(self, fh : RepoFileHelper):
        assert False

    def on_dirty_file(self, fh : RepoFileHelper):
        assert False

    def on_new_name_for_existing_file(self, fh : RepoFileHelper):
        assert False

    def on_save_new_file(self, fh : RepoFileHelper):
        assert False

class Repo:
    def __init__(self, root_path : Path):
        self.root = root_path

    def process(self, file_name : Path, clt : RepoProcessCallback):
        #caculate md5sum of file_name
        filehelper = RepoFileHelper.from_file(file_name, self.root)

        #if find same file_name in repo
        if filehelper.has_staging_info():
            #if same md5sum
            if filehelper.staging_info.md5sum == filehelper.md5sum:
                clt.on_same_file(filehelper)
            else:
                clt.on_dirty_file(filehelper)
        else:
            #find same md5sum in repo
            if filehelper.has_object_info():
                clt.on_new_name_for_existing_file(filehelper)
            else:
                #create a new entry and save all items
                clt.on_save_new_file(filehelper)
            
        
repo = Repo(Path("~/.local/file_meta").expanduser())

def old_main( file_name: Path ):
    if not file_name.is_file():
        print(f"{file_name} is not a file, can't handle")
        exit(0)

def main( file_name: Path ):
    class StatusCmdCb(RepoProcessCallback):
        def on_same_file(self, fh : RepoFileHelper):
            print("Already saved in repo")

        def on_dirty_file(self, fh : RepoFileHelper):
            print("Dirty file")

        def on_new_name_for_existing_file(self, fh : RepoFileHelper):
            print("Found duplicate")

        def on_save_new_file(self, fh : RepoFileHelper):
            print("New file, save to repo")

    repo.process(file_name, StatusCmdCb())

def run():
    typer.run(main)
