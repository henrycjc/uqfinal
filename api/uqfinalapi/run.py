from app import webapp
import boto3


# Create a connection to the offerings dynamodb table
# Connecting is slow, so only do it once
table = boto3.resource('dynamodb').Table("uqfinal-offerings")
table.load()  # Force some request so the connection is warm and benchmarking of requests is consistent

webapp.config.update({
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_POOL_SIZE': 0,
    'SQLALCHEMY_POOL_RECYCLE': 500,
    'UQFINAL_TABLE_OFFERINGS': table,
})


if __name__ == "__main__":
    webapp.run(port=8080)
