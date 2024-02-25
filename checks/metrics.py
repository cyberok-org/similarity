from typing import List, Dict, Optional
from pydantic import BaseModel
import pandas as pd


class Node(BaseModel):
    path: str
    ip: str
    domain: Optional[str]
    status_code: int
    server: List[str]
    vendors: List[str]
    cpe: List[str]
    regexes: Optional[str]
 
 
# copypaste from ..local.metrics
def load_nodes(nodes_path: str) -> Dict[int, Node]:
    res = {}
    df = pd.read_csv(nodes_path, sep=",")
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
