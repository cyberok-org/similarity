from typing import List, Dict, Optional, Any, Callable
from pydantic import BaseModel
import pandas as pd
import os
import numpy as np
from tqdm import tqdm
import json

# set it all

__cur_file_dir = os.path.dirname(os.path.abspath(__file__))

__source_prefix = f"{__cur_file_dir}{os.sep}db{os.sep}import"
__nodes_path = f"{__source_prefix}{os.sep}nodes.csv"
__default_clusters_prefix = f"{__cur_file_dir}{os.sep}rooster{os.sep}clusters"

__edges_suffix = ".csv"
__edges = ["mrsh.csv", "nilsimsa.csv", "simhash.csv", "ssdeep.csv", "tlsh.csv"]


class Node(BaseModel):
    path: str
    ip: str
    domain: Optional[str]
    status_code: int
    server: List[str]
    vendors: List[str]
    cpe: List[str]
    regexes: Optional[str]


class NodePrinter(BaseModel):
    host: str
    ip: str
    port: int
    protocol: str
    base_protocol: str
    title: Optional[str]
    domain: Optional[str]
    server: List[str]
    country: str
    country_name: str
    link: Optional[str]
    jarm: Optional[str]
    icp: Optional[str]
    os: Optional[str]
    product: List[str]
    product_category: List[str]
    cname: Optional[str]


def __find_clusters(df: pd.DataFrame, *, skip_score: Optional[int] = None, skip_score_more: bool = True) -> List[List[int]]:
    cluster_num = 0
    index_to_cluster: Dict[int, int] = {}
    cluster_to_indices: Dict[int, List[int]] = {}
    
    for _, row in df.iterrows():
        if skip_score is not None and ((skip_score_more and skip_score > row["score:int"]) or (not skip_score_more and skip_score < row["score:int"])):
            continue
        cluster_from = index_to_cluster.get(row[":START_ID"], None)
        cluster_to = index_to_cluster.get(row[":END_ID"], None)

        if cluster_from is None:
            if cluster_to is None:
                cluster_to_indices[cluster_num] = [row[":START_ID"], row[":END_ID"]]
                index_to_cluster[row[":START_ID"]] = cluster_num
                index_to_cluster[row[":END_ID"]] = cluster_num
                cluster_num += 1
            else:
                cluster_to_indices[cluster_to].append(row[":START_ID"])
                index_to_cluster[row[":START_ID"]] = cluster_to
        else:
            if cluster_to is None:
                cluster_to_indices[cluster_from].append(row[":END_ID"])
                index_to_cluster[row[":END_ID"]] = cluster_from
            else:
                if cluster_from == cluster_to:
                    continue
                if len(cluster_to_indices[cluster_from]) > len(cluster_to_indices[cluster_to]):
                    cluster_from, cluster_to = cluster_to, cluster_from
                indices = cluster_to_indices.pop(cluster_from)
                cluster_to_indices[cluster_to] += indices
                for index in indices:
                    index_to_cluster[index] = cluster_to
    return cluster_to_indices.values()


def __save_clusters(clusters, prefix: str = __default_clusters_prefix):
    os.makedirs(prefix, exist_ok=True)
    for name, groups in clusters.items():
        with open(f"{prefix}{os.sep}{name}.txt", 'w') as f:
            f.write("\n".join(" ".join(str(index) for index in cluster) for cluster in sorted(list(groups), key=lambda x: len(x), reverse=True)))


def __read_clusters(prefix=__default_clusters_prefix):
    clusters = {}
    for filename in os.listdir(prefix):
        name = filename.replace(".txt", "")
        with open(f"{prefix}{os.sep}{filename}", 'r') as f:
            clusters[name] = [[int(index) for index in line.split()] for line in f.readlines()]
    return clusters


def load_clusters(force: bool = True, prefix: str = __default_clusters_prefix, *, save: bool = True, edges: Optional[List[str]] = None, name_to_cluster_kwargs: Optional[Dict[str, Any]] = None):
    """run for current db edges, fun edges.py once before it"""
    if edges is None:
        edges = __edges
    if name_to_cluster_kwargs is None:
        name_to_cluster_kwargs = {}
    if force or not os.path.exists(prefix):
        clusters = {}
        for edges_filename in edges:
            df = pd.read_csv(f"{__source_prefix}{os.sep}{edges_filename}")
            name = edges_filename.replace(__edges_suffix, "")
            clusters[name] = __find_clusters(df, **(kwargs if (kwargs := name_to_cluster_kwargs.get(name)) is not None else {}))
        if save:
            __save_clusters(clusters)
        return clusters
    else:
        return __read_clusters(prefix)


def load_nodes() -> Dict[int, Node]:
    res = {}
    df = pd.read_csv(__nodes_path, sep=",")
    for _, row in df.iterrows():
        domain = None if pd.isnull(row.domain) else row.domain
        server = row["server:string[]"]
        server = [] if pd.isnull(server) or len(server) == 0 else server.split(";")
        vendors = row["vendors:string[]"]
        vendors = [] if pd.isnull(vendors) or len(vendors) == 0 else vendors.split(";")
        cpe = row["cpe:string[]"]
        cpe = [] if pd.isnull(cpe) or len(cpe) == 0 else cpe.split(";")
        regexes = None if pd.isnull(row.regexes) else row.regexes
        res[row["index:ID"]] = Node(path=row.path, ip=row.ip, domain=domain, status_code=row["status_code:int"], server=server, vendors=vendors, cpe=cpe, regexes=regexes)
    return res


