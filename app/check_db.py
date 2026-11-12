import asyncio

from sqlalchemy import text

from app.database import SessionFactory, engine


async def main():
    try:
        async with SessionFactory() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar_one()
            print(f"Database connection successful. SELECT 1 returned: {value}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())