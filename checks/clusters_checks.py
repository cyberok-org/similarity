import os
import shutil
from metrics import Node, load_nodes
from tqdm import tqdm
import json
from typing import Dict, List, Any, Optional, Callable

__clusters_dir = "clusters"     # set it
__nodes_path = "nodes.csv"      # set it

__interesting_vendors = {'Apache httpd', 'Apache Tomcat', 'Microsoft IIS httpd', 'nginx', 'OpenBSD httpd', 'Tornado httpd', 'Werkzeug httpd', 'Node.js Express framework', 'OpenResty web app server', 'BaseHTTPServer', 'Boa HTTPd', 'CherryPy httpd', 'Cloudflare http proxy', 'Cloudflare nginx', 'Gunicorn', 'lighttpd', 'LiteSpeed httpd', 'mini_httpd', 'Mojolicious httpd', 'Mongrel httpd', 'Monkey httpd', 'Squid http proxy', 'Tengine httpd', 'Thin httpd', 'thttpd', 'tinyproxy', 'TwistedWeb httpd', 'uc-httpd', 'WebLogic server', 'WEBrick http', 'Zope httpd', '<empty>'}
__algorithm_to_sorted_thresholds = {
    "ssdeep": [70, 80, 90, 95],
    "mrsh": [30, 50, 70, 90],
    "nilsimsa": [100, 110, 120, 125],
    "simhash": [4, 3, 2, 1],
    "tlsh": [55, 30, 15, 5],
}
__clusters_batches = [[f"{algorithm}_{threshold}.txt" for threshold in thresholds] for algorithm, thresholds in __algorithm_to_sorted_thresholds.items()]
__regexes_split_by = "###"


def __vendors(nodes: Dict[int, Node], cluster: List[int]) -> Dict[str, int]:
    vendors = {}
    for node_index in cluster:
        node = nodes[node_index]
        if len(node.vendors) == 0:
            vendors["<empty>"] = vendors.get("<empty>", 0) + 1
        else:
            for name in set(node.vendors):
                vendors[name] = vendors.get(name, 0) + 1
    return vendors


def __servers(nodes: Dict[int, Node], cluster: List[int]) -> Dict[str, int]:
    servers = {}
    for node_index in cluster:
        node = nodes[node_index]
        if len(node.server) == 0:
            servers["<empty>"] = servers.get("<empty>", 0) + 1
        else:
            for name in set(node.server):
                servers[name] = servers.get(name, 0) + 1
    return servers


def __regexes(nodes: Dict[int, Node], cluster: List[int]) -> Dict[str, int]:
    regexes = {}
    for node_index in cluster:
        node = nodes[node_index]
        if node.regexes is None:
            regexes["<empty>"] = regexes.get("<empty>", 0) + 1
        else:
            for name in node.regexes.split(__regexes_split_by):
                regexes[name] = regexes.get(name, 0) + 1
    return regexes


def metric(nodes: Dict[int, Node], filename: str, *, save_prefix: str = "res/5", k_less=1):
    """k - metric score, if k < k_less - save"""
    vendors_dir = f"{save_prefix}{os.sep}vendors"
    servers_dir = f"{save_prefix}{os.sep}servers"
    regexes_dir = f"{save_prefix}{os.sep}regexes"
    
    algorithm = filename[filename.rfind(os.sep)+1:filename.rfind(".")]
    os.makedirs(f"{vendors_dir}{os.sep}{algorithm}")
    os.makedirs(f"{servers_dir}{os.sep}{algorithm}")
    os.makedirs(f"{regexes_dir}{os.sep}{algorithm}")

    with open(filename, 'r') as fr:
        i = -1
        while True:
            line = fr.readline()
            if not line:
                break
            i += 1
            cluster = list(map(lambda x: int(x), line.split()))

            servers = __servers(nodes, cluster)
            max_value_servers = servers[max(servers, key=servers.get)]
            k = max_value_servers / len(cluster)
            if k < k_less:
                res = {
                    "k": k,
                    "max": max_value_servers,
                    "count": len(cluster),
                    "data": servers,
                    "cluster": cluster,
                }
                json.dump(res, open(f"{servers_dir}{os.sep}{algorithm}{os.sep}{i}.json", 'w'))

            vendors = __vendors(nodes, cluster)
            max_value_vendors = vendors[max(vendors, key=vendors.get)]
            k = max_value_vendors / len(cluster)
            if k < k_less:
                res = {
                    "k": k,
                    "max": max_value_vendors,
                    "count": len(cluster),
                    "data": vendors,
                    "cluster": cluster,
                }
                json.dump(res, open(f"{vendors_dir}{os.sep}{algorithm}{os.sep}{i}.json", 'w'))

            regexes = __regexes(nodes, cluster)
            max_value_regexes = regexes[max(regexes, key=regexes.get)]
            k = max_value_regexes / len(cluster)
            if k < k_less:
                res = {
                    "k": k,
                    "max": max_value_regexes,
                    "count": len(cluster),
                    "data": regexes,
                    "cluster": cluster,
                }
                json.dump(res, open(f"{regexes_dir}{os.sep}{algorithm}{os.sep}{i}.json", 'w'))



