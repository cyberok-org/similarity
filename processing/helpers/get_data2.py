import json
import os
import shutil
from tqdm import tqdm

__cases = ['http_tls', 'http_ssl', 'http']
__keys = ["result", "response", "body"]
__dir = "/home/andrey.pogrebnoy/data/fofa_top51_httpports_result"
__prefix = "/home/andrey.pogrebnoy/data/51/data"


def main():
    # if os.path.exists(__prefix):
    #     shutil.rmtree(__prefix)
    # os.mkdir(__prefix)
    for _, _, filenames in os.walk(__dir):
        for filename in tqdm(filenames):
            temp = filename[14:]
            port = int(temp[:temp.find("-")])

            with open(f"{__dir}{os.sep}{filename}", 'r') as f:
                i = -1
                while True:
                    line = f.readline()
                    if not line:
                        break
                    i += 1

                    try:
                        data = json.loads(line)
                    except BaseException as ex:
                        print(f"line {i}: {ex}")
                        continue
                    data = data.get("data")
                    if data is None:
                        continue

                    for case in __cases:
                        temp = data.get(case)
                        if temp is None:
                            continue

                        for key in __keys:
                            temp = temp.get(key)
                            if temp is None:
                                break

                        if temp is not None:
                            with open(f"{__prefix}/{port}_{i}.html", 'w', encoding='utf-8') as f2:
                                f2.write(temp)
                            break


if __name__ == "__main__":
    main()
