import requests

# the api key
MAILGUN_API_KEY = 'NOT_REAL'


# create mailing lists and seed users into them
def seed(identifier):
    raise NotImplementedError('Seeding not implemented!')


# get all the mailing lists the user belongs to
def access(identifier):
    raise NotImplementedError('Access not implemented!')


# remove the user from all mailing lists
def erasure(identifier, context):
    raise NotImplementedError('Erasure not implemented!')
