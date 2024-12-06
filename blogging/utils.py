from rest_framework.response import Response


# Helper for return response
def get_response(code_status, msg, payload):
    return Response( {'code': code_status, 'msg': msg, 'data': payload }, status=code_status)
