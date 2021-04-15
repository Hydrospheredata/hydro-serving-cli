from typing import List
from hydrosdk.modelversion import ModelVersion


def filter_internal_model_versions(mvs: List[ModelVersion]) -> List[ModelVersion]:
    return [mv for mv in mvs if not mv.metadata.get('is_metric', False)]