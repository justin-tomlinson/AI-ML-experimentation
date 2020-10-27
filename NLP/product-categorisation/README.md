## Protagee Service

This repo contains a very basic web service created as a POC to help classify products into a master category structure.

The NLP model was build using FastAI. an example notebook can be found in [/nbs/product-categorisation-2-level.ipynb](/nbs/product-categorisation-2-level.ipynb)

The model is then used in a small web service built using the  [FastAPI](https://fastapi.tiangolo.com/ ) library to quickly define the API methods and includes automatic Swagger and Redoc UI's for testing.

The sample web service is hosted [here]() on GCP.

## Build Locally

You can build the docker image locally by installing Docker and using the following command:

```bash
docker build -t product-categorisation . && docker run --rm -it -p 5000:5000 product-categorisation
```

## Running in Python

To run in pure python, create and activate a new virtual environment with the `requirements.txt` file then run:

```bash
python3 app/server.py serve
```

When running locally you can see the API docs and test using:

 * http://localhost:5000/docs  - Swagger UI
 * http://localhost:5000/redoc  - Redoc UI
 * http://localhost:5000/openapi.json - OpenAPI Spec
