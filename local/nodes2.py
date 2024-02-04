import os
import json
from typing import Optional, List, Dict
from tqdm import tqdm

__regexes_split_by = "###"

__dir = "/home/andrey.pogrebnoy/data/fofa_top51_httpports_result"
__parsed_body_prefix = "~/51"
__save_nodes_path = "/home/andrey.pogrebnoy/data/51/res/nodes.csv"
__clusters_path = None

__protocols = ['http_tls', 'http_ssl', 'http']

__keys_status_code = ["result", "response", "status_code"]
__keys_server = ["result", "response", "headers", "server"]
__keys_products = ["result", "products"]
__keys_body = ["result", "response", "body"]
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


def nodes_big(dir_json_paths: str, parsed_body_prefix: str, save_nodes_path: str):  # if json is big enough
    with open(save_nodes_path, 'w', encoding='utf-8') as fw:
        fw.write("index:ID,path,ip,domain,protocol,status_code:int,server:string[],vendors:string[],cpe:string[],regexes,:LABEL\n")

        for _, _, filenames in os.walk(dir_json_paths):
            for filename in tqdm(filenames):
                with open(f"{dir_json_paths}{os.sep}{filename}", 'r') as fr:
                    index = -1
                    while True:
                        line = fr.readline()
                        if not line:
                            break
                        index += 1

                        try:
                            json_data = json.loads(line)
                        except BaseException as ex:
                            continue

                        data = json_data.get("data")
                        if data is None:
                            continue

                        for protocol in __protocols:
                            protocol_data = data.get(protocol)
                            if protocol_data is None:
                                continue

                            temp = protocol_data
                            for key in __keys_body:
                                temp = temp.get(key)
                                if temp is None:
                                    break

                            if temp is not None:    # body exist
                                ip = json_data.get("ip", None)
                                domain = json_data.get("domain", None)
                                filename_part = filename[14:]
                                port = int(filename_part[:filename_part.find("-")])
                                data_id = f"{port}_{index}"

                                status_code = __status_code(protocol_data)
                                server = ";".join(__server(protocol_data))
                                vendors = ";".join(__vendors(protocol_data))
                                cpes = ";".join(__cpe(protocol_data))
                                regexes = __regexes(protocol_data)

                                path = f"{data_id}.html"
                                if parsed_body_prefix is not None:
                                    path = f"{parsed_body_prefix}{os.sep}{path}"
                                fw.write(f"{data_id},{path},{ip},{domain},{protocol},{status_code},{server},{vendors},{cpes},{regexes},{__label}\n")
                                break


def nodes_add_labels(nodes_path: str, clusters_path: str):      # label should be in the end of line
    nodes_path_to = nodes_path.replace(".csv", "_labeled.csv")  # temp file

    index_to_labels: Dict[int, List[str]] = {}
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
                    int_index = int(index)
                    if int_index not in index_to_labels:
                        index_to_labels[int_index] = []
                    index_to_labels[int_index].append(label)
    with open(nodes_path, 'r') as fr, open(nodes_path_to, 'w') as fw:
        fw.write(fr.readline())
        while True:
            line = fr.readline()
            if not line:
                break
            index = int(line[:line.index(",")])
            if index in index_to_labels:
                extra_labels = ";".join(index_to_labels[index])
                fw.write(f"{line[:-1]};{extra_labels}\n")
            else:
                fw.write(line)

    os.rename(nodes_path_to, nodes_path)


if __name__ == "__main__":
    # nodes(__main_json_path, __parsed_body_prefix, __save_nodes_path)
    nodes_big(__dir, __parsed_body_prefix, __save_nodes_path)

    # if __clusters_path is not None:
    #     nodes_add_labels(__save_nodes_path, __clusters_path)
