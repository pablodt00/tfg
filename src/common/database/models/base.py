import typing

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

ORMModelClass: typing.TypeAlias = DeclarativeMeta
ORMBaseModel: ORMModelClass = declarative_base()
