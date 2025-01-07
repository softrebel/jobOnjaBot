from prisma import Prisma


prisma = Prisma(auto_register=True)


def init_db():
    prisma.connect()
    # await db.connect()


def close_db():
    prisma.disconnect()


def get_client() -> Prisma:
    return prisma
