from app.categories.schemas import CreateCategory
from app.models import SuperCategory, SubCategory
from crud import CRUD


class SuperCategoryCRUD(CRUD[SuperCategory, CreateCategory, SuperCategory]):
    pass


class SubCategoryCRUD(CRUD[SubCategory, CreateCategory, SubCategory]):
    pass


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)