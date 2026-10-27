"""
Reset the SQLite database and re-seed from data files.
Run from the repo root: python scripts/reset_seed.py
"""
import asyncio
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

async def main():
    from app.database import engine, Base
    from app.main import _seed_zones, _seed_facilities, AsyncSessionLocal
    from app.models import LostReport, Incident, Subscription

    # Drop and recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _seed_zones(session)
        await _seed_facilities(session)

    print("Database reset and re-seeded.")

asyncio.run(main())
