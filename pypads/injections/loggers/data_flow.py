import os
from typing import List

from pydantic import BaseModel

from pypads.app.injections.base_logger import LoggingFunction, LoggerCall, LoggerTrackingObject
from pypads.model.models import ArtifactMetaModel, LoggerCallModel
from pypads.utils.logging_util import WriteFormats


# TODO Literal for python 3.7 / 3.8?
class InputTO(LoggerTrackingObject):
    """
    Tracking object class for inputs of your tracked workflow.
    """

    class InputModel(BaseModel):
        class ParamModel(BaseModel):
            content_format: WriteFormats = WriteFormats.pickle
            name: str = ...
            value: str = ...  # path to the artifact containing the param
            type: str = ...

            class Config:
                orm_mode = True
                arbitrary_types_allowed = True

        input: List[ParamModel] = []
        call: LoggerCallModel = ...

        class Config:
            orm_mode = True

    def __init__(self, *args, call: LoggerCall, **kwargs):
        super().__init__(*args, model_cls=self.InputModel, call=call, **kwargs)

    def add_arg(self, name, value, format):
        self._add_param(name, value, format, 0)

    def add_kwarg(self, name, value, format):
        self._add_param(name, value, format, "kwarg")

    def _add_param(self, name, value, format, type):
        # TODO try to extract parameter documentation?
        index = len(self.input)
        path = os.path.join(self._base_path(), self._get_artifact_path(name))
        self.input.append(self.InputModel.ParamModel(content_format=format, name=name, value=path, type=type))
        self._store_artifact(value, ArtifactMetaModel(path=path,
                                                      description="Input to function with index {} and type {}".format(
                                                          index, type),
                                                      format=format))

    def _get_artifact_path(self, name):
        return os.path.join(self.call.call.to_folder(), "input", name)


class Input(LoggingFunction):
    """
    Function logging the input parameters of the current pipeline object function call.
    """

    name = "InputLogger"
    url = "https://www.padre-lab.eu/onto/input-logger"

    def tracking_object_schemata(self):
        return [InputTO.InputModel.schema()]

    def __pre__(self, ctx, *args, _pypads_write_format=None, _logger_call: LoggerCall, _args, _kwargs, **kwargs):
        """
        :param ctx:
        :param args:
        :param _pypads_write_format:
        :param kwargs:
        :return:
        """

        inputs = InputTO(call=_logger_call)
        for i in range(len(_args)):
            arg = _args[i]
            inputs.add_arg(str(i), arg, format=_pypads_write_format)

        for (k, v) in _kwargs.items():
            inputs.add_kwarg(str(k), v, format=_pypads_write_format)


class OutputTO(LoggerTrackingObject):
    """
    Tracking object class for inputs of your tracked workflow.
    """

    def _path_name(self):
        return "inputs"

    class OutputModel(BaseModel):
        content_format: WriteFormats = WriteFormats.pickle
        output: str = ...  # Path to the output holding file
        call: LoggerCallModel = ...

        class Config:
            orm_mode = True
            arbitrary_types_allowed = True

    def __init__(self, value, format, *args, call: LoggerCall, **kwargs):
        super().__init__(*args, model_cls=self.OutputModel, output="", content_format=format, call=call, **kwargs)
        path = os.path.join(self._base_path(), self.call.call.to_folder(), "output")
        self.output = path
        self._store_artifact(value, ArtifactMetaModel(path=path,
                                                      description="Output of function call {}".format(self.call.call),
                                                      format=format))


class Output(LoggingFunction):
    """
    Function logging the output of the current pipeline object function call.
    """

    def tracking_object_schemata(self):
        return [OutputTO.OutputModel.schema()]

    name = "OutputLogger"
    url = "https://www.padre-lab.eu/onto/output-logger"

    def __post__(self, ctx, *args, _pypads_write_format=WriteFormats.pickle, _logger_call, _pypads_result, **kwargs):
        """
        :param ctx:
        :param args:
        :param _pypads_write_format:
        :param kwargs:
        :return:
        """
        OutputTO(_pypads_result, _pypads_write_format, call=_logger_call)
