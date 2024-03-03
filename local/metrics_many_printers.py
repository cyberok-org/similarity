import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from tqdm import tqdm
import matplotlib.pyplot as plt
from metrics import load_clusters, load_nodes_printer, compute, diff_printer


__cur_file_dir = os.path.dirname(os.path.abspath(__file__))
__show_dir = f"{__cur_file_dir}{os.sep}rooster{os.sep}pict"
__stat_names = ["product_category", "server", "product"]


class TestItem(BaseModel):
    name: str
    edges_filename: str
    scores: List[int]
    skip_score_more: bool = True


def __show(data: Dict[str, Dict[str, Any]], stat_names: Optional[List[str]] = None):
    os.makedirs(__show_dir, exist_ok=True)
    if stat_names is None:
        stat_names = __stat_names
    for alg, statistics in data.items():
        scores = [stat["score"] for stat in statistics]
        stat = {}
        for name in stat_names:
            stat[name] = [stat[name] for stat in statistics]

        figure, axis = plt.subplots(len(stat_names), 1)
        for i, name in enumerate(stat_names):
            axis[i].plot(scores, stat[name]) 
            axis[i].set_xlabel("scores")
            axis[i].set_ylabel(name)
            axis[i].set_xticks(scores)
        figure.suptitle(alg)
        plt.savefig(f"{__show_dir}{os.sep}{alg}.png")


def main():
    items = [
        TestItem(name="mrsh", edges_filename="mrsh.csv", scores=list(range(20, 101, 5))),
        TestItem(name="ssdeep", edges_filename="ssdeep.csv", scores=list(range(20, 101, 5))),
        TestItem(name="tlsh", edges_filename="tlsh.csv", scores=list(range(0, 150, 5)) + list(range(150, 301, 15)), skip_score_more=False),
        TestItem(name="simhash", edges_filename="simhash.csv", scores=list(range(0, 21, 1)), skip_score_more=False),
        TestItem(name="nilsimsa", edges_filename="nilsimsa.csv", scores=list(range(0, 64, 8)) + list(range(64, 129, 4))),
    ]

    nodes = load_nodes_printer()
    for item in items:
        res = {}
        item_res = []
        for score in tqdm(item.scores):
            clusters = load_clusters(force=True, save=False, edges=[item.edges_filename], name_to_cluster_kwargs={item.name: {"skip_score": score, "skip_score_more": item.skip_score_more}})
            statistic = compute(clusters, nodes, diff_printer)[item.name]
            statistic["score"] = score
            item_res.append(statistic)
        res[item.name] = item_res
        __show(res)


if __name__ == "__main__":
    main()
