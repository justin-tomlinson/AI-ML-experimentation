import asyncio
import uvicorn
import os
import requests
#import boto3
import logging
from pydantic import BaseModel
from fastai.text import *
from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse

logging.basicConfig(filename='run.log',level=logging.INFO)

#model_bucket = 'intellipharm.machine-learning.models'
#model_key_prefix = 'product_categorisation'

L2_model_url = 'https://storage.googleapis.com/jt-machine-learning-models/product-categorisation/model-2-level-export.pkl'
L3_model_url = 'https://storage.googleapis.com/jt-machine-learning-models/product-categorisation/model-2-level-export.pkl'

L2_model = 'model-2-level-export.pkl'
L3_model = 'model-3-level-export.pkl'

#l2_item_key = f'{model_key_prefix}/{L2_model}'
#l3_item_key = f'{model_key_prefix}/{L3_model}'

path = Path(__file__).parent

app = FastAPI(
    title="Protagee (Prod-Tag-ee)",
    description="""This is a POC where a NLP model has been trained on 
    the product descriptions of over 3500 pharmacy stores stock files. This service 
    takes a text string (product name) and classifies it across 2 or 3 
    levels a Master Product Hierarchy""",
    version="0.0.1"
    )
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])


# Model for the prediction result
class L3PredictionResult(BaseModel):
    text: str
    catL1: str
    catL2: str
    catL3: str
    confidence: float


# Model for the prediction result
class L2PredictionResult(BaseModel):
    text: str
    catL1: str
    catL2: str
    confidence: float


# Model for the prediction request
class PredictionRequest(BaseModel):
    text: str


async def download_file(url, dest):
    """Download the model from the specified S3 Bucket to a
    local location

    If the file already exists then just Return.
    """
    if os.path.exists(dest):
        logging.info(f'Local model {dest} found.')
        return
    try:
        logging.info(f'Local model {dest} not found. Attempting download.')
        r = requests.get(url, allow_redirects=True)
        open(dest, 'wb').write(r.content)
        return
    except RuntimeError as e:
        logging.critical(f'Model could not be downloaded.')
        print(e)
        raise RuntimeError(e)



# Load in a FastAI model
async def setup_learner(url, model_name):
    """Set up a learner class for the FastAI model.

    This first calls the download_file() function to get a local copy
    of the model file.

    Returns a FastAi learner object.
    """
    logging.info(f'Checking if local model {model_name} exists...')
    await download_file(
        url = url,
        dest = os.path.join(os.getcwd(), 'app', 'models', model_name)
        )
    try:
        logging.info(f'Loading local model {model_name}.')
        learn = load_learner(
            os.path.join(os.getcwd(), 'app', 'models'),
            model_name
            )
        logging.info(f'Local model {model_name} loaded.')
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = """\n\nThis model was trained with an old version
             of fastai and will not work in a CPU environment.
            \n\nPlease update the fastai library in your training environment
             and export your model again."""
            raise RuntimeError(message)
        else:
            raise

loop = asyncio.get_event_loop()

tasks = [
    asyncio.ensure_future(
        setup_learner(
            url= L2_model_url,
            model_name = L2_model)),
    asyncio.ensure_future(
        setup_learner(
            url= L3_model_url,
            model_name = L3_model))
    ]

learn_l2 = loop.run_until_complete(asyncio.gather(*tasks))[0]
learn_l3 = loop.run_until_complete(asyncio.gather(*tasks))[1]

loop.close()

@app.get(
    "/",
    tags = ["Home Page"],
    summary = 'This gets the homepage of the app'
    )
async def homepage():
    html_file = os.path.join(os.getcwd(), 'app', 'view', 'index.html')
    return HTMLResponse(open(html_file, "r").read())

@app.post(
    '/classify/3_levels',
    response_model = L3PredictionResult,
    tags = ["Classify - Product Tree"],
    summary = 'Classify a Product to 3 Levels',
    response_description='The prediction for the product',
    )
async def classify_l3(req: PredictionRequest):
    """
    Classify a product name to all 3 levels of the Product Hierarchy.
     
     ***Note:*** *The confidence may be lower in these cases as there is substantially more combinations to predict on.*
    """
    cat, pred_idx, preds = learn_l3.predict(req.text)
    cats = str(cat).split('>',3)
    res = L3PredictionResult(
        text = req.text,
        catL1 = cats[0],
        catL2 = cats[1],
        catL3 = cats[2],
        confidence = preds[pred_idx.item()].item()
    )
    logging.info(f'prediction for l3 Model: {res}')
    return res

@app.post(
    '/classify/2_levels',
    response_model = L2PredictionResult,
    tags = ["Classify - Product Tree"],
    summary = 'Classify a Product to 2 Levels',
    response_description='The prediction for the product',
    )
async def classify_l2(req: PredictionRequest):
    """
    Classify a product name to the first 2 levels of the Product Hierarchy.
    """
    cat, pred_idx, preds = learn_l2.predict(req.text)
    cats = str(cat).split('>',3)
    res = L2PredictionResult(
        text = req.text,
        catL1 = cats[0],
        catL2 = cats[1],
        confidence = preds[pred_idx.item()].item()
    )
    logging.info(f'prediction for l2 Model: {res}')
    return res

if __name__ == '__main__':
    if 'serve' in sys.argv:
        logging.info(f'Starting product classification service.')
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