def load_nodes_printer() -> Dict[int, NodePrinter]:  # for printers/routers
    res = {}
    df = pd.read_csv(__nodes_path)
    for _, row in df.iterrows():
        title = None if pd.isnull(row.title) else row.title
        domain = None if pd.isnull(row.domain) else row.domain
        server = [] if pd.isnull(row.server) else row.server.split("; ")
        link = None if pd.isnull(row.link) else row.link
        jarm = None if pd.isnull(row.jarm) else row.jarm
        icp = None if pd.isnull(row.icp) else row.icp
        os = None if pd.isnull(row.os) else row.os
        product = row["product"].split(",")
        product_category = row.product_category.split(",")
        cname = None if pd.isnull(row.cname) else row.cname
        res[row["index:ID"]] = NodePrinter(host=row.host, ip=row.ip, port=row.port, protocol=row.protocol, base_protocol=row.base_protocol,
                                           title=title, domain=domain, server=server, country=row.country, country_name=row.country_name, link=link,
                                           jarm=jarm, icp=icp, os=os, product=product, product_category=product_category, cname=cname)
    return res


#

def diff(clusters: List[List[int]], nodes: Dict[int, Node]) -> Dict[str, int]:
    """counts statistics
    
    Returns:
        Dict[str, int]: average number (in [0, 1]) of identical values across cluster nodes for `status_code`, `server`, `vendors`
    """
    statistic = {"status_code": 0, "server": 0, "vendors": 0}
    for cluster in clusters:
        status_codes = {}
        servers = {}
        vendors = {}
        for node in [nodes[index] for index in cluster]:
            status_codes[node.status_code] = status_codes.get(node.status_code, 0) + 1
            for name in node.server:
                servers[name] = servers.get(name, 0) + 1
            for name in node.vendors:
                vendors[name] = vendors.get(name, 0) + 1
        statistic["status_code"] += status_codes[max(status_codes, key=status_codes.get)] / len(cluster)
        statistic["server"] += 1 if len(servers) == 0 else servers[max(servers, key=servers.get)] / len(cluster)
        statistic["vendors"] += 1 if len(vendors) == 0 else vendors[max(vendors, key=vendors.get)] / len(cluster)
    statistic["status_code"] /= len(clusters)
    statistic["server"] /= len(clusters)
    statistic["vendors"] /= len(clusters)
    return statistic


def diff_printer(clusters: List[List[int]], nodes: Dict[int, Node]) -> Dict[str, int]:
    """counts statistics
    
    Returns:
        Dict[str, int]: average number (in [0, 1]) of identical values across cluster nodes for `product_category`, `server`, `product`
    """
    statistic = {"product_category": 0, "server": 0, "product": 0}
    for cluster in clusters:
        product_category = {}
        server = {}
        product = {}
        for node in [nodes[index] for index in cluster]:
            for name in set(node.product_category):
                product_category[name] = product_category.get(name, 0) + 1
            for name in set(node.server):
                server[name] = server.get(name, 0) + 1
            for name in set(node.product):
                product[name] = product.get(name, 0) + 1
        statistic["product_category"] += product_category[max(product_category, key=product_category.get)] / len(cluster)
        statistic["server"] += 1 if len(server) == 0 else server[max(server, key=server.get)] / len(cluster)
        statistic["product"] += 1 if len(product) == 0 else product[max(product, key=product.get)] / len(cluster)
    statistic["product_category"] /= len(clusters)
    statistic["server"] /= len(clusters)
    statistic["product"] /= len(clusters)
    return statistic


def compute(clusters_dict: Dict[str, List[List[int]]], nodes: Dict[int, Node], f: Callable[[List[int], Dict[int, Node]], Any] = diff) -> Dict[str, Any]:
    res = {}
    for name, clusters in clusters_dict.items():
        res[name] = f(clusters, nodes)
    return res


cluster_score_filter = {
    "mrsh": {"skip_score": 30},
    "nilsimsa": {"skip_score": 115},
    "simhash": {"skip_score": 4, "skip_score_more": False},
    "ssdeep": {"skip_score": 75},
    "tlsh": {"skip_score": 55, "skip_score_more": False},
}


if __name__ == "__main__":
    clusters = load_clusters(force=False, name_to_cluster_kwargs=cluster_score_filter) # force it once after change ANALYZE
    nodes = load_nodes()
    print(compute(clusters, nodes, diff))


# if __name__ == "__main__":
#     nodes = load_nodes_printer()
#     clusters = load_clusters(force=False, name_to_cluster_kwargs=cluster_score_filter, edges=["nilsimsa.csv", "simhash.csv", "ssdeep.csv", "tlsh.csv", "mrsh.csv"]) # force it once after change ANALYZE
#     print(compute(clusters, nodes, diff_printer))
