from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():

    df = pd.read_csv("2026.csv")
    df = df.fillna("")

    return f"""
    <html>
    <head>
        <title>Dataset 2026</title>
    </head>
    <body>
        <h1>Data CSV</h1>

        {df.head(100).to_html(index=False)}

    </body>
    </html>
    """