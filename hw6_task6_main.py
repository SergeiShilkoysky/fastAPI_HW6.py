""" Задание №6
📌 Необходимо создать базу данных для интернет-магазина. База данных должна
состоять из трех таблиц: товары, заказы и пользователи. Таблица товары должна
содержать информацию о доступных товарах, их описаниях и ценах. Таблица
пользователи должна содержать информацию о зарегистрированных
пользователях магазина. Таблица заказы должна содержать информацию о
заказах, сделанных пользователями.
○ Таблица пользователей должна содержать следующие поля: id (PRIMARY KEY),
имя, фамилия, адрес электронной почты и пароль.
○ Таблица товаров должна содержать следующие поля: id (PRIMARY KEY),
название, описание и цена.
○ Таблица заказов должна содержать следующие поля: id (PRIMARY KEY), id
пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус
заказа.
----------------------------------------------------------------
📌 Создайте модели pydantic для получения новых данных и возврата существующих
 в БД для каждой из трёх таблиц (итого шесть моделей).
📌 Реализуйте CRUD операции для каждой из таблиц через
создание маршрутов, REST API (итого 15 маршрутов).
○ Чтение всех
○ Чтение одного
○ Запись
○ Изменение
○ Удаление
"""
import logging
from datetime import datetime, timedelta
from random import randint
from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError, HTTPException

from hw6_task6_models_data import User, UserWithID, ProductWithID, OrderWithID, Product, Order
from hw6_task6_tables_db import database, users, products, orders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()
    print("Connected to the database.")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Disconnected from the database.")


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup
#     print("connect db")
#     await database.connect()
#     yield
#     # shutdown
#     await database.disconnect()
#     print("disconnect db")
#
#
# app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"Welcome to": "ONLINE STORE"}


MAX_PRICE = 1000


@app.get("/test_data/{user_count}/{product_count}/{order_count}")
async def create_fake_data(user_count: int, product_count: int, order_count: int):
    """Генерация тестовых данных:
    Create a fake user, products and orders"""

    for i in range(user_count):
        query = users.insert().values(
            username=f"User_{i + 1}", lastname=f"Last_name_{i + 1}",
            # date_of_birth=f'{datetime.strptime("2024-03-10", "%Y-%m-%d").date() + timedelta(days=i ** 2)}',
            date_of_birth=datetime.strptime("2024-03-10", "%Y-%m-%d").date() + timedelta(days=i ** 2),
            email=f"user{i + 1}@gmail.com", password=f"pass{i + 1}00000")

        await database.execute(query)
    logger.info(f'{user_count} fake users create - success')

    # return {"list users created": f"{users.select()}"}
    # return users.select()
    for i in range(product_count):
        query = products.insert().values(
            name=f'nameProd{i + 1}',
            # date_of_production=datetime.now(timezone.utc),
            description=f'some_text_{i + 1}',
            price=randint(1, MAX_PRICE))
        await database.execute(query)
    logger.info(f'{product_count} fake products create - success')

    for i in range(order_count):
        query = orders.insert().values(
            user_id=randint(1, user_count),
            product_id=randint(1, product_count),
            # date_of_order=datetime.now(timezone.utc),
            date_of_order=datetime.strptime("2024-03-10", "%Y-%m-%d").date() + timedelta(days=i ** 2),
            order_status=f'status_{i + 1}', )
        await database.execute(query)
    logger.info(f'{order_count} fake orders create - success')

    return {'message': f'created fake data success: '
                       f'{user_count} - users, '
                       f'{product_count} - products, '
                       f'{order_count} - orders.'}


# ------------ Users --------------------------------
@app.get("/users/", response_model=List[UserWithID])
async def get_users():
    """ Returns one from the list of users from the database """

    query = users.select()
    logger.info(' отработал GET запрос на получение списка пользователей')
    return await database.fetch_all(query)


@app.get("/users/{user_id}", response_model=UserWithID)
async def get_user_one(usr_id: int):
    """ Returns one of the users from the database """
    try:
        query = users.select().where(users.c.user_id == usr_id)
        logger.info(f' отработал GET запрос на получение инф. о пользователе по id={usr_id}')
        return await database.fetch_one(query)
    except ResponseValidationError:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.post("/users/", response_model=UserWithID)
async def create_user(user: User):
    """ Create a new user in database"""

    query = users.insert().values(
        username=user.username,
        lastname=user.lastname,
        date_of_birth=user.date_of_birth,
        email=user.email,
        password=user.password.get_secret_value())
    last_record_id = await database.execute(query)
    # print(user.model_dump())
    logger.info(' create user - success')
    return {**user.model_dump(), "user_id": last_record_id}


@app.put("/users/{user_id}", response_model=UserWithID)
async def update_user(usr_id: int, new_user: User):
    """ Update the user in database"""

    query = users.update().where(users.c.user_id == usr_id).values(
        username=new_user.username,
        lastname=new_user.lastname,
        date_of_birth=new_user.date_of_birth,
        email=new_user.email,
        password=new_user.password.get_secret_value())
    await database.execute(query)
    logger.info(' update user - success')
    return {**new_user.model_dump(), "user_id": usr_id}


