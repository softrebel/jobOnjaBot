from pydantic import BaseModel

from datetime import datetime

# JobPlatform


class JobPlatformBase(BaseModel):
    name: str
    link: str


class JobPlatformCreate(JobPlatformBase):
    pass


class JobPlatformUpdate(BaseModel):
    name: str | None = None
    link: str | None = None


class JobPlatformView(JobPlatformBase):
    id: int
    created_at: datetime
    updated_at: datetime
    companies: list[int] = []
    jobs: list[int] = []


# Company


class CompanyBase(BaseModel):
    name: str
    link: str
    job_plaftorm_id: int
    description: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    link: str | None = None
    job_plaftorm_id: int | None = None


class CompanyView(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    jobs: list[int] = []


# Job


class JobBase(BaseModel):
    job_id: str
    title: str
    description: str
    link: str
    photo_url: str | None = None
    body: str | None = None
    company_id: int
    job_plaftorm_id: int


class JobCreate(JobBase):
    job_metas: list["JobMetaCreate"] = []


class JobUpdate(BaseModel):
    job_id: str | None = None
    title: str | None = None
    description: str | None = None
    link: str | None = None
    photo_url: str | None = None
    body: str | None = None
    company_id: int | None = None
    job_plaftorm_id: int | None = None
    job_metas: list["JobMetaUpdate"] = []


class JobView(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime
    job_metas: list[int] = []


# JobMeta


class JobMetaBase(BaseModel):
    job_id: int
    key: str
    value: str


class JobMetaCreate(JobMetaBase):
    pass


class JobMetaUpdate(BaseModel):
    job_id: int | None = None
    key: str | None = None
    value: str | None = None


class JobMetaView(JobMetaBase):
    id: int
    created_at: datetime
    updated_at: datetime
