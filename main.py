import os
import random
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load environment variables
load_dotenv()

# Verify API Key
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")

# Load Achievements Data
try:
    df_achievements = pd.read_csv("famous_achievements.csv", sep='|')
except Exception as e:
    print(f"Error loading CSV: {e}")
    df_achievements = pd.DataFrame(columns=["Name", "Age", "Achievement"])

app = FastAPI()

# --- LangChain Setup ---
class TaskDetails(BaseModel):
    summary: str = Field(description="A concise summary of the task.")
    passive_aggressive_flair: str = Field(description="A passive aggressive comment. MUST follow this exact format: 'Oh you're concerned about [Task Summary]? Did you know that [Name] was doing [Achievement] at age [Age]?'")
    due_date: Optional[str] = Field(description="The due date of the task in ISO 8601 format (YYYY-MM-DD). If no date is specified, return null.")

parser = JsonOutputParser(pydantic_object=TaskDetails)

# Random Flair Formats
FLAIR_FORMATS = [
    '"Oh you\'re concerned about [Task Summary]? Did you know that {ach_name} was doing {ach_thing} at age {ach_age}?"',
    '"While you\'re worrying about [Task Summary], {ach_name} was busy doing {ach_thing} at age {ach_age}."',
    '"I see you\'re struggling with [Task Summary]. Just remember that {ach_name} had already {ach_thing} by the time they were {ach_age}."',
    '"[Task Summary] sounds tough, but {ach_name} managed to {ach_thing} at age {ach_age}."',
    '"You\'re worried about [Task Summary]? {ach_name} was already {ach_thing} at age {ach_age}."'
]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a passive aggressive assistant. The current date is {current_date}."),
    ("human", """Extract the task summary and due date from: "{text}".
    
    For the 'passive_aggressive_flair', use the following fact to shame the user:
    Name: {ach_name}
    Age: {ach_age}
    Achievement: {ach_thing}
    
    Format the flair EXACTLY as: {flair_format}
    
    ensure that the text in {ach_thing} is modified to fit the sentence structure and tense.

    {format_instructions}""")
])

chain = prompt | llm | parser

# --- API Models ---
class TaskInput(BaseModel):
    task_description: str

# --- Routes ---

@app.post("/parse-task")
async def parse_task(input_data: TaskInput):
    try:
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Select random achievement
        if not df_achievements.empty:
            row = df_achievements.sample(1).iloc[0]
            ach_name = row['Name']
            ach_age = row['Age']
            ach_thing = row['Achievement']
        else:
            ach_name = "Mozart"
            ach_age = "5"
            ach_thing = "composing symphonies"

        # Select random format
        flair_fmt = random.choice(FLAIR_FORMATS)

        # Invoke LangChain
        result = chain.invoke({
            "text": input_data.task_description,
            "current_date": current_date_str,
            "ach_name": ach_name,
            "ach_age": ach_age,
            "ach_thing": ach_thing,
            "flair_format": flair_fmt,
            "format_instructions": parser.get_format_instructions()
        })
        
        return result
    except Exception as e:
        print(f"Error parsing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Frontend stuff
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
