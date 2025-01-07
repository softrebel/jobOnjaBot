from prisma.models import Job, Company, JobMeta


Job.create_partial(
    "JobCreate",
    include={
        "job_id",
        "title",
        "description",
        "body",
        "job_metas",
        "job_platform_id",
        "company_id",
    },
)
Company.create_partial(
    "CompanyCreate",
    include={
        "name",
        "link",
        "photo_url",
        "description",
        "job_platform_id",
    },
)

JobMeta.create_partial(
    "JobMetaCreate",
    include={
        "job_id",
        "key",
        "value",
    },
)
