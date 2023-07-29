import argparse
from pathlib import Path

from interlab import context


def main():
    # arg-parse Directory for storing contexts (structured logs)
    args = argparse.ArgumentParser()
    args.add_argument(dest="storage", type=Path)
    args = args.parse_args()
    storage = context.FileStorage(args.storage)
    print(Path(storage.directory).absolute())
    server = storage.start_server()
    print(f"{server.url=}")


if __name__ == '__main__':
    main()
