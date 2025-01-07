from prisma.models import Job, Company, JobMeta

from src._core.schemas import JobCreate


def create_job(data: JobCreate):
    return Job.prisma().create(
        data={
            "job_id": data.job_id,
            "title": data.title,
            "description": data.description,
            "link": data.link,
            "company_id": data.company_id,
            "body": data.body,
            "job_plaftorm_id": data.job_plaftorm_id,
            "photo_url": data.photo_url,
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
