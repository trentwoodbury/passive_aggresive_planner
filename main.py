import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY not found in environment variables.")

app = FastAPI()

class TaskDetails(BaseModel):
    summary: str = Field(description="A concise summary of the task.")
    passive_aggressive_flair: str = Field(description="A passive aggressive comment about the task.")
    due_date: Optional[str] = Field(description="The due date of the task in ISO 8601 format (YYYY-MM-DD). If no date is specified, return null.")

parser = JsonOutputParser(pydantic_object=TaskDetails)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a passive aggressive assistant that extracts task details. The current date is {current_date}."),
    ("human", "Extract the task summary and due date from the following text: {text}. \n{format_instructions}")
])

chain = prompt | llm | parser


class TaskInput(BaseModel):
    task_description: str


@app.post("/parse-task")
async def parse_task(input_data: TaskInput):
    try:
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        result = chain.invoke({
            "text": input_data.task_description,
            "current_date": current_date_str,
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
