import typer
from pathlib import Path
import os
from loguru import logger
import yaml
import hashlib

#app = typer.Typer()


def md5sum(file_name : Path):
    m = hashlib.md5()
    with file_name.open("rb") as fd:
        while True: 
            buf = fd.read( 1024 * 1024 * 128 )
            if buf:
                m.update(buf)
            else:
                return m.hexdigest()


def md5sum_to_path( md5sum : str ):
    return "/".join([md5sum[0:2], md5sum[2:4] , md5sum[4:8] ,md5sum[8:-1]])


class Repo:
    def __init__(self, root_path : Path):
        self.root = root_path

    def _from_path(self, file_name : Path ):
        return Path(md5sum_to_path(md5sum(file_name)))


    def info_path_for(self, file_name : Path ):
        dest_path = self.root/ "info" / self._from_path(file_name)
        dest_path.parent.mkdir(parents=True, exist_ok=True) 
        return dest_path

    def local_path_for(self, file_name : Path ):
        dest_path = self.root / "path" / file_name.absolute().relative_to("/")
        dest_path.parent.mkdir(parents=True, exist_ok=True) 
        return dest_path
        
repo = Repo(Path("~/.local/file_meta").expanduser())

def main( file_name: Path ):
    if not file_name.is_file():
        print(f"{file_name} is not a file, can't handle")
        exit(0)

    info = {
        "stat": file_name.stat(),
        "names" : [ str(file_name.absolute())],
        "md5sum" : md5sum( file_name ),
         "comment": ""
        };

    path_info = {
            "current": md5sum(file_name),
            "trackable": False,
            }
    
    path_of_local = repo.local_path_for(file_name)

    if path_of_local.exists():
        with path_of_local.open("r") as fd:
            old_path_info = yaml.safe_load(fd)

        if old_path_info["current"] != md5sum(file_name):
            print(f"{file_name} is changed, want to track it?")
            exit(0)


    with repo.info_path_for(file_name).open("w") as fd:
        yaml.dump(info, fd)

    with repo.local_path_for(file_name).open("w") as fd:
        yaml.dump(path_info, fd)




def run():
    typer.run(main)
