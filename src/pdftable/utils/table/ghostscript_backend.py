# -*- coding: utf-8 -*-

import sys
import os
import ctypes
import traceback
import subprocess
import glob
from ctypes.util import find_library

from ...utils import CmdUtils
from ...utils import logger

__all__ = [
    "GhostscriptBackend",
]


def installed_posix():
    library = find_library("gs")
    if library is not None:
        return True
    
    try:
        result = subprocess.run(["gs", "--version"],
                                capture_output=True,
                                timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def installed_windows():
    library = find_library(
        "".join(("gsdll", str(ctypes.sizeof(ctypes.c_voidp) * 8), ".dll"))
    )
    if library is not None:
        return True
    
    gs_exe = get_gs_command_windows()
    try:
        result = subprocess.run([gs_exe, "--version"],
                                capture_output=True,
                                timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    common_paths = [
        r"C\Program Files\gs",
        r"C\Program Files (x86)\gs"
    ]
    dll_name = "".join(("gsdll", str(ctypes.sizeof(ctypes.c_void_p) * 8), ".dll"))

    for base_path in common_paths:
        if os.path.exists(base_path):
            dll_pattern = os.path.join(base_path, "**", dll_name)
            matches = glob.glob(dll_pattern, recursive=True)
            if matches:
                return True
            
    return False

def get_gs_command_windows():
    if ctypes.sizeof(ctypes.c_void_p) == 0:
        return "gswin64c.exe"
    else:
        return "gswin32c.exe"

def get_gs_command():
    if sys.platform == "win32":
        return get_gs_command_windows()
    else:
        return "gs"

class GhostscriptBackend(object):
    def installed(self):
        if sys.platform in ["linux", "darwin"]:
            return installed_posix()
        elif sys.platform == "win32":
            return installed_windows()
        else:
            return installed_posix()

    def convert_v0(self, pdf_path, png_path, resolution=300):
        if not self.installed():
            raise OSError(
                "Ghostscript is not installed. You can install it using the instructions"
                " here: https://camelot-py.readthedocs.io/en/master/user/install-deps.html"
            )

        import ghostscript

        gs_cmd = get_gs_command()
        gs_command = [
            gs_cmd,
            "-q",
            "-sDEVICE=png16m",
            "-o",
            png_path,
            f"-r{resolution}",
            pdf_path,
        ]
        print(f"ghostscript : {' '.join(gs_command)}")
        ghostscript.Ghostscript(*gs_command)

    def convert(self, pdf_path, png_path, resolution=300):
        """
        Convert PDF to PNG using Ghostscript
        
        :param pdf_path:
        :param png_path:
        :param resolution:
        :return: (success: bool, metric: dict)
        """
        if not self.installed():
            raise OSError(
                "Ghostscript is not installed. You can install it using the instructions"
                " here: https://camelot-py.readthedocs.io/en/master/user/install-deps.html"
            )

        extract_success = False
        metric = {}
        try:
            gs_cmd = get_gs_command()
            gs_command = [
                gs_cmd,
                "-q",
                "-sDEVICE=png16m",
                "-o",
                png_path,
                f"-r{resolution}",
                pdf_path,
            ]
            logger.info(f"Starting ghostscript:{" ".join(gs_command)}")

            result = subprocess.run(
                gs_command,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                extract_success = True
                logger.info("Ghostscript completed successfully")
            else:
                logger.error(f"Ghostscript failed with return code {result.returncode}")
                logger.error(f"stderr: {result.stderr}")

            metric["cmd"] = " ".join(gs_command)
            metric["returncode"] = result.returncode

        except subprocess.TimeoutExpired:
            logger.error("Ghostscript command timed out after 5 minutes")
        except FileNotFoundError:
            logger.error(f"Ghostscript comman '{gs_command}' not found. Make sure Ghostscript is installed and in PATH")
        except Exception as e:
            logger.error(f"Ghostscript conversion failed: {e}")

        return extract_success, metric
