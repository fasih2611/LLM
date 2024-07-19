from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import anthropic
import json
import os
import io
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
app = FastAPI()
# Can Remove
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Anthropic API call failed: {str(e)}"
        )


@app.post("/api/ingest-data")
async def ingest_data(data: SalesData):
    global sales_data
    try:
        if data.data.startswith("{"):  # JSON
            df = pd.read_json(data.data)
        else:  # CSV
            # CSV in string causes issues
            csv_data = io.StringIO(data.data)
            df = pd.read_csv(csv_data)
        sales_data = df.to_dict("records")
        return {"message": "Data ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Data ingestion failed: {str(e)}")


@app.get("/api/representative-performance/{rep_name}")
async def representative_performance(rep_name: str):
    rep_data = [sale for sale in sales_data if sale["representative"] == rep_name]
    if not rep_data:
        raise HTTPException(status_code=404, detail="Representative not found")

    prompt = f"Analyze the following sales data for {rep_name} and provide detailed performance feedback:\n{json.dumps(rep_data, indent=2)}"
    feedback = call_anthropic_api(prompt)
    return {"representative": rep_name, "feedback": feedback}


@app.get("/api/team-performance")
async def team_performance():
    prompt = f"Analyze the following sales data and provide comprehensive overall team performance feedback:\n{json.dumps(sales_data, indent=2)}"
    feedback = call_anthropic_api(prompt)
    return {"team_feedback": feedback}


@app.get("/api/sales-trends")
async def sales_trends():
    prompt = f"Analyze the following sales data, identify key trends, and provide a detailed sales forecast:\n{json.dumps(sales_data, indent=2)}"
    analysis = call_anthropic_api(prompt)
    return {"trends_and_forecast": analysis}


@app.get("/api/top_unit")
async def top_unit(unit_id: str):
    unit_data = [sale for sale in sales_data if sale.get("unit_id") == unit_id]
    if not unit_data:
        raise HTTPException(status_code=404, detail="Unit not found")

    prompt = f"""Analyze the following unit sales data and provide a detailed performance analysis and feedback:

Unit Data: {json.dumps(unit_data, indent=2)}

Please include:
1. Overall performance metrics
2. Comparison to similar units
3. Pricing strategy effectiveness
4. Actionable recommendations for improvement"""

    analysis = call_anthropic_api(prompt)
    return {"unit_id": unit_id, "analysis": analysis}


@app.get("/api/unit_price_history")
async def unit_price_history(unit_type: Optional[str] = None):
    if unit_type:
        relevant_data = [
            sale for sale in sales_data if sale.get("unit_type") == unit_type
        ]
    else:
        relevant_data = sales_data

    prompt = f"""Analyze the following sales data and identify the units with the biggest price changes downwards:

Sales Data: {json.dumps(relevant_data, indent=2)}

Please provide:
1. List of units with significant price decreases
2. Analysis of factors contributing to price decreases
3. Potential implications for future pricing strategies"""

    analysis = call_anthropic_api(prompt)
    return {"analysis": analysis}


@app.get("/api/building_deals")
async def building_deals(
    neighborhood: Optional[str] = None, building_type: Optional[str] = None
):
    relevant_data = sales_data
    if neighborhood:
        relevant_data = [
            sale for sale in relevant_data if sale.get("neighborhood") == neighborhood
        ]
    if building_type:
        relevant_data = [
            sale for sale in relevant_data if sale.get("building_type") == building_type
        ]

    prompt = f"""Analyze the following sales data and identify the buildings that are the best deals:

Sales Data: {json.dumps(relevant_data, indent=2)}

Please provide:
1. List of top buildings offering the best value
2. Factors contributing to their 'best deal' status
3. Comparison with average market prices
4. Recommendations for potential buyers or investors"""

    analysis = call_anthropic_api(prompt)
    return {"analysis": analysis}
