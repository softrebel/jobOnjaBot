from prisma.models import JobPlatform
from src._core.database import prisma


def run():
    prisma.connect()
    try:
        JobPlatform.prisma().create(
            {
                "name": "jobinja",
                "label": "جابینجا",
                "link": "https://jobinja.ir/",
            }
        )
    except Exception as e:
        print(e)
    finally:
        prisma.disconnect()


if __name__ == "__main__":
    run()
