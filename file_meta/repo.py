from pathlib import Path
import os
from loguru import logger
import yaml
import hashlib
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime
import time
import random

class Md5sum:
    def __init__(self, md5sum : str):
        self.md5sum = md5sum

    @staticmethod
    def from_file(file_name : Path):
        m = hashlib.sha256()
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

@dataclass
class Comment:
    uid : str
    mtime : datetime
    content : str

@dataclass
class ObjectInfo:
    md5sum : Md5sum
    st_size : int
    paths : dict[Path,datetime]
    comments : dict[str,Comment]
    metas : dict[str,str]

@dataclass
class StagingInfo:
    md5sum : Md5sum
    st_dev : int
    st_size : int
    st_mtime : float
    st_ctime : float

symbols = "0123456789abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789"

def int2sym(value,mod):
    while value >= mod:
        value, remind = divmod(value, mod)
        yield symbols[remind]

def uniqid2():
    value = int(time.time())
    mod = len(symbols)
    return "".join(list(int2sym(value,mod)))

def uniqid():
    return "".join(random.choices(symbols, k=12))

class RepoFileHelper:
    def __init__(self, file_path : Path, root_path : Path ):
        self.md5sum = Md5sum.from_file(file_path)
        self._src_file_path = file_path
        self.root = root_path
        self._file_path = None
        self._object_path = None
        self._staging_info = None
        self._object_info = None

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

    @property
    def staging_info(self) -> StagingInfo:
        assert self.has_staging_info()

        if not self._staging_info:
            with self.staging_path.open("r") as fd:
                self._staging_info = StagingInfo(**yaml.unsafe_load(fd)) 

        return self._staging_info

    @property
    def object_info(self):
        assert self.has_object_info()

        if not self._object_info:
            with self.object_path.open("r") as fd:
                self._object_info = ObjectInfo(**yaml.unsafe_load(fd)) 

        return self._object_info

    def create_infos(self):
        assert not self.has_object_info()
        assert not self.has_staging_info()

        self._create_object_info()
        self._create_staging_info()

    def add_comment(self, comment:str):
        c = Comment(uniqid(), datetime.now(), comment)
        self.object_info.comments[c.uid] = c
        self._save_object_info()

    def add_meta(self, meta_name:str, meta_value:str):
        self.object_info.metas[meta_name] = meta_value
        self._save_object_info()

    @property
    def metas(self):
        return self.object_info.metas

    def _create_object_info(self):
        assert not self.has_object_info()

        current_stat = self._src_file_path.stat()

        self._object_info = ObjectInfo(self.md5sum, current_stat.st_size,
                dict({self._src_file_path.absolute(): datetime.now()}), 
            dict(), dict())


        self._save_object_info()

    def _save_object_info(self):
        with self.object_path.open("w") as fd:
            yaml.dump( asdict(self._object_info), fd)

    def _create_staging_info(self):
        assert not self.has_staging_info()
        self._replace_staging_info()
        
    def _replace_staging_info(self):
        current_stat = self._src_file_path.stat()

        self._staging_info = StagingInfo( self.md5sum, 
                    current_stat.st_dev, current_stat.st_size, current_stat.st_mtime, current_stat.st_ctime) 
        self._save_staging_info()


    def _save_staging_info(self):
        with self.staging_path.open("w") as fd:
            yaml.dump( asdict(self._staging_info), fd)

    def add_staging_info(self):
        self._create_staging_info()
        self._add_path_to_object_info()


    def _add_path_to_object_info(self):
        self.object_info.paths[self._src_file_path.absolute()]=datetime.now()
        self._save_object_info()

    def replace_infos(self):
        assert self.md5sum != self.staging_info.md5sum
        self._replace_staging_info()
        if self.has_object_info():
            self._add_path_to_object_info()
        else:
            self._create_object_info()

    def query(self):
        #if find same file_name in repo
        if self.has_staging_info():
            #if same md5sum
            if self.staging_info.md5sum == self.md5sum:
                return QueryResult.SAME
            else:
                return QueryResult.DIRTY
        else:
            #find same md5sum in repo
            if self.has_object_info():
                return QueryResult.NEW_NAME
            else:
                #create a new entry and save all items
                return QueryResult.NEW


class QueryResult(Enum):
    SAME = 1
    DIRTY = 2
    NEW_NAME = 3
    NEW = 4

class Repo:
    def __init__(self, root_path : Path):
        self.root = root_path

    def query(self, file_name : Path ):
        return self.file_helper(file_name).query()

            
    def file_helper(self, file_name : Path) :
        return RepoFileHelper.from_file(file_name, self.root)
        
