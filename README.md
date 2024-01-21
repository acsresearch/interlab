<p align="center"><img src="docs/assets/logo3-cut.webp" width="350" height="350"/></p>

# InterLab - toolkit for multi-agent interactions

<p align="center">
<a href="https://github.com/acsresearch/interlab/releases/latest/"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/acsresearch/interlab" /></a>
<a href="https://pypi.org/project/interlab/"><img alt="PyPI Release" src="https://img.shields.io/pypi/v/interlab"></a>
<a href="https://acsresearch.org/interlab/stable/"><img alt="Documentation" src="https://img.shields.io/badge/Documentation-blue" /></a>
<a href="https://github.com/acsresearch/interlab/actions/workflows/ci.yaml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/acsresearch/interlab/ci.yaml" /></a>
<a href="https://colab.research.google.com/github/acsresearch/interlab/blob/main/notebooks/car_negotiation_colab.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
<a href="https://github.com/acsresearch/interlab/blob/main/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/acsresearch/interlab"></a>
</p>

Welcome to InterLab, a research-focused toolkit created to facilitate study and experimentation in the realm of agent interactions, particularly those based on Language Learning Models (LLMs). Our primary objective is to simplify the process of crafting, deploying, and inspecting complex and structured queries within the context of agent interactions, while also providing robust support for interaction logging, UI and visualization. While we maintain a broad scope and plan to include game theoretic agents and a variety of scenarios, our main emphasis lies in the sphere of LLM interactions.

InterLab is developed at the [Alignment of Complex Systems Research Group](https://acsresearch.org/) and distributed under MIT license (see `LICENSE`).

**Current status: InterLab is in open beta.** InterLab is also active development, we use it internally for our experiments, and we want to make it available to the wider research community. Although we aim to limit the breaking changes between major versions, the API may change substantially as we refine the design and gather information about usage.

If you use InterLab, want to share ideas, feedback or have any questions, please email us at `gavento@acsresearch.org` - we'd be happy to hear from you.

## Overview

InterLab is composed of three main packages:

* `interlab` contains the core functionality and common abstractions of actors, environments, memory, and language model interactions, along with a few helpful scaffolds. The main modules there are:
  - `actor` provides framework for actor interactions, including a generic LLM single-shot agent and a web console for playing as an actor, along with actor memory systems. The agents may be queried for structured (typed JSON-like) or unstuctured actions.
  - `environment` providing abstraction over partially observable environments.
  - `queries` contains powerful helpers for querying the models, in particular querying for any dataclass or Pydantic model with robust response parsing and retries, summarization tools etc.
* `treetrace` offers comprehensive structured logging of nested `TracingNodes`s, storage for traing nodes, and custom visualization of content such as Images, generic HTML, and tracking f-string-like field substitutions in larger text.
* `interlab_zoo` serves as a repository for specific and opinionated implementations of actors, scenarios, actor memory systems, tracing post-processing, and other tools that enhance the InterLab project. Its mission is to gather code that is both widely applicable and useful, while maintaining a compact and focused core package.

Beyond that, some less-tested and experimental code can be found in `experimental` submodules accross the core package.

### Structured interaction log browser

In-notebook or independent browser for the structured logs, with live updates, support for JSON-like structured data and inline visualizations. Captures both high-level interaction structure and the low-level API calls for easy inspection and debugging.
Example screenshots (click to zoom in):

<p align="center"><img src="docs/assets/imgs/context-browser-2.png" alt= "Tracing browser screenshot" width="100%" ></p>

<p align="center"><img src="docs/assets/imgs/context-browser-1.png" alt= "Tracing browser screenshot" width="90%" ></p>

### Example notebooks

You can find Jupyter notebooks with a few worked-out examples [here](https://github.com/acsresearch/interlab/tree/main/notebooks). The notebook [car_negotiation.ipynb](https://github.com/acsresearch/interlab/blob/main/notebooks/car_negotiation.ipynb) is a good starting point for a simple bargaining simulation.

## Installation

You can install the package `interlab` from PyPI using `pip` or any other package manager.

```commandline
pip install interlab
```

### Installation with development tools

This repository utilizes [**Poetry**](https://python-poetry.org/) package management, which is recommended for dependency installation and is required for InterLab development. Poetry automatically generates and manages a virtual environment for you, and also installs `interlab` module itself. If you have poetry installed, running the following command inside this repository will install InterLab:

```commandline
poetry install
```

**pip and `requirements.txt`.** Alternatively, `pip` can be used to install dependencies with `pip install -r requirements.txt` (core requirements) or `pip install -r requirements-full.txt` (including development tools, Jupyter Lab, etc.; equivalent to `poetry install`). To use InterLab in Google Colab, we use the requirements in `requirements-colab.txt` to get aroung some Colab versioning conflicts.

## Development and experiments

Jupyter Lab provides the simplest way to interact with the code and design experiments:

```commandline
poetry run jupyter lab
# Or without poetry, in the project root folder:
jupyter lab
```

After running the command, open the provided link in your browser. `notebooks/car_negotiation.ipynb` is a recommended starting point.

### Google Colab

<a target="_blank" href="https://colab.research.google.com/github/acsresearch/interlab/blob/main/notebooks/car_negotiation_colab.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

Google Colab often offers a lightweight alternative to setting up InterLab locally on your computer. Interlab comes with built-in colab compatibility and we have prepared a [Example InterLab Colab experiment](https://colab.research.google.com/github/acsresearch/interlab/blob/main/notebooks/car_negotiation_colab.ipynb) with common setup and a simple example experiment with two LLMs interacting on behalf of their users.

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

## Contributions and development

To contribute, please submit a pull request with your proposed changes based on the latest `main` branch.

By submitting a pull request for this project, you agree to license your contribution under the MIT license to this project as written in the `LICENSE` file.

## Citing InterLab

If you use InterLab in your researh, please cite it in your work using the "Cite this repository" github gadget or with:

Tomáš Gavenčiak, Ada Böhm: *InterLab [Computer software].* 2023. https://github.com/acsresearch/interlab
