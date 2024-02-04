import os
from nilsimsa import POPC
import pandas as pd
from tqdm import tqdm
from itertools import combinations

__path_from = "nilsimsa_digests.txt"
__path_to = "nilsimsa.txt"
__threshold = 0


def __convert_hex_to_ints(hexdigest):
    return [int(hexdigest[i:i+2], 16) for i in range(0, 63, 2)]


def nilsimsa_digests_compare(digest1, digest2):
    bit_diff = 0
    for i in range(len(digest1)):
        bit_diff += POPC[digest1[i] ^ digest2[i]]
    return 128 - bit_diff


if __name__ == "__main__":
    df = pd.read_csv(__path_from)
    digests = {}
    for _, row in df.iterrows():
        digests[row["name"]] = __convert_hex_to_ints(row["digest"])
    
    with open(__path_to, 'w') as f:
        for (name_from, name_to) in tqdm(list(combinations(digests.keys(), 2))):
            score = nilsimsa_digests_compare(digests[name_from], digests[name_to])
            if score < __threshold:
                continue
            f.write(f"{name_from} {name_to} {score}\n")
