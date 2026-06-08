from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return{
        "message": "F1 race intelligence dashboard API is running!"
    }


@app.get("/health")
def health():
    return{
        "status": "healthy"
    }

