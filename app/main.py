from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Daily Planner")


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!doctype html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Daily Planner</title>
        </head>
        <body>
            <main>
                <h1>Daily Planner</h1>
                <p>The application is up and running</p>
            </main>
        </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok"}