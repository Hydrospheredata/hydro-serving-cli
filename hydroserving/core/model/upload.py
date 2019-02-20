"""
Functions for handling async/sync upload logic.
"""
import logging
import time

from hydroserving.core.contract import contract_to_dict
from hydroserving.core.model.entities import UploadMetadata, VersionStatus


class ModelBuildError(RuntimeError):
    def __init__(self, model_version):
        self.model_version = model_version
        super().__init__(model_version)


def await_upload(model_api, model_version):
    while True:
        name = model_version["model"]["name"]
        version = model_version["modelVersion"]
        model_version = model_api.find_version(name, version)
        str_status = model_version['status']
        try:
            status = VersionStatus[str_status]
            if status is VersionStatus.Assembling:
                time.sleep(5)  # wait until it's finished
                continue
            elif status is VersionStatus.Released:
                return model_version
            elif status is VersionStatus.Failed:
                raise ModelBuildError(model_version)
            else:
                raise ValueError("Unknown status '{}' for model {}:{}".format(str_status, name, version))
        except KeyError:
            raise ValueError("Unknown status '{}' for model {}:{}".format(str_status, name, version))

    # end of loop

def await_training_data(profile_api, uid):
    status = ""
    while status != "success":
        status = profile_api.status(uid)
        time.sleep(30)
    return uid


def push_training_data_async(profile_api, model_version_id, filename):
    logging.info("Uploading training data")
    uid = profile_api.push(model_version_id, filename)
    logging.info("Data profile computing is started with id %s", uid)
    return uid


def push_training_data(profile_api, model_version_id, filename, is_async):
    uid = push_training_data_async(profile_api, model_version_id, filename)

    if is_async:
        return uid
    return await_training_data(profile_api, uid)


def upload_model_async(model_api, model, tar):
    """

    Args:
        tar (str):
        model_api (ModelAPI):
        model (Model):

    Returns:
        dict:
    """
    logger = logging.getLogger()
    logger.debug("Uploading model to %s", model_api.connection.remote_addr)

    metadata = UploadMetadata(
        name=model.name,
        host_selector=model.host_selector,
        contract=contract_to_dict(model.contract),
        runtime=model.runtime.__dict__,
        install_command=model.install_command
    )

    result = model_api.upload(tar, metadata)
    return result


def upload_model(model_service, profiler_service, monitoring_service, model, model_path, is_async, no_training_data, ignore_monitoring):
    mv = upload_model_async(model_service, model, model_path)

    is_monitorable = not ignore_monitoring and model.monitoring
    if is_monitorable:
        logging.info("Monitoring config is here. Preparing config for monitoring service.")
        monitoring_params = model.monitoring
        for param in monitoring_params:
            param["modelVersionId"] = mv["id"]
        logging.debug("Creating monitoring %s", monitoring_params)
        monitoring_service.create(monitoring_params)

    is_pushable = model.training_data_file and not no_training_data
    if is_pushable:
        logging.info("Training data is here. Preparing push to the profiler service.")
        model_version = mv['id']
        try:
            push_uid = push_training_data_async(
                profiler_service,
                model_version,
                model.training_data_file
            )
            logging.info("Training data push id: %s", push_uid)
        except RuntimeError as ex:
            logging.error(ex)
            logging.error("Training data upload failed. Please use `hs profile push` command to try again.")

    if is_async:
        return mv

    logging.info("Waiting for a model build to complete...")
    build_status = await_upload(model_service, mv)

    return build_status

    # def check_monitoring_deps(self, app):
    #     """
    #
    #     Args:
    #         app (Application):
    #     """
    #     stages = app.execution_graph.as_pipeline().stages
    #     id_mapper_mon = {}
    #     for stage in stages:
    #         for mon in stage.monitoring:
    #             mon_type_res = METRIC_SPECIFICATION_KINDS.get(mon.type)
    #             if mon_type_res is None:
    #                 raise ValueError("Can't find metric provider for : {}".format(mon.__dict__))
    #             if mon.app is None:
    #                 if mon_type_res in PARAMETRIC_PROVIDERS:
    #                     raise ValueError("Application (app) is required for metric {}".format(mon.__dict__))
    #             else:
    #                 if mon.app not in id_mapper_mon:  # check for appName -> appId
    #                     mon_app_result = self.find(mon.app)
    #                     logging.debug("MONAPPSEARCH")
    #                     logging.debug(mon.__dict__)
    #                     logging.debug(mon_app_result)
    #                     if mon_app_result is None:
    #                         raise ValueError("Can't find metric application for {}".format(mon.__dict__))
    #                     id_mapper_mon[mon.app] = mon_app_result['id']
    #
    #     return id_mapper_mon

    # def configure_monitoring(self, app_id, app, id_mapper_mon):
    #     """
    #
    #     Args:
    #         id_mapper_mon (dict):
    #         app (Application):
    #         app_id (int):
    #     """
    #     pipeline = app.execution_graph.as_pipeline()
    #     results = []
    #     for idx, stage in enumerate(pipeline.stages):
    #         for mon in stage.monitoring:
    #             spec = MetricProviderSpecification(
    #                 metric_provider_class=METRIC_SPECIFICATION_KINDS[mon.type],
    #                 config=None,
    #                 with_health=mon.healthcheck_on,
    #                 health_config=None
    #             )
    #             if mon.app is not None:
    #                 spec.config = MetricConfigSpecification(id_mapper_mon[mon.app])
    #             if mon.threshold is not None:
    #                 spec.healthConfig = HealthConfigSpecification(mon.threshold)
    #
    #             aggregation = EntryAggregationSpecification(
    #                 name=mon.name,
    #                 metric_provider_specification=spec,
    #                 filter=FilterSpecification(
    #                     source_name=mon.input,
    #                     stage_id="app{}stage{}".format(app_id, idx)
    #                 )
    #             )
    #             results.append(self.monitoring_service.create_aggregation(aggregation))
    #     return results
