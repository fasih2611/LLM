from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import anthropic
import json
import os
import io
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
# Can Remove
app.add_middleware(
    CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'],
)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Data storage (in-memory)
sales_data = []

class SalesData(BaseModel):
    data: str  # CSV or JSON string

def call_anthropic_api(prompt):
    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anthropic API call failed: {str(e)}")

@app.post('/ingest-data')
async def ingest_data(data: SalesData):
    global sales_data
    try:
        if data.data.startswith('{'):  # JSON
            df = pd.read_json(data.data)
        else:  # CSV
            # Use StringIO to create a file-like object from the string
            csv_data = io.StringIO(data.data)
            df = pd.read_csv(csv_data)
        sales_data = df.to_dict('records')
        return {"message": "Data ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data ingestion failed: {str(e)}")

@app.get('/representative-performance/{rep_name}')
async def representative_performance(rep_name: str):
    rep_data = [sale for sale in sales_data if sale['representative'] == rep_name]
    if not rep_data:
        raise HTTPException(status_code=404, detail="Representative not found")
    
    prompt = f"Analyze the following sales data for {rep_name} and provide detailed performance feedback:\n{json.dumps(rep_data, indent=2)}"
    feedback = call_anthropic_api(prompt)
    return {"representative": rep_name, "feedback": feedback}

@app.get('/team-performance')
async def team_performance():
    prompt = f"Analyze the following sales data and provide comprehensive overall team performance feedback:\n{json.dumps(sales_data, indent=2)}"
    feedback = call_anthropic_api(prompt)
    return {"team_feedback": feedback}

@app.get('/sales-trends')
async def sales_trends():
    prompt = f"Analyze the following sales data, identify key trends, and provide a detailed sales forecast:\n{json.dumps(sales_data, indent=2)}"
    analysis = call_anthropic_api(prompt)
    return {"trends_and_forecast": analysis}
