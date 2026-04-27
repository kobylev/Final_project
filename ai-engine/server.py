from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CodeSnippet(BaseModel):
    code: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/classify")
async def classify(snippet: CodeSnippet):
    # TODO: Implement ONNX inference
    return {"label": "IO_Intensive", "confidence": 0.95}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
