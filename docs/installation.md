

# Getting started

## Installation via Poetry (recommended)

This repository utilizes [poetry](https://python-poetry.org/) for package management, which is recommended for dependency installation and is mandatory for InterLab development. Poetry automatically generates and manages a virtual environment for you, and also installs `interlab` module itself. If you have poetry installed, running the following command will install InterLab:

```commandline
poetry install
```

## Installation via `pip` (alternative)

Alternatively, `pip` can be used to install dependencies with `pip install -r requirements.txt` (core requirements) or `pip install -r requirements-full.txt` (including development tools, Jupyter Lab, etc.; equivalent to `poetry install`).

Please note, when using `pip`, you're responsible for managing any virtual environments and deciding where packages should be installed.


## Running Jupyter Lab

Jupyter Lab provides the simplest way to interact with the code and design experiments:

```commandline
poetry run jupyter lab
# Or without poetry, in the project root folder:
jupyter lab
```

After running the command, open the provided link in your browser. `notebooks/car_negotiation.ipynb` is a recommended starting point.

## Google Colab

Google Colab often offers a lightweight alternative to setting up InterLab locally on your computer. Interlab comes with built-in colab compatibility and we have prepared a [Template InterLab Colab notebook](https://colab.research.google.com/drive/1ncy02sdPse5KSxi5olbWb51dpW5IuVFq) with common setup and a simple example experiment with two LLMs interacting on behalf of their users.

## Note: API Keys

In order to use LLM provider serveics and APIs, you need to generate and provide the corresponding API keys. You can provide the keys as environment variables, via `.env` file, or interactively on every run (e.g. in the colab). Storing keys in the notebook is possible but not recommended (as they easily leak into git or while sharing the code).

API keys can be stored in a `.env` file located in the notebook directory or your home directory. (This file is ignored by `git` by default, providing an additional security measure.) The file is a simple text file with key=value pairs, for example:

```text
OPENAI_API_KEY=sk-...
OPENAI_API_ORG=org-...
ANTHROPIC_API_KEY=sk-ant-...
...
```

You can then import these variables from the `.env` file into a Jupyter notebook using the [dotenv](https://github.com/theskumar/python-dotenv) package:

```python
import dotenv
dotenv.load_dotenv()
```
