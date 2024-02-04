import json
import os
import shutil

__keys = ["data", "http_tls", "result", "response", "body"]
__prefix = "/home/andrew/cyberok/duplicate/rooster/data/outputzgrab2443-tls-cokhostdomains"
__main_json_path = "/home/andrew/cyberok/similarity/rooster/results/outputzgrab2443-tls-cokhostdomains.json"
# outputzgrab2443-tls-cokhostdomains.json  outputzgrab2443-tls-networks-ru-v3-3-top30000.json  outputzgrab2443-tls-networks-ru-v3-check-gateway.json


def main():
    if os.path.exists(__prefix):
        shutil.rmtree(__prefix)
    os.mkdir(__prefix)
    with open(__main_json_path, 'r') as f:
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
            for key in __keys:
                data = data.get(key)
                if data is None:
                    break
            if data is not None:
                with open(f"{__prefix}/{i}.html", 'w') as f2:
                    f2.write(data)


if __name__ == "__main__":
    main()
