import os
import shutil

__batch_sz = 60000
__dir = "data"
__res_dir_template = lambda i: f"parts/{i}"


def main():
    for _, _, filenames in os.walk(__dir):
        i = 0
        while True:
            batch_filenames = sorted(filenames)[__batch_sz*i:__batch_sz*(i+1)]
            if len(batch_filenames) == 0:
                break
            print(i)
            dir_to = __res_dir_template(i)
            os.makedirs(dir_to)
            for filename in batch_filenames:
                shutil.copyfile(f"{__dir}{os.sep}{filename}", f"{dir_to}{os.sep}{filename}")
            i += 1


if __name__ == "__main__":
    main()
