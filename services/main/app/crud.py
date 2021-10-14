from app.categories.schemas import CreateCategory, UpdateCategory
from app.models import SuperCategory, SubCategory, Job
from crud import CRUD


class SuperCategoryCRUD(CRUD[SuperCategory, CreateCategory, UpdateCategory]):
    """ Super category CRUD """
    pass


class SubCategoryCRUD(CRUD[SubCategory, CreateCategory, UpdateCategory]):
    """ Sub category CRUD """
    pass


class JobCRUD(CRUD[Job, Job, Job]):
    """ Job CRUD """
    pass


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)
job_crud = JobCRUD(Job)
