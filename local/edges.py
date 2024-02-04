import os
import consts as C
from typing import Optional

__cur_file_dir = os.path.dirname(os.path.abspath(__file__))
__files_prefix = "." # f"{__cur_file_dir}{os.sep}rooster{os.sep}analysis{os.sep}{C.ANALYZE}"
__db_import_prefix = f"{__cur_file_dir}{os.sep}db{os.sep}import"
__header = ":START_ID,:END_ID,score:int,:TYPE"
__buf_size = 1_000_000_000


def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, 'rb') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            if remaining_size == file_size and buffer[-1] == ord('\n'):
                buffer = buffer[:-1]
            remaining_size -= buf_size
            lines = buffer.split(b'\n')
            if segment is not None:
                lines[-1] += segment
            segment = lines[0]
            lines = lines[1:]
            for line in reversed(lines):
                yield line.decode()
        if segment is not None:
            yield segment.decode()


def format_ssdeep(path: str, score_filter=20, save_to_name="ssdeep.csv", save_path_prefix: Optional[str] = None):
    if save_path_prefix is None:
        save_path_prefix = __db_import_prefix
    with open(f"{__files_prefix}{os.sep}{path}", 'r') as fr, open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")
        while True:
            line = fr.readline()
            if not line:
                break
            parts = line.split()
            score = int(parts[3][1:-1])
            if score < score_filter:
                continue
            index_from = parts[0][parts[0].rfind("/") + 1 : parts[0].rfind(".")]
            index_to = parts[2][parts[2].rfind("/") + 1 : parts[2].rfind(".")]
            # if index_from >= index_to:
            #     continue
            fw.write(f"{index_from},{index_to},{score},ssdeep\n")


def format_ssdeep_rev(path: str, score_filter=20, save_to_name="ssdeep.csv", save_path_prefix: Optional[str] = None):
    with open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")

        path_from = f"{__files_prefix}{os.sep}{path}"

        paused = True
        while paused:
            paused = False
            sz = 0

            for line in reverse_readline(path_from):
                sz += len(line) + 1

                parts = line.split()
                score = int(parts[3][1:-1])
                if score < score_filter:
                    if (sz > __buf_size):
                        paused = True
                        break
                    continue
                index_from = parts[0][parts[0].rfind("/") + 1 : parts[0].rfind(".")]
                index_to = parts[2][parts[2].rfind("/") + 1 : parts[2].rfind(".")]
                # if index_from >= index_to:
                #     if (sz > __buf_size):
                #         paused = True
                #         break
                #     continue
                fw.write(f"{index_from},{index_to},{score},ssdeep\n")

                if (sz > __buf_size):
                    paused = True
                    break

            if paused:
                assert os.system(f"truncate -s \"-{sz}\" \"{path_from}\"") == 0, sz


def format_tlsh(path: str, score_filter=300, save_to_name="tlsh.csv", save_path_prefix: Optional[str] = None):
    if save_path_prefix is None:
        save_path_prefix = __db_import_prefix
    with open(f"{__files_prefix}{os.sep}{path}", 'r') as fr, open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")
        while True:
            line = fr.readline()
            if not line:
                break
            parts = line.split()
            score = int(parts[2])
            if score > score_filter:
                continue
            index_from = parts[0][parts[0].rfind("/") + 1 : parts[0].rfind(".")]
            index_to = parts[1][parts[1].rfind("/") + 1 : parts[1].rfind(".")]
            fw.write(f"{index_from},{index_to},{score},tlsh\n")


def format_mrsh(path: str, score_filter=20, save_to_name="mrsh.csv", save_path_prefix: Optional[str] = None):
    if save_path_prefix is None:
        save_path_prefix = __db_import_prefix
    with open(f"{__files_prefix}{os.sep}{path}", 'r') as fr, open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")
        while True:
            line = fr.readline()
            if not line:
                break
            parts = line.split()
            score = int(parts[4])
            if score < score_filter:
                continue
            index_from = parts[0][:parts[0].rfind(".")]
            index_to = parts[2][:parts[2].rfind(".")]
            fw.write(f"{index_from},{index_to},{score},mrsh\n")


def format_nilsimsa(path: str, score_filter=0, save_to_name="nilsimsa.csv", save_path_prefix: Optional[str] = None):
    if save_path_prefix is None:
        save_path_prefix = __db_import_prefix
    with open(f"{__files_prefix}{os.sep}{path}", 'r') as fr, open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")
        while True:
            line = fr.readline()
            if not line:
                break
            parts = line.split()
            score = int(parts[2])
            if score < score_filter:
                continue
            index_from = parts[0][:parts[0].rfind(".")]
            index_to = parts[1][:parts[1].rfind(".")]
            fw.write(f"{index_from},{index_to},{score},nilsimsa\n")


def format_simhash(path: str, score_filter=20, save_to_name="simhash.csv", save_path_prefix: Optional[str] = None):
    if save_path_prefix is None:
        save_path_prefix = __db_import_prefix
    with open(f"{__files_prefix}{os.sep}{path}", 'r') as fr, open(f"{save_path_prefix}{os.sep}{save_to_name}", 'w') as fw:
        fw.write(f"{__header}\n")
        while True:
            line = fr.readline()
            if not line:
                break
            parts = line.split()
            score = int(parts[2])
            if score > score_filter:
                continue
            index_from = parts[0][:parts[0].rfind(".")]
            index_to = parts[1][:parts[1].rfind(".")]
            fw.write(f"{index_from},{index_to},{score},simhash\n")


if __name__ == "__main__":
    # format_ssdeep("ssdeep.txt", score_filter=70)
    # format_tlsh("tlsh.txt", score_filter=55)
    # format_mrsh("mrsh.txt", score_filter=30)
    # format_nilsimsa("nilsimsa.txt", score_filter=110)
    # format_simhash("simhash.txt", score_filter=4)
    pass
