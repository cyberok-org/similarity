batch_sz = 10000

__alg = "nilsimsa"
__temp_path = f"/home/andrey.pogrebnoy/data/51/temp/nilsimsa_digests.txt"
# __alg = "simhash"
# __temp_path = f"/home/andrey.pogrebnoy/data/51/temp/simhash_digests.txt"

__temp_path_template = lambda name: f"/home/andrey.pogrebnoy/data/51/temp/{__alg}/{name}.txt"


if __name__ == "__main__":
    finish = False
    index = 0
    with open(__temp_path, 'r') as fr:
        header = fr.readline()
        while not finish:
            with open(__temp_path_template(f"data{index}"), 'w') as fw:
                fw.write(header)
                for _ in range(batch_sz):
                    line = fr.readline()
                    if not line:
                        finish = True
                        break
                    fw.write(line)
            index += 1
    print(index)
