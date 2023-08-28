# Data Browser

Context stored in [Storage](storage.md) can be visualized through Data Browser.
Data Browser is a web application that shows hierarchy of contexts and attached data.

## Data Browser in Jupyter

In Jupyter notebook, a storage have a method `.display` that shows a 
Data Browser directly in Jupyter notebook.

```python
storage = FileStorage("./my-directory")
storage.display() # Shows Data browser in the resulting Jupyter output cell
```

## Starting server

Server for Data Browser can be also started manually. It returns a handle where a HTTP server
is running. 

```python
storage = FileStorage("./my-directory")
storage.start_server()  # returns <ServerHandle http://localhost:PORT>
```

## Embedded HTML

TODO

## Data with MIME type

TODO