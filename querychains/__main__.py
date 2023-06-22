import argparse

from .server import start_server
from .storage import FileStorage


def main():
    parser = argparse.ArgumentParser(
        prog="querychains", description="Start server for serving data from storage"
    )
    parser.add_argument("directory")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    storage = FileStorage(args.directory)
    server = start_server(storage=storage, port=args.port)
    server.serve_forever()


if __name__ == "__main__":
    main()
