from prisma.models import JobPlatform

from src._core.schemas import JobCreate


def get_job_platform_by_name(name: str) -> JobPlatform | None:
    return JobPlatform.prisma().find_first(where={"name": name})
