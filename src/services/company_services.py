from prisma.models import Company
from prisma.partials import CompanyCreate


def get_company_by_name(name: str) -> Company | None:
    return Company.prisma().find_first(where={"name": name})


def create_company(data: CompanyCreate):
    return Company.prisma().create(
        data={
            "name": data.name,
            "link": data.link,
            "photo_url": data.photo_url,
            "description": data.description,
            "job_platform_id": data.job_platform_id,
        }
    )
