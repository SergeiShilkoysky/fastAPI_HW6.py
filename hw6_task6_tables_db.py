import databases
import sqlalchemy

DATABASE_URL = "sqlite:///hw6.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

"""
Таблица пользователи - содержит следующие поля: id (PRIMARY KEY),
имя, фамилия, адрес электронной почты и пароль.
"""
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("user_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(32)),
    sqlalchemy.Column("lastname", sqlalchemy.String(32)),
    # sqlalchemy.Column("date_of_birth", sqlalchemy.String(32)),
    sqlalchemy.Column("date_of_birth", sqlalchemy.Date),
    # sqlalchemy.Column("address", sqlalchemy.String(128)),
    # sqlalchemy.Column("phone", sqlalchemy.String(128)),
    sqlalchemy.Column("email", sqlalchemy.String(80)),
    sqlalchemy.Column("password", sqlalchemy.String(32)),
)

"""
Таблица товары содержит следующие поля: id (PRIMARY KEY),
название, описание и цена.
"""
products = sqlalchemy.Table(
    "products",
    metadata,
    sqlalchemy.Column("product_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(128), nullable=False),
    # sqlalchemy.Column("date_of_production", sqlalchemy.String(16)),
    sqlalchemy.Column("description", sqlalchemy.String(200)),
    sqlalchemy.Column("price", sqlalchemy.Float, nullable=False),
)

"""
Таблица заказы содержит следующие поля: id (PRIMARY KEY), id
пользователя (FOREIGN KEY), id товара (FOREIGN KEY), дата заказа и статус заказа.
"""
orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("order_id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey('users.user_id')),
    sqlalchemy.Column("product_id", sqlalchemy.ForeignKey('products.product_id')),
    # sqlalchemy.Column("date_of_order", sqlalchemy.String(16), nullable=False),
    sqlalchemy.Column("date_of_order", sqlalchemy.Date, nullable=False),
    sqlalchemy.Column("order_status", sqlalchemy.String(30), nullable=False)
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)
