from typing import List, Any, Optional, Dict
import os
import subprocess


COMMON_TEMP_DIR = f"{os.path.dirname(os.path.abspath(__file__))}{os.sep}temp"
MRSH_PATH = "./mrsh"    # this path should exist locally for mrshAlg


def _temp_dir(name: str) -> str:
    return f"{COMMON_TEMP_DIR}{os.sep}{name}"

def _temp_file(dir: str) -> str:
    return f"{dir}{os.sep}hash.txt"

def _run_cmd_with_result(cmd: List[str]) -> str:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')

def _run_cmd(cmd: List[str], stdout, stderr=subprocess.DEVNULL) -> None:
    subprocess.run(cmd, stdout=stdout, stderr=stderr)


class AnyAlgorithm:
    def __init__(self) -> None:
        pass
    
    def neighbours(self, dir: str, path: str) -> Any:   # not recursive dir
        assert "\"neighbours\" not implemented"


class ssdeepAlg(AnyAlgorithm):
    __cache = {}

    def __init__(self, threshold: Optional[int] = None, cache_force: bool = False) -> None:
        super().__init__()
        self.__temp_dir = _temp_dir("ssdeep")
        self.__threshold = threshold
        self.__cache_force = cache_force
        os.makedirs(self.__temp_dir, exist_ok=True)
    
    def __hashes(self, dir: str) -> str:
        temp_path = self.__cache.get(dir, None)
        if temp_path is None:
            temp_path = f"{self.__temp_dir}{os.sep}{dir}.txt"
            self.__cache[dir] = temp_path
            if self.__cache_force or not os.path.exists(temp_path):
                _run_cmd(["ssdeep", "-rs", dir], stdout=open(temp_path, 'w'))
        return temp_path
    
    def neighbours(self, dir: str, path: str, threshold: Optional[int] = None) -> Dict[str, int]:
        hashes_path = self.__hashes(dir)
        temp_file = _temp_file(self.__temp_dir)
        _run_cmd(["ssdeep", "-s", path], stdout=open(temp_file, 'w'))
        if threshold is None:
            threshold = self.__threshold
        assert threshold is None or 0 <= threshold < 100, "wrong threshold"
        with_threshold = ["-t", str(threshold)] if threshold is not None else []
        lines = _run_cmd_with_result(["ssdeep", "-k", temp_file, "-rs", *with_threshold, hashes_path])
        path_start = f"{dir}{os.sep}"
        res = {}
        for line in lines.splitlines():
            parts = line.split()
            path_part = path_start + parts[0].split(path_start)[1]
            score_part = int(parts[3][1:-1])
            res[path_part] = score_part
        return res


class tlshAlg(AnyAlgorithm):    # ignore small files
    __cache = {}

    def __init__(self, threshold: Optional[int] = None, cache_force: bool = False) -> None:
        super().__init__()
        self.__temp_dir = _temp_dir("tlsh")
        self.__threshold = threshold
        self.__cache_force = cache_force
        os.makedirs(self.__temp_dir, exist_ok=True)

    def __hashes(self, dir: str) -> str:
        temp_path = self.__cache.get(dir, None)
        if temp_path is None:
            temp_path = f"{self.__temp_dir}{os.sep}{dir}.txt"
            self.__cache[dir] = temp_path
            if self.__cache_force or not os.path.exists(temp_path):
                _run_cmd(["tlsh", "-r", dir], stdout=open(temp_path, 'w'))
        return temp_path

    def neighbours(self, dir: str, path: str, threshold: Optional[int] = None) -> Dict[str, int]:
        hashes_path = self.__hashes(dir)
        if threshold is None:
            threshold = self.__threshold
        assert threshold is None or 0 <= threshold, "wrong threshold"
        with_threshold = ["-T", str(threshold)] if threshold is not None else []
        lines = _run_cmd_with_result(["tlsh", "-c", path, "-l", hashes_path, *with_threshold])
        res = {}
        for line in lines.splitlines():
            parts = line.split()
            path_part = parts[1]
            score_part = int(parts[2])
            res[path_part] = score_part
        return res


