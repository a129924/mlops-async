from mlops_async.mlops_async_client import MlopsAsyncClient

__all__ = ["MlopsAsyncClient", "hello"]


def hello() -> str:
    return "Hello from mlops-async!"
