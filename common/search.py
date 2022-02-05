from django.contrib.postgres.search import SearchVector

from common.payload import create_error_payload, create_success_payload
from common.validation import validate_post_data


def search_table(model, search_fields, request):
    is_valid, request_data, debug_data = validate_post_data(request.body, ["query"])
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    results = model.objects.annotate(search=SearchVector(*search_fields)).filter(
        search=request_data["query"]
    )
    return create_success_payload([result.serialize() for result in results])
