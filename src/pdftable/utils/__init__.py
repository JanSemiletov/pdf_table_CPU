#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project ：PdfTable 
# @File    ：__init__.py
# @Author  ：cycloneboy
# @Date    ：20xx/6/21 13:54

from .constant import Constants
from .base_utils import BaseUtil

def __getattr__(name):
    # lazy import submodules on attribute access
    if name == "logger":
        from .logger_utils import logger
        return logger
    elif name == "CmdUtils":
        from .cmd_utils import CmdUtils
        return CmdUtils
    elif name == "TimeUtils":
        from .time_utils import TimeUtils
        return TimeUtils
    elif name == "FileUtils":
        from .file_utils import FileUtils
        return FileUtils
    elif name == "RequestUtils":
        from .request_utils import RequestUtils
        return RequestUtils
    elif name == "MathUtils":
        from .math_utils import MathUtils
        return MathUtils
    elif name == "CommonUtils":
        from .common_utils import CommonUtils
        return CommonUtils
    elif name == "MatchUtils":
        from .match_utils import MatchUtils
        return MatchUtils
    elif name == "PdfUtils":
        from .pdf_utils import PdfUtils
        return PdfUtils
    elif name == "PdfTableExtractUtils":
        from .pdf_table_extract_utils import PdfTableExtractUtils
        return PdfTableExtractUtils
    elif name == "DeployUtils":
        from .deploy_utils import DeployUtils
        return DeployUtils
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")