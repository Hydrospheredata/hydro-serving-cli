from pydantic import BaseModel
import importlib_metadata

class HSInfo(BaseModel):
    sdk_version: str
    cli_version: str
    protos_version: str

    def to_metadata(self):
        return {
            'hydrosphere.sdk.version': self.sdk_version,
            'hydrosphere.cli.version': self.cli_version,
            'hydrosphere.protos.version': self.protos_version
        }

    @staticmethod
    def collect() -> "HSInfo":
        return HSInfo(
            sdk_version = importlib_metadata.version("hydrosdk"),
            cli_version = importlib_metadata.version("hs"),
            protos_version = importlib_metadata.version("hydro_serving_grpc")
        )

