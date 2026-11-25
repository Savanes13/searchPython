from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/product/{product_id}")
async def getProduct(product_id):
    return {'item': product_id}

