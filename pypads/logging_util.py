import os
import pickle
from enum import Enum
from logging import warning
from os.path import expanduser

import mlflow
from mlflow.utils.autologging_utils import try_mlflow_log


def to_folder(file_name):
    """
    TODO
    :param file_name:
    :return:
    """
    return os.path.join(expanduser("~") + "/.pypads/" + mlflow.active_run().info.experiment_id + "/" + file_name)


class WriteFormats(Enum):
    pickle = 1
    text = 2


def try_write_artifact(file_name, obj, write_format):
    """
    Function to write an artifact to disk. TODO
    :param write_format:
    :param file_name:
    :param obj:
    :return:
    """
    path = to_folder(file_name)

    # Todo allow for configuring output format
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # Functions for the options to write to
    def write_text(p, o):
        with open(p + ".txt", "w+") as fd:
            fd.write(str(o))
            return fd.name

    def write_pickle(p, o):
        try:
            with open(p + ".pickle", "wb+") as fd:
                pickle.dump(o, fd)
                return fd.name
        except Exception as e:
            warning("Couldn't pickle output. Trying to save toString instead. " + str(e))
            return write_text(p, o)

    # Options to write to
    options = {
        WriteFormats.pickle: write_pickle,
        WriteFormats.text: write_text
    }

    # Write to disk
    if isinstance(write_format, str):
        if WriteFormats[write_format]:
            write_format = WriteFormats[write_format]
        else:
            warning("Configured write format " + write_format + " not supported! ")
            return

    path = options[write_format](path, obj)

    # Log artifact to mlflow
    try_mlflow_log(mlflow.log_artifact, path)