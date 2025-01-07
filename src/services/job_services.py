from prisma.models import Job, Company, JobMeta

from src._core.schemas import JobCreate


def get_job_by_link(link: str) -> Job | None:
    return Job.prisma().find_first(where={"link": link})


def get_job_by_job_id(job_id: str) -> Job | None:
    return Job.prisma().find_first(where={"job_id": job_id})


def create_job(data: JobCreate):
    return Job.prisma().create(
        data={
            "job_id": data.job_id,
            "title": data.title,
            "description": data.description,
            "link": data.link,
            # "company_id": data.company_id,
            "body": data.body,
            # "job_platform_id": data.job_platform_id,
            "job_platform": {"connect": {"id": data.job_platform_id}},
            "company": {"connect": {"id": data.company_id}},
            "job_metas": {
                "create": [
                    {
                        "key": job_meta.key,
                        "value": job_meta.value,
                    }
                    for job_meta in data.job_metas
                ]
            },
        }
    )
