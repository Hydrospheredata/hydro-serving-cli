from hydroserving.core.application.entities import streaming_params, ApplicationDef


def parse_streaming_params(in_list):
    """

    Args:
        in_list (list of dict):

    Returns:
        StreamingParams:
    """
    params = []
    for item in in_list:
        params.append(streaming_params(item["in-topic"], item["out-topic"]))
    return params


def parse_singular_app(in_dict):
    return {
        "stages": [
            {
                "modelVariants": [parse_singular(in_dict)]
            }
        ]
    }


def parse_singular(in_dict):
    return {
        'modelVersion': in_dict['model'],
        'weight': 100
    }


def parse_model_variant_list(in_list):
    services = [
        parse_model_variant(x)
        for x in in_list
    ]
    return services


def parse_model_variant(in_dict):
    return {
        'modelVersion': in_dict['model'],
        'weight': in_dict['weight']
    }


def parse_pipeline_stage(stage_dict):
    if len(stage_dict) == 1:
        parsed_variants = [parse_singular(stage_dict[0])]
    else:
        parsed_variants = parse_model_variant_list(stage_dict)
    return {"modelVariants": parsed_variants}


def parse_pipeline(in_list):
    pipeline_stages = []
    for i, stage in enumerate(in_list):
        pipeline_stages.append(parse_pipeline_stage(stage))
    return {'stages': pipeline_stages}


def parse_application(in_dict):
    singular_def = in_dict.get("singular")
    pipeline_def = in_dict.get("pipeline")

    streaming_def = in_dict.get('streaming')
    if streaming_def:
        streaming_def = parse_streaming_params(streaming_def)

    if singular_def and pipeline_def:
        raise ValueError("Both singular and pipeline definitions are provided")

    if singular_def:
        execution_graph = parse_singular_app(singular_def)
    elif pipeline_def:
        execution_graph = parse_pipeline(pipeline_def)
    else:
        raise ValueError("Neither model nor graph are defined")

    return ApplicationDef(
        name=in_dict['name'],
        execution_graph=execution_graph,
        kafka_streaming=streaming_def
    )
