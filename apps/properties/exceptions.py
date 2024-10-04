from rest_framework.exceptions import APIException

# Ref : https://www.django-rest-framework.org/api-guide/exceptions/#custom-errors
class PropertyNotFound(APIException):
    status_code = 404
    default_detail = "The requested property does not exist."