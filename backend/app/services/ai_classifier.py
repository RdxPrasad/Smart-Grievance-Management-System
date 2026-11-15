import os
import json
from groq import Groq
from sqlalchemy.orm import Session
from app.models import Department, Category
from app.schemas import GrievanceClassificationResponse

def classify_grievance_with_ai(complaint_text: str, db: Session) -> GrievanceClassificationResponse:
    """
    Analyzes a student's grievance text using Groq's Llama-3.3-70b model.
    Dynamically grounds the classification using existing Departments and Categories in PostgreSQL.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment (.env).")

    client = Groq(api_key=api_key)

    # Fetch available departments and categories to ground the AI prompt
    departments = db.query(Department).all()
    categories = db.query(Category).all()

    dept_list_str = "\n".join(
        [f"- ID: {d.id}, Name: {d.name} (Details: {d.description or 'N/A'})" for d in departments]
    ) if departments else "No specific departments configured."

    cat_list_str = "\n".join(
        [f"- ID: {c.id}, Name: {c.name} (Details: {c.description or 'N/A'})" for c in categories]
    ) if categories else "No specific categories configured."

    system_prompt = f"""
You are an expert AI Grievance Classification Engine for an educational institution.
Your job is to read the student complaint, determine the best department, category, and priority.

VALID DEPARTMENTS IN OUR INSTITUTION:
{dept_list_str}

VALID CATEGORIES IN OUR INSTITUTION:
{cat_list_str}

PRIORITY DETERMINATION GUIDELINES:
- Urgent: Safety hazard, live electric wire/sparks, gas/fire, server crash during online exam, sewage overflow.
- High: Major academic/lab disruption (e.g. lab PCs power failure, projector down during class, drinking water cooler broken).
- Medium: Inconvenience, but work can continue (e.g. chair broken, fan makes squeaky sound, Wi-Fi slow in corridor).
- Low: Non-urgent feedback, cosmetic fixes, requests for extra library copies.

INSTRUCTIONS:
1. Match department_id and category_id with the provided list. If none fit, return null.
2. Provide a short reasoning (1-2 sentences) explaining the choice.
3. Provide a clear, professional suggested_title (4-8 words).
4. Assign a confidence_score between 0.0 and 1.0.

You must respond STRICTLY with a valid JSON object matching this schema:
{{
  "department_id": <int or null>,
  "department_name": "<exact name or null>",
  "category_id": <int or null>,
  "category_name": "<exact name or null>",
  "priority": "Low" | "Medium" | "High" | "Urgent",
  "confidence_score": <float between 0.0 and 1.0>,
  "reasoning": "<string>",
  "suggested_title": "<string>"
}}
"""

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Student Complaint:\n\"{complaint_text}\""}
        ],
        model="qwen/qwen3.8-27b",
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    raw_json = response.choices[0].message.content
    parsed_data = json.loads(raw_json)

    return GrievanceClassificationResponse(**parsed_data)