import os, sys, uuid
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
os.chdir(repo_root)
sys.path.append(str(repo_root))

from dotenv import load_dotenv
load_dotenv()

from app.main import app
from app.database import SessionLocal
from app.models import User, Department, Category, Grievance
from app.auth import hash_password, create_access_token
from fastapi.testclient import TestClient

client = TestClient(app)

def test_rbac_flow():
    db = SessionLocal()
    try:
        # 1. Setup departments
        dept_cs = db.query(Department).filter(Department.name == "Computer Engineering").first()
        if not dept_cs:
            dept_cs = Department(name="Computer Engineering", description="CS Dept")
            db.add(dept_cs)
            db.commit()
            db.refresh(dept_cs)

        dept_mech = db.query(Department).filter(Department.name == "Mechanical Engineering").first()
        if not dept_mech:
            dept_mech = Department(name="Mechanical Engineering", description="Mech Dept")
            db.add(dept_mech)
            db.commit()
            db.refresh(dept_mech)

        # 2. Setup category
        cat = db.query(Category).first()
        if not cat:
            cat = Category(name="Lab Facilities", description="Lab issues")
            db.add(cat)
            db.commit()
            db.refresh(cat)

        # 3. Create or find Admin User
        admin_email = "admin_test@institution.edu"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(name="Admin User", email=admin_email, role="admin", hashed_password=hash_password("AdminPass123!"))
            db.add(admin)
            db.commit()
            db.refresh(admin)

        # 4. Create or find Staff User (CS Department)
        staff_email = "staff_cs_test@institution.edu"
        staff = db.query(User).filter(User.email == staff_email).first()
        if not staff:
            staff = User(name="Staff CS", email=staff_email, role="staff", department_id=dept_cs.id, hashed_password=hash_password("StaffPass123!"))
            db.add(staff)
            db.commit()
            db.refresh(staff)

        # 5. Create or find Student User
        student_email = "student_test@institution.edu"
        student = db.query(User).filter(User.email == student_email).first()
        if not student:
            student = User(name="Student Test", email=student_email, role="student", hashed_password=hash_password("StudentPass123!"))
            db.add(student)
            db.commit()
            db.refresh(student)

        # Tokens
        admin_token = create_access_token({"sub": str(admin.id), "email": admin.email, "role": admin.role})
        staff_token = create_access_token({"sub": str(staff.id), "email": staff.email, "role": staff.role})
        student_token = create_access_token({"sub": str(student.id), "email": student.email, "role": student.role})

        h_admin = {"Authorization": f"Bearer {admin_token}"}
        h_staff = {"Authorization": f"Bearer {staff_token}"}
        h_student = {"Authorization": f"Bearer {student_token}"}

        print("\n--- TEST 1: Role Restrictions on Departments ---")
        # Student trying to create department -> should be 403 Forbidden
        r = client.post("/departments/", json={"name": f"Dept {uuid.uuid4().hex[:5]}"}, headers=h_student)
        print("Student creating department (expect 403):", r.status_code)
        assert r.status_code == 403

        # Admin creating department -> should be 201 Created
        new_dept_name = f"Dept {uuid.uuid4().hex[:5]}"
        r = client.post("/departments/", json={"name": new_dept_name}, headers=h_admin)
        print("Admin creating department (expect 201):", r.status_code)
        assert r.status_code == 201

        print("\n--- TEST 2: Grievance Creation by Student ---")
        # Student creates grievance
        r = client.post("/grievances/", json={
            "complaint": "Computer lab PC #4 monitor is broken",
            "priority": "High",
            "department_id": dept_cs.id,
            "category_id": cat.id
        }, headers=h_student)
        print("Student creating grievance (expect 201):", r.status_code)
        assert r.status_code == 201
        grievance_id = r.json()["id"]
        # Verify submitted_by was automatically set to student.id!
        assert r.json()["submitted_by"] == student.id
        print(f"Grievance #{grievance_id} submitted_by securely set to student id: {r.json()['submitted_by']}")

        print("\n--- TEST 3: Student View Scoping ---")
        r = client.get("/grievances/", headers=h_student)
        print("Student listing grievances (expect 200):", r.status_code)
        assert r.status_code == 200
        # All grievances returned for student must belong to this student
        for g in r.json():
            assert g["submitted_by"] == student.id
        print("All grievances listed for student belong to this student.")

        print("\n--- TEST 4: Staff Department Scoping & Status Updates ---")
        # Staff can view grievances of CS department
        r = client.get("/grievances/", headers=h_staff)
        print("Staff listing grievances (expect 200):", r.status_code)
        assert r.status_code == 200
        for g in r.json():
            assert g["department_id"] == dept_cs.id

        # Student trying to update grievance status -> should be 403 Forbidden
        r = client.post("/grievance-updates/", json={
            "grievance_id": grievance_id,
            "status": "In Progress",
            "note": "Student trying to resolve their own complaint"
        }, headers=h_student)
        print("Student trying to update status (expect 403):", r.status_code)
        assert r.status_code == 403

        # Staff updating CS department grievance -> should be 201 Created
        r = client.post("/grievance-updates/", json={
            "grievance_id": grievance_id,
            "status": "In Progress",
            "note": "Technician has been assigned to inspect PC #4"
        }, headers=h_staff)
        print("Staff updating department grievance (expect 201):", r.status_code)
        assert r.status_code == 201
        assert r.json()["updated_by"] == staff.id
        print("Grievance status updated & timeline entry created by staff!")

        # Verify grievance status changed to "In Progress"
        r = client.get(f"/grievances/{grievance_id}", headers=h_student)
        assert r.json()["status"] == "In Progress"
        print("Parent grievance status verified as 'In Progress'.")

        print("\n--- TEST 5: Timeline Access ---")
        r = client.get(f"/grievance-updates/grievance/{grievance_id}", headers=h_student)
        assert r.status_code == 200
        assert len(r.json()) >= 1
        print("Student can view timeline updates of their grievance:", len(r.json()), "updates found.")

        print("\n✅ ALL RBAC AND AUTHORIZATION TESTS PASSED SUCCESSFULLY! 🎉\n")
    finally:
        db.close()

if __name__ == "__main__":
    test_rbac_flow()