def by_products(nodes: Dict[int, Node], filename: str, *, save_prefix: str = "res/1"):
    algorithm = filename[filename.rfind(os.sep)+1:filename.rfind(".")]
    os.makedirs(f"{save_prefix}{os.sep}{algorithm}")

    with open(filename, 'r') as fr:
        i = -1
        while True:
            line = fr.readline()
            if not line:
                break
            i += 1
            cluster = list(map(lambda x: int(x), line.split()))

            vendors = __vendors(nodes, cluster)
            most_popular_vendor = max(vendors, key=vendors.get)
            if most_popular_vendor in __interesting_vendors:
                res = {
                    "len": len(cluster),
                    "most_popular_vendor": most_popular_vendor,
                    "data": vendors,
                    "cluster": cluster,
                }
                json.dump(res, open(f"{save_prefix}{os.sep}{algorithm}{os.sep}{i}.json", 'w'))


def create_cluster_structure(nodes: Dict[int, Node], filenames: List[str], algorithm: str, *, save_prefix: str = "res/3"):
    """filenames - sorted by score"""
    res: List[List[List[Dict[str, Any]]]] = []    # cluster number (min threshold) -> level (= filename index) -> cluster subgroup -> structure
    os.makedirs(f"{save_prefix}{os.sep}{algorithm}")
    cluster_by_index: Dict[int, int] = {}   # node index -> cluster number
    with open(filenames[0], 'r') as fr:
        cluster_num = -1
        while True:
            line = fr.readline()
            if not line:
                break
            cluster_num += 1
            cluster = list(map(lambda x: int(x), line.split()))
            for index in cluster:
                cluster_by_index[index] = cluster_num

            vendors = __vendors(nodes, cluster)
            most_popular_vendor = max(vendors, key=vendors.get)
            regexes = __regexes(nodes, cluster)
            most_popular_regex = max(regexes, key=regexes.get)

            cluster_struct = [[] for _ in filenames]
            cluster_struct[0].append({
                "index": cluster_num,
                "cluster": cluster,
                "vendor": most_popular_vendor,
                "regex": most_popular_regex,
            })
            res.append(cluster_struct)

    previous_cluster_by_index = cluster_by_index
    for i, filename in enumerate(filenames[1:]):
        new_cluster_by_index = {}
        filename_index = i + 1
        with open(filename, 'r') as fr:
            cluster_num = -1
            while True:
                line = fr.readline()
                if not line:
                    break
                cluster_num += 1
                cluster = list(map(lambda x: int(x), line.split()))
                for index in cluster:
                    new_cluster_by_index[index] = cluster_num
                    
                any_index_from_cluster = cluster[0]     # necessarily lies in the desired subcluster, it does not matter what index
                main_cluster_num = cluster_by_index[any_index_from_cluster]
                previous_cluster_index = previous_cluster_by_index[any_index_from_cluster]  # index cluster at a higher level
                
                vendors = __vendors(nodes, cluster)
                most_popular_vendor = max(vendors, key=vendors.get)
                regexes = __regexes(nodes, cluster)
                most_popular_regex = max(regexes, key=regexes.get)
                
                res[main_cluster_num][filename_index].append({
                    "index": cluster_num,
                    "index_from": previous_cluster_index,
                    "vendor": most_popular_vendor,
                    "regex": most_popular_regex,
                    "cluster": cluster,
                })
        previous_cluster_by_index = new_cluster_by_index

    for i, cluster_struct in enumerate(res):
        json.dump(cluster_struct, open(f"{save_prefix}{os.sep}{algorithm}{os.sep}{i}.json", 'w'))

# interesting defs


def interesting_cluster_check_simple(structs: List[Dict[str, Any]]) -> Optional[List[str]]:
    """one struct keys - index, index_from, vendor, regex, cluster; return interesting indices (subset of struct.index by structs) or None"""
    if len(structs) == 1:
        return None
    return [struct["index"] for struct in structs]


def interesting_cluster_check_big_only(structs: List[Dict[str, Any]], minimal_cluster_size: int = 10) -> Optional[List[str]]:
    """one struct keys - index, index_from, vendor, regex, cluster; return interesting indices (subset of struct.index by structs) or None"""
    indices = []
    for struct in structs:
        if len(struct["cluster"]) >= minimal_cluster_size:
            indices.append(struct["index"])
    
    if len(indices) > 1:
        return indices
    return None


def interesting_cluster_check_different_vendors(structs: List[Dict[str, Any]]) -> Optional[List[str]]:
    """one struct keys - index, index_from, vendor, regex, cluster; return interesting indices (subset of struct.index by structs) or None"""
    vendors = set()
    for struct in structs:
        vendors.add(struct["vendor"])

    if len(vendors) > 1:
        return [struct["index"] for struct in structs]
    return None


