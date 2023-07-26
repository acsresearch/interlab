from interlab import context

if __name__ == '__main__':
    storage = context.FileStorage("logs")  # Directory for storing contexts (structured logs)
    server = storage.start_server()
    print(f"{server.url=}")
