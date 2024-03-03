import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Dict
from ..local.metrics import Node, load_nodes
from cdifflib import CSequenceMatcher

__cur_file_dir = os.path.dirname(os.path.abspath(__file__))
__common_prefix = f"{__cur_file_dir}{os.sep}res{os.sep}2"

__clusters_prefix = f"{__common_prefix}{os.sep}clusters"
__clusters_prefix_to = f"{__common_prefix}{os.sep}cokhostdomains"
__pictures_prefix_to = f"{__common_prefix}{os.sep}pict"
__names = ["mrsh.txt", "nilsimsa.txt", "simhash.txt", "ssdeep.txt", "tlsh.txt"]


def domains(nodes: Dict[int, Node], filename: str, filename_prefix_from: Optional[str] = None, filename_prefix_to: Optional[str] = None):
    if filename_prefix_from is None:
        filename_prefix_from = __clusters_prefix
    if filename_prefix_to is None:
        filename_prefix_to = __clusters_prefix_to

    with open(f"{filename_prefix_from}{os.sep}{filename}", 'r') as fr, open(f"{filename_prefix_to}{os.sep}{filename}", 'w') as fw:
        while True:
            line = fr.readline()
            if not line:
                break
            cluster = list(map(lambda x: int(x), line.split()))
            domains = [nodes[ind].domain for ind in cluster]
            fw.write(" ".join(domains) + "\n")


def __diagram(length_to_count: Dict[int, int], filename: str, filename_prefix: str):
    max_length = max(length_to_count.keys()) + 1
    length = np.arange(max_length)
    counts = [0] * max_length
    for k, v in length_to_count.items():
        counts[k] = v

    fig, ax = plt.subplots()

    ax.barh(length, counts, align='center')
    ax.invert_yaxis()
    ax.set_xlabel('count')
    ax.set_title('Common substring length')

    plt.savefig(f"{filename_prefix}{os.sep}{filename}")


def check_domains(filename: str, filename_prefix: Optional[str] = None, pictures_prefix: Optional[str] = None):
    if pictures_prefix is None:
        pictures_prefix = __pictures_prefix_to
    if not os.path.exists(pictures_prefix):
        os.makedirs(pictures_prefix)
    if filename_prefix is None:
        filename_prefix = __clusters_prefix_to
    sizes = {}
    sizes_sum = 0
    count = 0
    with open(f"{filename_prefix}{os.sep}{filename}", 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            count += 1
            domains = line.split()

            max_size = 0
            temp = domains[0]
            for domain in domains[1:]:
                match = CSequenceMatcher(None, domain, temp).find_longest_match(0, len(domain), 0, len(temp))
                # print(domain, temp, domain[match.a: match.a + match.size])
                max_size = max(max_size, match.size)
                temp = domain
            sizes_sum += max_size
            sizes[max_size] = sizes.get(max_size, 0) + 1
    # mean_size = sizes_sum / count
    __diagram(sizes, filename.replace('.txt', '.png') , pictures_prefix)
    # print(f"mean common size ({filename.replace('.txt', '')}) = {mean_size}")


if __name__ == "__main__2":
    nodes = load_nodes()
    filename_prefix_to = __clusters_prefix_to
    if os.path.exists(filename_prefix_to):
        shutil.rmtree(filename_prefix_to)
    os.makedirs(filename_prefix_to)
    for name in __names:
        domains(nodes, name, filename_prefix_to=filename_prefix_to)


if __name__ == "__main__":
    for name in __names:
        check_domains(name)
