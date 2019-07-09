# main
import os
import time
import logging
import grpc
from grpc._cython import cygrpc
import importlib
import sys
from concurrent import futures
import hydro_serving_grpc as hs
from hydro_serving_grpc.tf.api import PredictionServiceServicer

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

# python runtime
class PythonRuntime:
    def __init__(self, func):
        self.port = None
        self.server = None
        self.func = func
        self.servicer = PythonRuntimeService(self.func)
        self.logger = logging.getLogger("python-runtime")

    def start(self, port=None, max_workers=10, max_message_size=256*1024*1024):
        
        if not port:
            port = os.getenv("APP_PORT")
            if port:
                logging.info("Using APP_PORT port {}".format(port))
            else:
                port = 9090
                logging.info("Using default port {}".format(port))
        else:
            logging.info("Using overriden port {}".format(port))

        logging.basicConfig(level=logging.INFO)

        options = [(cygrpc.ChannelArgKey.max_send_message_length, max_message_size),
                   (cygrpc.ChannelArgKey.max_receive_message_length, max_message_size)]
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers), options=options)
        hs.add_PredictionServiceServicer_to_server(self.servicer, self.server)
        addr = "[::]:{}".format(port)
        self.logger.info("Starting server on {}".format(addr))
        self.server.add_insecure_port(addr)
        self.server.start()
        try:
             while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            self.stop()

    def stop(self, code=0):
        self.logger.info("Shutting down")
        self.server.stop(code)
# end python runtime

# grpc impl
class PythonRuntimeService(PredictionServiceServicer):
    def __init__(self, func):
        self.logger = logging.getLogger("PythonRuntimeService")
        self.status_message = "Preparing to import entrypoint"
        self.error = None
        self.func = func
        try:
            self.signature = func._serving_signature
            self.status = "SERVING"
            self.status_message = "ok"
        except Exception as ex:
            logging.exception("Error during entrypoint import. Runtime is in invalid state.")
            self.error = ex
            self.status = "NOT_SERVING"
            self.status_message = "entrypoint reader error: {}".format(ex)

    def Predict(self, request, context):
        if self.error:
            context.abort(
                grpc.StatusCode.INTERNAL,
                "func_main is not imported due to error: {}".format(str(self.error))
            )
        else:
            self.logger.info("Received inference request: {}".format(request)[:256])
            try:
                result = self.func(**request.inputs)
                if not isinstance(result, hs.PredictResponse):
                    self.logger.warning("Type of a result ({}) is not `PredictResponse`".format(result))
                    context.set_code(grpc.StatusCode.OUT_OF_RANGE)
                    context.set_details("Type of a result ({}) is not `PredictResponse`".format(result))
                    return hs.PredictResponse()

                self.logger.info("Answer: {}".format(result)[:256])
                return result
            except Exception as ex:
                context.abort(grpc.StatusCode.INTERNAL, repr(ex))

    def Status(self, request, context):
        logging.info("STATUS REQUEST {} {}".format(self.status, self.status_message))
        return hs.tf.api.StatusResponse(
            status=self.status,
            message=self.status_message
        )
# end grpc impl