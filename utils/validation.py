def validate_post_data(request_data, required_fields=None, model=None):
    if model is not None:
        required_fields = model.VALIDATION_FIELDS

    missing_fields = {}
    for field in required_fields:
        if field not in request_data:
            missing_fields[field] = f"{field} is required"

    return len(missing_fields) == 0, missing_fields
