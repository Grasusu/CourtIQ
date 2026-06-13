from fastapi import FastAPI

app = FastAPI(title="CourtIQ API")


@app.get("/health")
def health_check():
    return {"status": "healthy"}

