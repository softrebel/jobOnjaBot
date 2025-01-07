from prisma.models import Job, Company, JobMeta


Job.create_partial(
    "JobCreate",
    include={
        "job_id",
        "title",
        "description",
        "photo_url",
        "body",
        "job_metas",
        "job_plaftorm_id",
        "company_id",
    },
)
Company.create_partial(
    "CompanyCreate",
    include={
        "name",
        "link",
        "description",
        "job_plaftorm_id",
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