@app.delete("/users/{user_id}")
async def delete_user(usr_id: int):
    """ Delete the user from database"""
    query = users.delete().where(users.c.user_id == usr_id)
    await database.execute(query)
    logger.info(' delete user - success')
    return {'message': 'User deleted'}


# ------------ Products --------------------------------
@app.get("/products/", response_model=List[ProductWithID])
async def get_products():
    """ Returns a list of products from the database """

    query = products.select()
    logger.info(' отработал GET запрос на получение списка продуктов')
    return await database.fetch_all(query)


@app.get("/products/{product_id}", response_model=ProductWithID)
async def get_product_one(prod_id: int):
    """ Returns one of the products from the database """

    query = products.select().where(products.c.product_id == prod_id)
    logger.info(' get product - success')
    return await database.fetch_one(query)


@app.post("/products/", response_model=ProductWithID)
async def create_product(product: Product):
    """ Create a new product in database"""

    query = products.insert().values(
        name=product.name,
        description=product.description,
        price=product.price)
    last_record_id = await database.execute(query)
    logger.info(' create product - success')
    return {**product.model_dump(), "product_id": last_record_id}


@app.put("/products/{product_id}", response_model=ProductWithID)
async def update_product(prod_id: int, new_prod: Product):
    """ Update the product in database"""

    query = products.update().where(products.c.product_id == prod_id).values(**new_prod.model_dump())
    # query = users.update().where(users.c.user_id == usr_id).values(
    #     username=new_user.username, email=new_user.email,
    #     password=new_user.password.get_secret_value())
    await database.execute(query)
    logger.info(' update product - success')
    return {**new_prod.model_dump(), "product_id": prod_id}


@app.delete("/products/{product_id}")
async def delete_product(prod_id: int):
    """ Delete the product from database"""
    query = products.delete().where(products.c.product_id == prod_id)
    await database.execute(query)
    logger.info(' delete product - success')
    return {'message': f'product id={prod_id}: deleted'}


# ------------ Orders --------------------------------
@app.get("/orders/", response_model=List[OrderWithID])
async def get_orders():
    """ Returns a list of orders from the database """

    query = orders.select()
    logger.info(' отработал GET запрос на получение списка заказов')
    return await database.fetch_all(query)


@app.get("/orders/{order_id}", response_model=OrderWithID)
async def get_order_one(ord_id: int):
    """ Returns one of the orders from the database """

    query = orders.select().where(orders.c.order_id == ord_id)
    logger.info(' get order - success')
    return await database.fetch_one(query)


@app.post("/orders/", response_model=OrderWithID)
async def create_order(order: Order):
    """ Create a new order in database"""

    query = orders.insert().values(**order.model_dump())
    last_record_id = await database.execute(query)
    print(order.model_dump())
    logger.info(' create order - success')
    return {**order.model_dump(), "order_id": last_record_id}


@app.put("/orders/{order_id}", response_model=OrderWithID)
async def update_order(ord_id: int, new_ord: Order):
    """ Update the order in database"""

    query = orders.update().where(orders.c.order_id == ord_id).values(**new_ord.model_dump())
    # query = users.update().where(users.c.user_id == usr_id).values(
    #     username=new_user.username, email=new_user.email,
    #     password=new_user.password.get_secret_value())
    await database.execute(query)
    logger.info(' update order - success')
    return {**new_ord.model_dump(), "order_id": ord_id}


@app.delete("/orders/{order_id}")
async def delete_order(ord_id: int):
    """ Delete the order from database"""
    query = orders.delete().where(orders.c.order_id == ord_id)
    await database.execute(query)
    logger.info(' delete order - success')
    return {'message': f'order id={ord_id}: deleted'}


#
# create##########################################################
# @app.post("/users/", response_model=UserWithID)  # Создание пользователя в БД, create
# async def create_user(user: User):
#     """/////////////////// Create a new user in the database"""
#
#     query = users.insert().values(
#         username=user.username,
#         lastname=user.lastname,
#         date_of_birth=user.date_of_birth,
#         email=user.email,
#         password=user.password)
#     # password=user.password.get_secret_value())
#     last_record_id = await database.execute(query)
#     print(user.model_dump())
#     return {**user.model_dump(), "user_id": last_record_id}


#
# # @app.get("/items/")
# # async def read_item(skip: int = 0, limit: int = 10):
# #     return {"skip": skip, "limit": limit}
#

#
# @app.put("/users/{user_id}", response_model=UserWithID)  # Обновление пользователя в БД, update
# async def update_user(usr_id: int, new_user: User):
#     # query = users.update().where(users.c.user_id == usr_id).values(**new_user.model_dump())
#     query = users.update().where(users.c.user_id == usr_id).values(
#         username=new_user.username, email=new_user.email,
#         password=new_user.password.get_secret_value())
#     await database.execute(query)
#     return {**new_user.model_dump(), "user_id": usr_id}  # dict() заменили на model_dump()
#
#
# @app.delete("/users/{user_id}")  # Удаление пользователя из БД, delete
# async def delete_user(usr_id: int):
#     query = users.delete().where(users.c.user_id == usr_id)
#     await database.execute(query)
#     return {'message': 'User deleted'}
#

if __name__ == "__main__":
    uvicorn.run("hw6_task6_main:app", host="127.0.0.1", port=8000, reload=True)
