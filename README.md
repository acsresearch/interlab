<p align="center"><img src="assets/logo3-cut.webp" width="350" height="350"/></p>

# InterLab: A research framework for artificial agent interactions

Welcome to InterLab, a research-focused toolkit created to facilitate study and experimentation in the realm of agent interactions, particularly those based on Language Learning Models (LLMs). Our primary objective is to simplify the process of crafting, deploying, and inspecting complex and structured queries within the context of agent interactions, while also providing robust support for interaction logging, UI and visualization. While we maintain a broad scope and plan to include game theoretic agents and a variety of scenarios, our main emphasis lies in the sphere of LLM interactions.

## Overview

InterLab is composed of several core modules, each providing distinct functionalities:

* `context` offers comprehensive structured logging of nested `Context`s, storage for contexts, and custom visualization of content such as Images, generic HTML, and f-string field substitutions.
* `actor` provides `ActorBase` and a few basic agents, including a generic LLM agent and a web console for playing as an actor, along with an actor memory system.
* `lang_models` includes several LLM APIs, a web-console "LLM" for debugging, and a generic `query_model` wrapper to unify the APIs of our models, LangChain models (both chat and non-chat), and general callable functions while maintaining context logging.
* `queries` presents powerful helpers for advanced queries to the models: querying the model for structured data for any dataclass or Pydantic model, generating schemas optionally, generating examples, and providing robust and comprehensive response parsing for JSON (with repeat and validation options).
* `ui` contains a server for context browser and web consoles (actor and model), along with pre-compiled web apps.
* `utils` encompasses several text utilities, color handling, and other helpers.
* `ext` includes extensions and integrations with other systems, currently Matplotlib and Google Colab.

### InterLab Zoo

The `interlab_zoo` package serves as a repository for specific and opinionated implementations of actors, scenarios, actor memory systems, context post-processing, and other tools that enhance the InterLab project. Its mission is to gather code that is both widely applicable and useful, while maintaining a compact and focused core package.

## Install

**Poetry (recommended).** This repository utilizes [poetry](https://python-poetry.org/) for package management, which is recommended for dependency installation and is mandatory for InterLab development. Poetry automatically generates and manages a virtual environment for you, and also installs `interlab` module itself. If you have poetry installed, running the following command will install InterLab:

```commandline
poetry install
```

**pip and `requirements.txt`.** Alternatively, `pip` can be used to install dependencies with `pip install -r requirements.txt` (core requirements) or `pip install -r requirements-full.txt` (including development tools, Jupyter Lab, etc.; equivalent to `poetry install`).

Please note, when using `pip`, you're responsible for managing any virtual environments and deciding where packages should be installed.

## Run

Jupyter Lab provides the simplest way to interact with the code and design experiments:

```commandline
poetry run jupyter lab
# Or without poetry, in the project root folder:
jupyter lab
```

After running the command, open the provided link in your browser. `notebooks/car_negotiation.ipynb` is a recommended starting point.

### Google Colab

Google Colab often offers a lightweight alternative to setting up InterLab locally on your computer. Interlab comes with built-in colab compatibility and we have prepared a [Template InterLab Colab notebook](https://colab.research.google.com/drive/1ncy02sdPse5KSxi5olbWb51dpW5IuVFq) with common setup and a simple example experiment with two LLMs interacting on behalf of their users.

### Note: API Keys

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