class mrshAlg(AnyAlgorithm):
    # __cache = {}
    
    def __init__(self, threshold: Optional[int] = None) -> None:
        super().__init__()
        # self.__temp_dir = _temp_dir("mrsh")
        self.__threshold = threshold
        # os.makedirs(self.__temp_dir, exist_ok=True)
    
    # def __hashes(self, dir: str) -> str:
    #     temp_path = self.__cache.get(dir, None)
    #     if temp_path is None:
    #         temp_path = f"{self.__temp_dir}{os.sep}{dir}.txt"
    #         _run_cmd([MRSH_PATH, "-p", dir], stdout=open(temp_path, 'w'))
    #         self.__cache[dir] = temp_path
    #     return temp_path

    def neighbours(self, dir: str, path: str, threshold: Optional[int] = None) -> Dict[str, int]:
        # hashes_path = self.__hashes(dir)
        if threshold is None:
            threshold = self.__threshold
        assert threshold is None or 0 <= threshold < 100, "wrong threshold"
        with_threshold = ["-t", str(threshold)] if threshold is not None else []
        lines = _run_cmd_with_result([MRSH_PATH, "-c", path, dir, *with_threshold])
        res = {}
        for line in lines.splitlines():
            parts = line.split()
            path_part = f"{dir}{os.sep}{parts[2]}"
            score_part = int(parts[4])
            res[path_part] = score_part
        return res


class nilsimsaAlg(AnyAlgorithm):
    def __init__(self, threshold: Optional[int] = None) -> None:
        super().__init__()
        self.__threshold = threshold
    
    def neighbours(self, dir: str, path: str, threshold: Optional[int] = None) -> Dict[str, int]:
        from nilsimsa import Nilsimsa   # should be installed for nilsimsaAlg
        
        if threshold is None:
            threshold = self.__threshold
        assert threshold is None or -128 <= threshold < 128, "wrong threshold"
        
        with open(path, 'r') as f:
            path_digest = Nilsimsa(f.read()).digest
        
        res = {}
        for compare_path in os.listdir(dir):
            path_part = f"{dir}{os.sep}{compare_path}"
            with open(path_part, 'r') as f:
                score = Nilsimsa(f.read()).compare(path_digest)
            if threshold is None or score > threshold:
                res[path_part] = score
        return res


class simhashAlg(AnyAlgorithm):
    def __init__(self, threshold: Optional[int] = None) -> None:
        super().__init__()
        self.__threshold = threshold
    
    def neighbours(self, dir: str, path: str, threshold: Optional[int] = None) -> Dict[str, int]:
        from simhash import Simhash   # should be installed for simhashAlg
        
        if threshold is None:
            threshold = self.__threshold
        assert threshold is None or 0 <= threshold, "wrong threshold"
        
        with open(path, 'r') as f:
            path_simhash = Simhash(f.read())
        
        res = {}
        for compare_path in os.listdir(dir):
            path_part = f"{dir}{os.sep}{compare_path}"
            with open(path_part, 'r') as f:
                score = Simhash(f.read()).distance(path_simhash)
            if threshold is None or score < threshold:
                res[path_part] = score
        return res


algorithms = {  # nilsimsa & simhash - work slowly(python version is used - but they are simple, if anything can be rewritten)
    "ssdeep": ssdeepAlg,        # % similarity 
    "tlsh": tlshAlg,            # distance
    "mrsh": mrshAlg,            # % similarity
    "nilsimsa": nilsimsaAlg,    # in [-128, 128], -127 - different, 128 - similar
    "simhash": simhashAlg,      # distance
    # "sdhash": None,
    # "spotSigs": None,
    # "pHash": None,
}

algorithms_more_is_better = {
    "ssdeep": True,
    "tlsh": False,
    "mrsh": True,
    "nilsimsa": True,
    "simhash": False,
}

default_algorithms = dict(zip(algorithms.keys(), [None] * len(algorithms)))


if __name__ == "__main__":
    alg = simhashAlg()
    res = alg.neighbours("data", "data/130.html")
    print(res)
