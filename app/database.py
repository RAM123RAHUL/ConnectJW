from prisma import Prisma

# Global Prisma client instance
db = Prisma()


async def connect_db():
    """Connect to database"""
    await db.connect()


async def disconnect_db():
    """Disconnect from database"""
    await db.disconnect()


def get_db() -> Prisma:
    """Get database client"""
    return db
