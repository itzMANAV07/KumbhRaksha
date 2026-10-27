"""
Delete all personal data after the Mela window ends.
Removes LostReports, Incidents, and Subscriptions.
Run once after the event: python scripts/purge_after_mela.py
"""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

async def main():
    from sqlalchemy import delete
    from app.database import AsyncSessionLocal
    from app.models import LostReport, Incident, Subscription

    async with AsyncSessionLocal() as session:
        for model in [LostReport, Incident, Subscription]:
            result = await session.execute(delete(model))
            print(f"Deleted {result.rowcount} rows from {model.__tablename__}")
        await session.commit()
    print("Purge complete.")

asyncio.run(main())
