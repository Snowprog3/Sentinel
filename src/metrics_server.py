import uvicorn
from src.metrics import metrics_app

if __name__ == "__main__":
    uvicorn.run(metrics_app, host="0.0.0.0", port=8000)