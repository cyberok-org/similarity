import pandas as pd
from tqdm import tqdm
from itertools import combinations

__features = 64
__path_from = "simhash_digests.txt"
__path_to = "simhash.txt"
__threshold = 20


def sumhash_digests_distance(digest1, digest2):
    x = (digest1 ^ digest2) & ((1 << __features) - 1)
    ans = 0
    while x:
        ans += 1
        x &= x - 1
    return ans


if __name__ == "__main__":
    df = pd.read_csv(__path_from)
    digests = {}
    for _, row in df.iterrows():
        digests[row["name"]] = int(row["digest"])

    with open(__path_to, 'w') as f:
        for (name_from, name_to) in tqdm(list(combinations(digests.keys(), 2))):
            score = sumhash_digests_distance(digests[name_from], digests[name_to])
            if score > __threshold:
                continue
            f.write(f"{name_from} {name_to} {score}\n")
