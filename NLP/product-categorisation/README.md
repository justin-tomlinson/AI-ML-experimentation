## Protagee Service

This repo contains a very basic web service created as a POC to help classify products into a master category structure.

The NLP model was build using FastAI. an example notebook can be found in [/nbs/product-categorisation-2-level.ipynb](/nbs/product-categorisation-2-level.ipynb)

The model is then used in a small web service built using the  [FastAPI](https://fastapi.tiangolo.com/ ) library to quickly define the API methods and includes automatic Swagger and Redoc UI's for testing/playing.

The wrapper service is ***VERY*** basic. As this was a POC at work, I did not spent a lot of time on the on the web service side including automated testing and error handling. It was primarily developed to show case a backend webservice that uses the model for predictions.

### The Challenge/Use case

I work as a BI Consultant at a company called Intellipharm. We provide analytics and data extraction and aggregation across the pharmacy sector in Australia and New Zealand. Across both countries we extract data from aprox. 4000 pharmacies.

A lot of these pharmacies are owned and run by small business owners. These are often part of a banner group or other management structure which provides central marketing and procurement services.

A common challenge when dealing with sales reporting is master data management and categorisation of products. Each store spells and categorises their products differently. When building consolidated reporting across hundreds of stores we map these products to master products. This is typically done using some identifier (usually EAN barcodes). This presents a challenge as we rely on the stores listing the correct barcodes and products often have multiple barcodes associated with them.

This service uses an NLP model to predict products categorised to 2 and 3 levels of the master product tree purely based on the product description. It could be used to populated suggested categories as the user create a new product record, pre-populating the boxes and make the categorisation more accurate and efficient.

## Sample Service

The sample web service is hosted [here](https://protagee-uw5pq4m64a-ts.a.run.app/docs) on GCP. You can try the 2 different endpoints for a 2-level or 3-level classification. 

The best place to go to get product name ideas is [Chemist Warehouse](https://www.chemistwarehouse.com.au/). Search for any product in the store then get the service to classify it.

Some example responses are:

```json
{
	"text": "Ostelin Calcium & Vitamin D3 - Calcium & Vitamin D - 300 Tablets",
	"catL1": "7-NATURAL MEDICINE",
	"catL2": "702-BONE HEALTH",
	"confidence": 0.9838922023773193
}
```

```json
{
	"text": "Nude by Nature Satin Liquid Lipstick 04 Soft Petal",
	"catL1": "3-COSMETICS/COLOUR",
	"catL2": "302-BUDGET COSMETICS",
	"confidence": 0.9907392263412476
}
```

```json
{
  "text": "Katy Perry Meow Eau de Parfum 100ml",
  "catL1": "31-FRAGRANCES",
  "catL2": "3102-WOMEN",
  "catL3": "3102C-WOMEN",
  "confidence": 0.9027482271194458
}
```

```json
{
  "text": "Ferro-grad C Iron & Vitamin C 30 Tablets",
  "catL1": "7-NATURAL MEDICINE",
  "catL2": "707-WOMEN",
  "catL3": "707B-WOMEN",
  "confidence": 0.7643293738365173
}
```

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
