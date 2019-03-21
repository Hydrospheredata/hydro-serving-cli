"""
Functions for handling async/sync upload logic.
"""
import logging
import time

from hydroserving.core.contract import contract_to_dict
from hydroserving.core.model.entities import UploadMetadata, VersionStatus
from hydroserving.core.monitoring.service import DataProfileStatus
from hydroserving.util.fileutil import read_in_chunks


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
                time.sleep(10)  # wait until it's finished
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


def await_training_data(monitoring_api, mv_id):
    while True:
        status = monitoring_api.get_data_processing_status(mv_id)
        if status == DataProfileStatus.Failure:
            raise ValueError("Data profile for modelversion {} failed".format(mv_id))
        elif status == DataProfileStatus.Success:
            return status
        elif status == DataProfileStatus.NotRegistered:
            raise ValueError("There is no data profile for model version {}".format(mv_id))
        elif status == DataProfileStatus.Processing:
            time.sleep(30)
            continue
        else:
            raise ValueError("Unknown data profile status for model version {}: {}".format(mv_id, status))


def push_training_data_async(monitoring_api, model_version_id, data_file):
    monitoring_api.start_data_processing(model_version_id, data_file)
    logging.info("Data profile computing is started")
    return model_version_id


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
        install_command=model.install_command,
        metadata=model.metadata,
    )

    result = model_api.upload(tar, metadata)
    return result


def upload_model(model_service, monitoring_service, model, model_path,
                 is_async, ignore_training_data, ignore_monitoring):
    mv = upload_model_async(model_service, model, model_path)

    is_monitorable = not ignore_monitoring and model.monitoring
    if is_monitorable:
        logging.info("Monitoring config is here. Preparing config for monitoring service.")
        monitoring_params = model.monitoring
        for param in monitoring_params:
            param["modelVersionId"] = mv["id"]
            logging.info("Creating monitoring %s", param)
            result = monitoring_service.create_metric_spec(param)
            logging.debug("Monitoring service output: %s", result)

    is_pushable = model.training_data_file and not ignore_training_data
    if is_pushable:
        logging.info("Training data is here. Preparing push to the profiler service.")
        model_version = mv['id']
        try:
            with open(model.training_data_file, "rb") as f:
                push_uid = push_training_data_async(
                    monitoring_service,
                    model_version,
                    f
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
