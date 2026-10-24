# mini-rag-app

This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.8 or later

#### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag-app python=3.8
```
3) Activate the environment:
```bash
$ conda activate mini-rag-app
```
## Installation 

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```
Set your environment variables in the `.env` file Like `OPENAI_API_KEY` value.

## Run the fastapi server 
```bash
$  uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
## Run Docker Compose Services

Start MongoDB from the repository root:

```bash
cp docker/.env.example docker/.env
```

Set `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` in `docker/.env`,
then start MongoDB:

```bash
cd docker
docker compose up -d
docker compose ps
```

When running the FastAPI app on your machine, set `MONGO_URI` in `src/.env` to
use the same credentials and the published MongoDB port:
`mongodb://<username>:<password>@localhost:27008/mini_rag_db?authSource=admin`.
URL-encode any special characters in the username or password.

Stop MongoDB with `docker compose down` from the `docker` directory. Its data
remains in the `mongodb_data` Docker volume. The old `docker/mongodb` folder,
if present, is left untouched.
