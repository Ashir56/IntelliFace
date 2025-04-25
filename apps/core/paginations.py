from rest_framework.response import Response


def paginated_queryset_response(queryset, request):
    params = request.query_params
    offset = int(params.get('offset', 0))
    limit = int(params.get('limit', 10))
    count = len(queryset)
    if count > 0:
        queryset = queryset[offset:offset + limit]
    return Response({"offset": offset,
                     "limit": limit,
                     "count": count,
                     "result": queryset})
