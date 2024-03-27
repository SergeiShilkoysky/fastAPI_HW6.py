import datetime

from pydantic import BaseModel, Field, EmailStr, SecretStr


class User(BaseModel):
    """ Родительский класс модели Пользователь:
    содержит информацию о зарегистрированных пользователях магазина

    @Parameters
    username: имя;
    lastname: фамилия;
    date_of_birth: birthday of user
    email: адрес электронной почты;
    password: <PASSWORD>.
    """

    username: str = Field(title="username", max_length=32)
    lastname: str = Field(title="lastname", max_length=32)
    # date_of_birth: str = Field(title='date_of_birth', description='use YYYY-MM-DD')
    date_of_birth: datetime.date = Field(..., title='date_of_birth')
    email: EmailStr = Field(title="email", max_length=80, description='use validation email!')
    # password: str = Field(title="Password", max_length=30)
    password: SecretStr = Field(title="password", max_length=32)


class UserWithID(User):
    """ Дочерний класс модели User:

    @Parameter
    user_id: id of the user
    """
    user_id: int = Field(title="ID")


class Product(BaseModel):
    """  Родительский класс модели Товар:
    содержит информацию о доступных товарах, их описаниях и ценах

    @Parameters
     name: название товара;
     # date_of_production: дата изготовления;
     description: описание;
     price: цена за единицу.
     """

    name: str = Field(..., title="name", max_length=128)
    # date_of_production: str = Field(..., description='use YYYY-MM-DD')
    # date_of_production: datetime.date = Field(title='date_of_production', description='use YYYY-MM-DD')
    description: str = Field(..., title="description", max_length=200, description='use max <=200 symbol')
    price: float = Field(..., title="price", ge=0, le=1000, description='use value 0-1000')


class ProductWithID(Product):
    """ Дочерний класс модели Продукт:

    @Parameter
    product_id: id of product
    """
    product_id: int = Field(..., title="id")


class Order(BaseModel):
    """ Родительский класс модели Заказ:
    содержит информацию о заказах, сделанных пользователями

    @Parameters
    user_id: id of the user
    product_id: id of the product
    date_of_order: дата заказа;
    price: цена.
    """

    user_id: int = Field(..., title="id")
    product_id: int = Field(..., title="id")
    
    # date_of_order: str = Field(description='use YYYY-MM-DD')
    date_of_order: datetime.date = Field(..., title='date_of_order')
    # date_of_order: datetime.date = Field(..., title='date_of_order', description='use YYYY-MM-DD')
    order_status: str = Field(..., title="order_status", max_length=30)


class OrderWithID(Order):
    """ Дочерний класс модели Заказ:

    @Parameter
    order_id: id of the order
    """

    order_id: int = Field(..., title="id")
