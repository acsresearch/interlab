import argparse

from interlab.context.storage import FileStorage


def main():
    parser = argparse.ArgumentParser(
        prog="interlab", description="Start server for serving data from storage"
    )
    parser.add_argument("directory")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    storage = FileStorage(args.directory)
    storage.start_server(port=args.port)


if __name__ == "__main__":
    main()
