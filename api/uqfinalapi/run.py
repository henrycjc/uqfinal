import os

from app import webapp

webapp.config.update({
    'SQLALCHEMY_DATABASE_URI': os.environ['UQFINAL_DB_URI'],
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_POOL_SIZE': 0,
    'SQLALCHEMY_POOL_RECYCLE': 500,
})


if __name__ == "__main__":
    webapp.run(port=8080)
