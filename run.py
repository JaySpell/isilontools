#!/home/kcup/PycharmProjects/quota/bin/python
from app import app
from external import config, secret

app.run(host='0.0.0.0',debug=True)
