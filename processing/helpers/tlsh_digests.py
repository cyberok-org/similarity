import os
import shutil
import subprocess

__batch_sz = 25000
__dir = "data"
__dir_to = "temp"


def main():
    with open("tlsh_digests.txt", 'wb') as f:
        for _, _, filenames in os.walk(__dir):
            i = 0
            while True:
                batch_filenames = filenames[__batch_sz*i:__batch_sz*(i+1)]
                if len(batch_filenames) == 0:
                    break
                print(i)
                shutil.rmtree(__dir_to)
                os.makedirs(__dir_to)
                for filename in batch_filenames:
                    shutil.copyfile(f"{__dir}{os.sep}{filename}", f"{__dir_to}{os.sep}{filename}")
                res = subprocess.run(["tlsh", "-r", "./data"], stdout = subprocess.PIPE, stderr = subprocess.DEVNULL)
                f.write(res.stdout)
                i += 1


if __name__ == "__main__":
    main()
