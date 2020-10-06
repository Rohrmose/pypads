import os
from abc import abstractmethod
from typing import List, Union

from mlflow.entities import ViewType
from mlflow.tracking.fluent import SEARCH_MAX_RESULTS_PANDAS

from pypads.model.logger_output import FileInfo
from pypads.model.models import IdBasedEntry, ResultType
from pypads.utils.logging_util import get_temp_folder, read_artifact


class BackendInterface:

    def __init__(self, uri, pypads):
        self._uri = uri
        self._pypads = pypads

    @property
    def uri(self):
        return self._uri

    @property
    def pypads(self):
        return self._pypads

    @abstractmethod
    def log_artifact(self, meta, local_path) -> str:
        """
        Logs an artifact from disk.
        :param meta: ArtifactTracking object holding meta information
        :param local_path: Path from which to take the artifact
        :return: Returns a relative path to the artifact including name and file extension.
        """
        raise NotImplementedError("")

    def log(self, obj: IdBasedEntry):
        """
        Log some entry to backend.
        :param obj: Entry object to be logged
        :param payload: Payload if an memory artifact is to be stored.
        :return:
        """
        raise NotImplementedError("")

    def get(self, run_id, uid, storage_type: Union[ResultType, str]):
        """
        Get an entry.
        :param run_id: Run to get the object from
        :param uid: Uid or path for getting
        :param storage_type: Type of the entity
        :return:
        """
        raise NotImplementedError("")

    @abstractmethod
    def set_experiment_tag(self, experiment_id, key, value):
        raise NotImplementedError("")

    @abstractmethod
    def get_metric_history(self, run_id, key):
        raise NotImplementedError("")

    @abstractmethod
    def list_experiments(self, view_type):
        raise NotImplementedError("")

    @abstractmethod
    def list_run_infos(self, experiment_id, run_view_type=None):
        raise NotImplementedError("")

    @abstractmethod
    def get_run(self, run_id):
        raise NotImplementedError("")

    @abstractmethod
    def get_experiment(self, experiment_id):
        raise NotImplementedError("")

    @abstractmethod
    def get_experiment_by_name(self, name):
        raise NotImplementedError("")

    @abstractmethod
    def delete_experiment(self, experiment_id):
        raise NotImplementedError("")

    @abstractmethod
    def search_runs(self, experiment_ids, filter_string="", run_view_type=ViewType.ACTIVE_ONLY,
                    max_results=SEARCH_MAX_RESULTS_PANDAS, order_by=None):
        raise NotImplementedError("")

    @abstractmethod
    def create_run(self, experiment_id, start_time=None, tags=None):
        raise NotImplementedError("")

    @abstractmethod
    def create_experiment(self, name, artifact_location=None):
        """Create an experiment.

        :param name: The experiment name. Must be unique.
        :param artifact_location: The location to store run artifacts.
                                  If not provided, the server picks an appropriate default.
        :return: Integer ID of the created experiment.
        """
        raise NotImplementedError("")

    @abstractmethod
    def delete_run(self, run_id):
        """
        Deletes a run with the given ID.
        """
        raise NotImplementedError("")

    @abstractmethod
    def download_artifacts(self, run_id, relative_path, dst_path=None):
        """
        Downloads the artifacts at relative_path to given destination folder.
        :param dst_path:
        :param run_id:
        :param relative_path:
        :return:
        """
        raise NotImplementedError("")

    def load_artifact_data(self, run_id, path):
        return read_artifact(self.download_tmp_artifacts(run_id, path))

    def download_tmp_artifacts(self, run_id, relative_path):
        """
        Downloads the artifact at relative_path to a local temporary folder.
        :param run_id:
        :param relative_path:
        :return:
        """
        local_path = get_temp_folder(self.get_run(run_id))
        if not os.path.exists(os.path.dirname(local_path)):
            os.makedirs(os.path.dirname(local_path))
        return self.download_artifacts(run_id=run_id, relative_path=relative_path, dst_path=local_path)

    @abstractmethod
    def list_files(self, run_id, path=None) -> List[FileInfo]:
        """
        This lists all available artifact files.
        :param run_id:
        :param path:
        :return:
        """
        raise NotImplementedError("")

    # def list_non_meta_files(self, run_id, path=None) -> List[FileInfo]:
    #     """
    #     This lists only artifacts which are not metadata files.
    #     :param run_id:
    #     :param path:
    #     :return:
    #     """
    #     return [a for a in self.list_files(run_id, path=path) if
    #             not str(a.path).endswith("meta." + FileFormats.json.value)]
    #
    # def list_artifacts(self, run_id, path=None) -> List[ArtifactInfo]:
    #     """
    #     This lists artifacts including their meta information.
    #     :param run_id:
    #     :param path:
    #     :return:
    #     """
    #     artifacts = self.list_non_meta_files(run_id, path=path)
    #     return [ArtifactInfo.construct(file_size=a.file_size,
    #                                    meta=self.get_artifact_meta(run_id=run_id, relative_path=a.path))
    #             for a in artifacts if not a.is_dir]

    def list(self, storage_type: Union[str, ResultType], experiment_name=None, experiment_id=None, run_id=None):
        raise NotImplementedError("The used backend doesn't support this form of querying.")

    @abstractmethod
    def get_artifact_uri(self, artifact_path=None):
        """
        Get the absolute URI of the specified artifact in the currently active run.
        If `path` is not specified, the artifact root URI of the currently active
        run will be returned.

        :param artifact_path: The run-relative artifact path for which to obtain an absolute URI.
                              For example, "path/to/artifact". If unspecified, the artifact root URI
                              for the currently active run will be returned.
        :return: An *absolute* URI referring to the specified artifact or the currently active run's
                 artifact root. For example, if an artifact path is provided and the currently active
                 run uses an S3-backed store, this may be a uri of the form
                 ``s3://<bucket_name>/path/to/artifact/root/path/to/artifact``. If an artifact path
                 is not provided and the currently active run uses an S3-backed store, this may be a
                 URI of the form ``s3://<bucket_name>/path/to/artifact/root``.
        """
        raise NotImplementedError("")
