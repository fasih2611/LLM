# Requirements
  1. FastAPI==0.111.1
  2. Pandas==2.0.3
  3. Pydantic==1.10.8
  4. anthropic==0.31.2
  5. Python==3.11.5

# Usage
The following is a Fastapi that utilizes anthropics Claude opus 3 for spreadsheet analysis from within a CSV or Json
## /ingest-data 
Must be called first to send data, accepts Json or CSV
## /representative-performance/$name
gives representative specific information, provided the representative was within the spreadsheet
returns {"representative": rep_name, "feedback": feedback}
## /team-performance
evaluates the entire team's performance
returns {"team_feedback": feedback}
## /sales-trends
gives analysis on the sheet
returns {"trends_and_forecast": analysis}
