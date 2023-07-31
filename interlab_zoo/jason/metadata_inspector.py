# read time per run
import datetime

import pandas as pd

from interlab import context


def main():
    # arg-parse Directory for storing contexts (structured logs)
    # args = argparse.ArgumentParser()
    # args.add_argument(dest="storage", type=Path)
    # args = args.parse_args()
    # storage_dir = args.storage

    storage_dir = "/home/jason/dev/acs/interlab/results/2023-07-29-19-37-32"
    storage = context.FileStorage(storage_dir)

    # get all root contexts
    roots = storage.read_roots(storage.list())
    uid_to_duration = {}
    for root in roots:
        # print(root["uid"])
        start_time = datetime.datetime.fromisoformat(root["start_time"])
        end_time = datetime.datetime.fromisoformat(root["end_time"])
        duration = end_time - start_time
        duration_sec = round(duration.total_seconds())
        # print(f"{duration_sec=}")
        uid_to_duration[root["uid"]] = duration_sec

    print(f"{uid_to_duration=}")

    # convert to pandas Series
    uid_to_duration = pd.Series(uid_to_duration)
    print(f"{uid_to_duration.describe(percentiles=[0.1,0.9])=}")


if __name__ == "__main__":
    main()
