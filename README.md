# Research framework for structured deliberation and agent interactions

The goal of this library is to make writing, using, and debugging structured and nested queries easier and composable, and to allow experimenting with LLM-based agent interactions. The framework is designed to also support game theoretic (i.e. not language based) and other agents and games, and we have further goals beyond that, but the main focus is on ease of use of LLMs in agent interactions at the moment.

_Note: This repo will be renamed soon, "querychains" is a very provisional name, as the focus shifted from low-level LLM interactions such as parsing etc to interactions_

## Install

This repo is using [poetry](https://python-poetry.org/) for package management.

```commandline
poetry install
```

## Run

The easiest way to interact with the code is via JupyterLab:

```commandline
poetry run jupyter lab
```

Open the link in your browser; `cars.ipynb` is a good starting point.

## API Keys

You need to provide API keys for OpenAI or Anthropic LLM services to use them. The recommended way is to set the `OPENAI_API_KEY` and optionally `OPENAI_API_ORG`, resp. `ANTHROPIC_API_KEY` environment variables before starting jupyterlab. We do not recommend storing your API keys in your source files.

For convenince, you can store your keys in `.env` file in the notebook directory. The file is ignored by `git` by default.

```text
OPENAI_API_KEY=sk-...
OPENAI_API_ORG=org-...
ANTHROPIC_API_KEY=sk-ant-...
```

You can then load the variables from `.env` in a jupyter notebook using [dotenv](https://github.com/theskumar/python-dotenv):

```text
%load_ext dotenv
%dotenv
```
