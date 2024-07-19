# Requirements
  1. FastAPI==0.111.1
  2. Pandas==2.0.3
  3. Pydantic==1.10.8
  4. anthropic==0.31.2
  5. Python==3.11.5

# Usage
The following is a Fastapi that utilizes anthropics Claude opus 3 for spreadsheet analysis from within a CSV or Json
## /ingest-data 
Must be called first to send data. Accepts JSON or CSV.
- Method: POST
- Body: JSON object with a 'data' field containing the CSV or JSON string
- Returns: {"message": "Data ingested successfully"} on success
## /representative-performance/$NAME
Gives representative-specific information, provided the representative was within the spreadsheet.
- Method: GET
- Parameters:
  - rep_name (string): Name of the representative
- Returns: {"representative": rep_name, "feedback": feedback}
## /team-performance
Evaluates the entire team's performance based on the ingested data.
- Method: GET
- Returns: {"team_feedback": feedback}
## /sales-trends
Provides analysis on the sales trends from the ingested data.
- Method: GET
- Returns: {"trends_and_forecast": analysis}
## /top_unit
Provides detailed performance analysis for a specific unit.
- Method: GET
- Parameters: 
  - unit_id (string): Unique identifier for the unit
- Returns: {"unit_id": unit_id, "analysis": detailed_analysis}
## /unit_price_history
Finds units with significant price decreases, optionally filtered by unit type.
- Method: GET
- Parameters:
  - unit_type (string, optional): Type of unit to filter by
- Returns: {"analysis": price_change_analysis}
## /building_deals
Identifies the best building deals, optionally filtered by neighborhood or building type.
- Method: GET
- Parameters:
  - neighborhood (string, optional): Neighborhood to filter by
  - building_type (string, optional): Type of building to filter by
- Returns: {"analysis": best_deals_analysis}
