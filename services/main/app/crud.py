from app.categories.schemas import CreateCategory, UpdateCategory
from app.models import SuperCategory, SubCategory
from crud import CRUD


class SuperCategoryCRUD(CRUD[SuperCategory, CreateCategory, UpdateCategory]):
    """ Super category CRUD """
    pass


class SubCategoryCRUD(CRUD[SubCategory, CreateCategory, UpdateCategory]):
    """ Sub category CRUD """
    pass


super_category_crud = SuperCategoryCRUD(SuperCategory)
sub_category_crud = SubCategoryCRUD(SubCategory)
