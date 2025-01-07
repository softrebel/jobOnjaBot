from prisma.models import Company
from prisma.partials import CompanyCreate


def create_company(data: CompanyCreate):
    return Company.prisma().create(data)
