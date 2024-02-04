from typing import Dict, Callable, Optional, Any, List, Union
from utils import algorithms, algorithms_more_is_better, default_algorithms, AnyAlgorithm
import random
import os
import pandas as pd
from tqdm import tqdm


class Analyzer:
    def __init__(self, used_algorithms: Dict[str, Optional[Dict[str, Any]]] = None, *, show_count: Optional[int] = None) -> None:
        """
        show_count: if None - not show, if < 0 - show all, otherwise - show not more than count
        save_to: if None - save nothing, otherwise - save csv with this name
        """
        if used_algorithms is None:
            used_algorithms = default_algorithms

        self.__show_count = show_count
        self.__alg_funs: Dict[str, Callable[[Any], AnyAlgorithm]] = {}
        self.__algs: Dict[str, AnyAlgorithm] = {}
        self.__used_algorithms = used_algorithms

        for name in used_algorithms:
            alg = algorithms.get(name, None)
            assert alg is not None, f"unknown algorithm: {name}"
            self.__alg_funs[name] = alg

    def __rand_path_from_dir(self, dir: str) -> str:
        return f"{dir}{os.sep}{random.choice(os.listdir(dir))}"
    
    def __prepare(self):
        for name, kw in self.__used_algorithms.items():
            kwargs = kw if kw is not None else {}
            self.__algs[name] = algorithms[name](**kwargs)
    
    def __check(self, *args, **kwargs) -> Dict[str, Dict[str, int]]:
        res = {}
        for name, alg in self.__algs.items():
            res[name] = alg.neighbours(*args, **kwargs)
        return res

    def __show(self, name_to_res: Dict[str, List[Union[str, int]]]):
        if self.__show_count is None:
            return
        if self.__show_count < 0:
            for name, res in name_to_res.items():
                print(f"{name}: {res}")
        else:
            for name, res in name_to_res.items():
                print(f"{name}: {res[:self.__show_count]}")
    
    def __sorted_res(self, name_to_res: Dict[str, Dict[str, int]]) -> Dict[str, List[Union[str, int]]]:
        sorted_res = {}
        for name, res in name_to_res.items():
            sorted_res[name] = sorted(res.items(), key=lambda it: it[1], reverse=algorithms_more_is_better[name])
        return sorted_res
    
    def __analyze(self, name_to_res: Dict[str, Dict[str, int]], sorted_res: Dict[str, List[Union[str, int]]]):
        pass    # TODO

    def __save_csv(self, save_to: Optional[str], name_to_res: Dict[str, Dict[str, int]]):
        if save_to is None:
            return
        data = {}
        for name, res in name_to_res.items():
            for file, count in res.items():
                if file not in data:
                    data[file] = {}
                data[file][name] = count
        keys = []
        records = []
        for key, value in sorted(data.items(), key=lambda it: len(it[1]), reverse=True):
            keys.append(key)
            records.append(value)
        df = pd.DataFrame.from_records(data, columns=keys)
        df.to_csv(save_to)

    def analyze(self, dir: str, path: Optional[str] = None, *, seed: int = 0, save_to: Optional[str] = None):
        random.seed(seed)
        if path is None:
            path = self.__rand_path_from_dir(dir)
        self.__prepare()
        res = self.__check(dir=dir, path=path)
        self.__save_csv(save_to, res)
        sorted_res = self.__sorted_res(res)
        self.__show(sorted_res)
        self.__analyze(res, sorted_res)


algorithms_with_kwargs = {
    "ssdeep": {"threshold": 30},
    "tlsh": {"threshold": 500},
    "mrsh": {"threshold": 30},
    "nilsimsa": {"threshold": 0},
    "simhash": {"threshold": 50},
}

algorithms_with_kwargs_2 = {
    "ssdeep": {"threshold": 80},
    "tlsh": {"threshold": 55},
    "mrsh": {"threshold": 30},
    "nilsimsa": {"threshold": 80},
    "simhash": {"threshold": 10},
}

# if __name__ == "__main__":
#     analyzer = Analyzer(algorithms_with_kwargs, show_count=None)
#     # analyzer.analyze("data_mini", "data_mini/130.html", save_to="res.csv")
#     for i in tqdm(range(100)):
#         analyzer.analyze("data", seed=i, save_to=f"results2/{i}.csv")

algorithms_with_kwargs_3 = {
    "ssdeep": {"threshold": 30},
    "tlsh": {"threshold": 400},
    "mrsh": {"threshold": 30},
}

if __name__ == "__main__":
    prefix = "data"
    analyzer = Analyzer(algorithms_with_kwargs_3, show_count=None)
    for path in tqdm(os.listdir(prefix)):
        path = "641.html"   # remove
        save_to = f"results3/{path[:path.rfind('.')]}.csv"
        if (os.path.exists(save_to)):
            continue
        analyzer.analyze(prefix, f"{prefix}{os.sep}{path}", save_to=save_to)
        break
