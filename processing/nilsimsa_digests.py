import os
import pandas as pd
from tqdm import tqdm
from nilsimsa import Nilsimsa

__dir = "/home/andrey.pogrebnoy/data/51/data"
__temp_path = "/home/andrey.pogrebnoy/data/51/temp/nilsimsa_digests.txt"


if __name__ == "__main__":
    records = []
    for name in tqdm(os.listdir(__dir)):
        with open(f"{__dir}{os.sep}{name}", 'r') as f:
            records.append({"name": name, "digest": Nilsimsa(f.read()).hexdigest()})
    df = pd.DataFrame.from_records(records)
    df.to_csv(__temp_path, index=False)