def interesting_cluster_check_different_vendors2(structs: List[Dict[str, Any]], interesting_vendors: Optional[List[str]] = None) -> Optional[List[str]]:
    """one struct keys - index, index_from, vendor, regex, cluster; return interesting indices (subset of struct.index by structs) or None"""
    if interesting_vendors is None:
        interesting_vendors = __interesting_vendors

    vendors = set()
    for struct in structs:
        vendors.add(struct["vendor"])

    if len(list(filter(lambda x: x in interesting_vendors, vendors))) > 1:
        return [struct["index"] for struct in structs]
    return None


def interesting_cluster_check_different_regexes(structs: List[Dict[str, Any]]) -> Optional[List[str]]:
    """one struct keys - index, index_from, vendor, regex, cluster; return interesting indices (subset of struct.index by structs) or None"""
    regexes = set()
    for struct in structs:
        # if len(struct["cluster"]) < 10:
        #     continue
        regexes.add(struct["regex"])

    if len(regexes) > 1:
        return [struct["index"] for struct in structs]
    return None

#


def interesting_cluster_decompositions(data_dir: str, save_filename: str, interesting_f: Optional[Callable]=None):
    if interesting_f is None:
        interesting_f = interesting_cluster_check_simple
    algorithm = data_dir[data_dir.rfind(os.sep)+1:]
    with open(save_filename, 'w') as fw:
        for name in tqdm(os.listdir(data_dir)):
            cluster_structure: List[List[Dict[str, Any]]] = json.load(open(f"{data_dir}{os.sep}{name}", 'r'))

            for previous_cluster_level, subclusters in enumerate(cluster_structure[1:]):
                previous_cluster_threshold = __algorithm_to_sorted_thresholds[algorithm][previous_cluster_level]
                current_cluster_threshold = __algorithm_to_sorted_thresholds[algorithm][previous_cluster_level + 1]

                index_from_to_structs = {}
                for struct in subclusters:
                    index_from = struct["index_from"]

                    if index_from not in index_from_to_structs:
                        index_from_to_structs[index_from] = []
                    index_from_to_structs[index_from].append(struct)

                for index_from, structs in index_from_to_structs.items():
                    indices = interesting_f(structs)
                    if indices is None:
                        continue

                    label_from = f"{algorithm}_{previous_cluster_threshold}_{index_from}"
                    labels_to = [f"{algorithm}_{current_cluster_threshold}_{index}" for index in indices]
                    fw.write(f'{label_from}: {" ".join(labels_to)}\n')


if __name__ == "__main__":
    nodes = load_nodes(__nodes_path)

    save_prefix = "res/1"
    if os.path.exists(save_prefix):
        shutil.rmtree(save_prefix)
    for name in tqdm(os.listdir(__clusters_dir)):
        by_products(nodes, f"{__clusters_dir}{os.sep}{name}", save_prefix=save_prefix)

    save_prefix = "res/5"
    if os.path.exists(save_prefix):
        shutil.rmtree(save_prefix)
    for name in tqdm(os.listdir(__clusters_dir)):
        metric(nodes, f"{__clusters_dir}{os.sep}{name}", save_prefix=save_prefix)

    save_prefix = "res/3"
    if os.path.exists(save_prefix):
        shutil.rmtree(save_prefix)
    for names in __clusters_batches:
        algorithm = names[0][:names[0].find('_')]
        create_cluster_structure(nodes, [f"{__clusters_dir}{os.sep}{name}" for name in names], algorithm=algorithm, save_prefix=save_prefix)


if __name__ == "__main__2":
    data_prefix = "res/3"
    save_prefix = f"{data_prefix}/interesting"
    if os.path.exists(save_prefix):
        shutil.rmtree(save_prefix)
    os.makedirs(save_prefix)

    # interesting_fun = interesting_cluster_check_simple
    # interesting_fun = interesting_cluster_check_big_only
    interesting_fun = interesting_cluster_check_different_vendors
    # interesting_vendors = {'Microsoft IIS httpd', 'OpenBSD httpd', 'Tornado httpd', 'Werkzeug httpd', 'Node.js Express framework', 'OpenResty web app server', 'BaseHTTPServer', 'Boa HTTPd', 'CherryPy httpd', 'Cloudflare http proxy', 'Cloudflare nginx', 'Gunicorn', 'lighttpd', 'LiteSpeed httpd', 'mini_httpd', 'Mojolicious httpd', 'Mongrel httpd', 'Monkey httpd', 'Squid http proxy', 'Tengine httpd', 'Thin httpd', 'thttpd', 'tinyproxy', 'TwistedWeb httpd', 'uc-httpd', 'WebLogic server', 'WEBrick http', 'Zope httpd'}
    # interesting_fun = lambda x: interesting_cluster_check_different_vendors2(x, interesting_vendors)
    # interesting_fun = interesting_cluster_check_different_regexes
    for name in os.listdir(data_prefix):
        if name == "interesting":
            continue
        interesting_cluster_decompositions(f"{data_prefix}{os.sep}{name}", f"{save_prefix}{os.sep}{name}.txt", interesting_f=interesting_fun)
