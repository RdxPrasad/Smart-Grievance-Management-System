import os
import sys
from pathlib import Path

# Setup project root import path
repo_root = Path(__file__).resolve().parents[1]
sys.path.append(str(repo_root))

from dotenv import load_dotenv
load_dotenv(repo_root / ".env")

from app.database import SessionLocal
from app.services.ai_classifier import classify_grievance_with_ai

def main():
    db = SessionLocal()
    try:
        test_complaints = [
            (
                "Scenario 1: Electrical Hazard (Rahul)",
                "The ceiling fan is making loud screeching noises and sparks flew out of the switchboard near Row 2 in Lab 304. Smells like burning plastic!"
            ),
            (
                "Scenario 2: Library Book Request",
                "Can the library please purchase 3 more copies of 'Database System Concepts' by Korth for the 5th semester exam preparation?"
            ),
            (
                "Scenario 3: Classroom Facility Breakdown",
                "The overhead HDMI projector in Seminar Hall B is not turning on and keeps blinking red. Our technical symposium presentation is in 2 hours."
            )
        ]

        print("\n" + "="*70)
        print("🤖 TESTING RESOLVERAG AI GRIEVANCE CLASSIFIER")
        print("="*70 + "\n")

        for title, complaint in test_complaints:
            print(f"📝 {title}")
            print(f"Complaint: \"{complaint}\"\n")
            
            # Call our AI Service
            result = classify_grievance_with_ai(complaint, db)
            
            print("--- AI CLASSIFICATION RESULT ---")
            print(f"🏷️  Title:       {result.suggested_title}")
            print(f"🏢 Department:  {result.department_name} (ID: {result.department_id})")
            print(f"📂 Category:    {result.category_name} (ID: {result.category_id})")
            print(f"🚨 Priority:    {result.priority}")
            print(f"🎯 Confidence:  {result.confidence_score * 100:.1f}%")
            print(f"💡 Reasoning:   {result.reasoning}")
            print("-" * 70 + "\n")

        print("✅ ALL CLASSIFICATIONS COMPLETED SUCCESSFULLY! 🎉\n")
    finally:
        db.close()

if __name__ == "__main__":
    main()