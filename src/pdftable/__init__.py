#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project ：PdfTable 
# @File    ：__init__.py
# @Author  ：cycloneboy
# @Date    ：20xx/6/21 13:50

def __getattr__(name):
    # lazy import submodules on attribute access
    if name == "entity":
        from . import entity
        return entity
    elif name == "utils":
        from . import utils
        return utils
    elif name == "model":
        from . import model
        return model
    elif name == "process":
        from . import process
        return process
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
