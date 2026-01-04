import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.laboratory.department_model import Department, Specialization


async def seed_departments_and_specializations():
    """Seed initial departments and specializations."""
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(Department))
        if result.first():
            print("Data already seeded")
            return
        
        # Create departments
        departments = [
            Department(
                name="General Laboratory",
                code="GENLAB",
                description="General laboratory services"
            ),
            Department(
                name="Microbiology",
                code="MICRO",
                description="Microbiology department"
            ),
            Department(
                name="Pathology",
                code="PATH",
                description="Pathology department"
            ),
            Department(
                name="Hematology",
                code="HEMA",
                description="Hematology department"
            ),
            Department(
                name="Administration",
                code="ADMIN",
                description="Administrative department"
            ),
        ]
        
        # Create specializations
        specializations = [
            Specialization(
                name="General Laboratory",
                code="GENLAB",
                description="General lab work"
            ),
            Specialization(
                name="Clinical Chemistry",
                code="CHEM",
                description="Clinical chemistry"
            ),
            Specialization(
                name="Hematology",
                code="HEMA",
                description="Blood disorders"
            ),
            Specialization(
                name="Immunology",
                code="IMMUNO",
                description="Immune system"
            ),
            Specialization(
                name="Medical Administration",
                code="MEDADMIN",
                description="Medical admin"
            ),
        ]
        
        db.add_all(departments)
        db.add_all(specializations)
        await db.commit()
        
        print(f"Seeded {len(departments)} departments")
        print(f"Seeded {len(specializations)} specializations")


if __name__ == "__main__":
    print("Starting database seeding...")
    asyncio.run(seed_departments_and_specializations())
    print("Seeding complete!")