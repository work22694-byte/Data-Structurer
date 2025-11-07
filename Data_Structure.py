from langchain_groq import ChatGroq
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model='openai/gpt-oss-20b')

system = """
You are a Data Structuring and Cleaning Assistant.

Your Job:
- Take the user’s raw, unstructured text (headers, lists, mixed data, etc.).
- Clean and organize it into a clear, structured table Remove Unecessory Keywords like 
(??,etc auto detect them and rewrite short name to full like dept to departement)
- Remove unnecessary symbols, extra spaces, and noise.
- Always write firt letter (capital)
always convert short word t ofull example like HR to Human Resources 
- Detect suspicious or inconsistent values and fix them intelligently 
  (e.g., if 'Age' contains 2027, replace it with an average or estimated correct value).
- Preserve all original names and categories — never rename columns or entries.

Always list by similarity like 
Developer	
Developer	
Developer	
Human Resources
Human Resources
Human Resources

Rules:
- Analyze carefully but never explain or comment.
- Output only clean, well-formatted tabular data.
- Always match the expected number of columns if provided.
- Respect any specific user instructions before generating the final table.
"""

history = []

def data_structurer(Instruction: str, data: str, columns: int):
    """Agent LLM"""
    global history

    max_len = 5
    ai = llm.invoke(f'{system}{history}{Instruction}{data}{columns}')
    history.append([f'You {Instruction}\na AI : {ai.content}'])
    history[:] = history[-max_len:]

    result = ai.content

    # --- Convert Markdown text to DataFrame ---
    lines = [line.strip().strip('|').strip() for line in result.strip().splitlines() if line.strip()]
    lines = [line for line in lines if not set(line) <= set('-| ')]
    clean_text = "\n".join(lines)

    try:
        df = pd.read_csv(StringIO(clean_text), sep='|', engine='python')
        df.columns = df.columns.str.strip()
        df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
    except Exception as e:
        return {"error": f"Failed to parse AI output into DataFrame: {e}", "raw_output": result}

    # --- NaN Summary ---
    total_cells = df.size
    total_nans = df.isna().sum().sum()
    non_nans = total_cells - total_nans
    percent_missing = round((total_nans / total_cells) * 100, 2)

    summary = {
        "Total Rows": df.shape[0],
        "Total Columns": df.shape[1],
        "Total Cells": total_cells,
        "Total NaN Values": int(total_nans),
        "Total Non-NaN Values": int(non_nans),
        "Percentage Missing": f"{percent_missing}%"
    }

    # ✅ Return results instead of just displaying
    return {
        "dataframe": df,
        "summary": summary,
        "raw_output": result
    }
