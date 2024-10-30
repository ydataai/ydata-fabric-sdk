"""
    In this file it can be found both the logic for the logger and decorator function
"""
import contextlib
import os
import platform
import subprocess

import logging

import pandas as pd
import requests

from ydata.sdk.datasources._models.datatype import DataSourceType

def is_running_in_databricks():
    mask = "DATABRICKS_RUNTIME_VERSION" in os.environ
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        return os.environ["DATABRICKS_RUNTIME_VERSION"]
    else:
        return str(mask)

def get_datasource_info(dataframe, datatype):
    """
        calculate required datasource info
    """
    if isinstance(dataframe, pd.DataFrame):
        connector = 'csv'
        nrows, ncols = dataframe.shape[0], dataframe.shape[1]  # calculate the number of rows and cols
    else:
        connector = dataframe.connector_type
        if DataSourceType(datatype) != DataSourceType.MULTITABLE:
            nrows = dataframe.metadata.number_of_rows
            ncols = len(dataframe.metadata.columns)
            ntables=1
        else:
            nrows = 0
            ncols = 0
            ntables=len(dataframe.tables.keys())
    return connector, nrows, ncols, ntables

def analytics_features(datatype: str, connector: str, nrows: int, ncols: int, ntables: int, method: str, dbx: str) -> None:
    """
        Returns metrics and analytics from ydata-sdk
    """
    endpoint = "https://packages.ydata.ai/ydata-sdk?"
    #package_version = __version__

    if (
        bool(os.getenv("YDATA_SDK_NO_ANALYTICS")) is not True
        #and package_version != "0.0.dev0"
    ):
        try:
            subprocess.check_output("nvidia-smi")
            gpu_present = True
        except Exception:
            gpu_present = False

        python_version = ".".join(platform.python_version().split(".")[:2])

        with contextlib.suppress(Exception):
            request_message = (
                f"{endpoint}python_version={python_version}"
                f"&datatype={datatype}"
                f"&connector={connector}"
                f"&ncols={ncols}"
                f"&nrows={nrows}"
                f"&ntables={ntables}"
                f"&method={method}"
                f"&os={platform.system()}"
                f"&gpu={str(gpu_present)}"
                f"&dbx={dbx}"
            )

            requests.get(request_message)

class SDKLogger(logging.Logger):
    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)

    def info(self, dataframe, datatype: str, method:str) -> None:  # noqa: ANN001

        dbx = is_running_in_databricks()

        connector, nrows, ncols, ntables = get_datasource_info(dataframe, datatype)

        analytics_features(
            datatype=datatype,
            method=method,
            connector=connector,
            nrows=nrows,
            ncols=ncols,
            ntables=ntables,
            dbx=dbx
        )

        super().info(
            f"[PROFILING] Calculating profile with the following characteristics "
            f"- {datatype} | {method} | {connector}."
        )
