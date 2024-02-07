import os
import json
import pandas as pd
import consts as C
from typing import Optional, List, Dict
from tqdm import tqdm

__cur_file_dir = os.path.dirname(os.path.abspath(__file__))
__regexes_split_by = "###"

__main_json_path = f"{__cur_file_dir}{os.sep}rooster{os.sep}results{os.sep}{C.ANALYZE}.json"
__parsed_body_prefix = f"{__cur_file_dir}{os.sep}rooster{os.sep}data{os.sep}{C.ANALYZE}"
__save_nodes_path = f"{__cur_file_dir}{os.sep}db{os.sep}import{os.sep}nodes.csv"
__clusters_path = None

__keys_status_code = ["data", "http_tls", "result", "response", "status_code"]
__keys_server = ["data", "http_tls", "result", "response", "headers", "server"]
__keys_products = ["data", "http_tls", "result", "products"]
__keys_body = ["data", "http_tls", "result", "response", "body"]
__label = "Node"


def __by_keys(data, keys):
    for key in keys:
        data = data.get(key, None)
        if data is None:
            break
    return data


def __status_code(data) -> Optional[int]:
    code = __by_keys(data, __keys_status_code)
    if code is not None:
        return int(code)
    return None


def __fix_lists(data: List[str]) -> List[str]:
    res = set()
    for element in data:
        if "," in element:
            for subelement in element.split(","):
                res.add(subelement.strip())   
        else:
            res.add(element)
    return list(res)


def __server(data) -> List[str]:
    servers = __by_keys(data, __keys_server)
    if servers is None:
        return []
    return __fix_lists(servers)


def __vendors(data) -> List[str]:
    vendorproductnames = []
    products = __by_keys(data, __keys_products)
    if products is not None:
        for product in products:
            vendor = product.get("vendorproductname", None)
            if vendor is not None:
                vendorproductnames.append(vendor)
    return __fix_lists(vendorproductnames)


def __cpe(data) -> List[str]:
    cpes = []
    products = __by_keys(data, __keys_products)
    if products is not None:
        for product in products:
            cpe = product.get("cpe", None)
            if cpe is not None:
                for cpe_i in cpe:
                    cpes.append(cpe_i)
    return __fix_lists(cpes)


def __regexes(data) -> str:
    regexes = []
    products = __by_keys(data, __keys_products)
    if products is not None:
        for product in products:
            regex = product.get("regex", None)
            if regex is not None:
                assert __regexes_split_by not in regex, f"wrong regex splitter: {__regexes_split_by}; regex: {regex}"
                regexes.append(regex.replace('"', '""'))
    if len(regexes) == 0:
        return ""
    return f"\"{__regexes_split_by.join(regexes)}\""


def nodes(main_json_path: str, parsed_body_prefix: str, save_nodes_path: str):
    records = []
    lines = []
    with open(main_json_path, 'r') as f:
        lines = f.readlines()
    for path in os.listdir(parsed_body_prefix):
        index = int(path[:path.rfind(".")])
        try:
            data = json.loads(lines[index])
        except: # one incorrect json in outputzgrab2443-tls-networks-ru-v3-3-top30000
            continue
        ip = data.get("ip", None)
        domain = data.get("domain", None)
        status_code = __status_code(data)
        server = ";".join(__server(data))
        vendors = ";".join(__vendors(data))
        cpes = ";".join(__cpe(data))
        regexes = __regexes(data)
        if parsed_body_prefix is not None:
            path = f"{parsed_body_prefix}{os.sep}{path}"
        records.append({"index:ID": index, "path": path, "ip": ip, "domain": domain, "status_code:int": status_code, "server:string[]": server, "vendors:string[]": vendors, "cpe:string[]": cpes, "regexes": regexes, ":LABEL": __label})
    df = pd.DataFrame.from_records(records)
    df.to_csv(save_nodes_path, index=None)


def nodes_big(main_json_path: str, parsed_body_prefix: str, save_nodes_path: str):  # if json is big enough
    with open(main_json_path, 'r') as fr, open(save_nodes_path, 'w') as fw:
        fw.write("index:ID,path,ip,domain,status_code:int,server:string[],vendors:string[],cpe:string[],regexes,:LABEL\n")
        index = -1
        while True:
            line = fr.readline()
            if not line:
                break
            index += 1

            try:
                data = json.loads(line)
            except BaseException as ex: # one incorrect json in outputzgrab2443-tls-networks-ru-v3-3-top30000
                continue
            body = data
            for key in __keys_body:
                body = body.get(key)
                if body is None:
                    break
            if body is None:
                continue

            ip = data.get("ip", None)
            domain = data.get("domain", None)
            status_code = __status_code(data)
            server = ";".join(__server(data))
            vendors = ";".join(__vendors(data))
            cpes = ";".join(__cpe(data))
            regexes = __regexes(data)
            path = f"{index}.html"
            if parsed_body_prefix is not None:
                path = f"{parsed_body_prefix}{os.sep}{path}"
            fw.write(f"{index},{path},{ip},{domain},{status_code},{server},{vendors},{cpes},{regexes},{__label}\n")


def nodes_add_labels(nodes_path: str, clusters_path: str):      # label should be in the end of line
    nodes_path_to = nodes_path.replace(".csv", "_labeled.csv")  # temp file

    index_to_labels: Dict[str, List[str]] = {}
    for path in tqdm(os.listdir(clusters_path)):
        label_prefix = path.replace('.txt', '')
        with open(f"{clusters_path}{os.sep}{path}", 'r') as f:
            i = -1
            while True:
                line = f.readline()
                if not line:
                    break
                i += 1
                label = f"{label_prefix}_{i}"
                for index in line.split():
                    if index not in index_to_labels:
                        index_to_labels[index] = []
                    index_to_labels[index].append(label)
    with open(nodes_path, 'r') as fr, open(nodes_path_to, 'w') as fw:
        fw.write(fr.readline())
        while True:
            line = fr.readline()
            if not line:
                break
            index = line[:line.index(",")]
            if index in index_to_labels:
                extra_labels = ";".join(index_to_labels[index])
                fw.write(f"{line[:-1]};{extra_labels}\n")
            else:
                fw.write(line)

    # os.rename(nodes_path_to, nodes_path)


if __name__ == "__main__":
    nodes(__main_json_path, __parsed_body_prefix, __save_nodes_path)
    # nodes_big(__main_json_path, __parsed_body_prefix, __save_nodes_path)

    if __clusters_path is not None:
        nodes_add_labels(__save_nodes_path, __clusters_path)
