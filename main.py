from fastapi import FastAPI

app=FastAPI(title="EventSphere API")

@app.get("/")
def home():
    return{"message":"Welcome to EventSphere", "status":"running"}