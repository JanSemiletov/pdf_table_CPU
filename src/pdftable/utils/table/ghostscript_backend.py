# -*- coding: utf-8 -*-

import sys
import os
import ctypes
import traceback
import subprocess
import glob
from ctypes.util import find_library

from ..cmd_utils import CmdUtils
from ..file_utils import FileUtils
from ..logger_utils import logger

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
        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs"
    ]
    dll_name = "".join(("gsdll", str(ctypes.sizeof(ctypes.c_void_p) * 8), ".dll"))

    for base_path in common_paths:
        if os.path.exists(base_path):
            dll_pattern = FileUtils.join_path(base_path, "**", dll_name)
            matches = glob.glob(dll_pattern, recursive=True)
            if matches:
                return True
            
    return False

def get_gs_command_windows():
    if ctypes.sizeof(ctypes.c_void_p) == 8:
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
            if not os.path.exists(pdf_path):
                logger.error(f"Input PDF does not exist: {pdf_path}")
                metric["error"] = f"Input PDF not found: {pdf_path}"
                return False, metric
            
            png_dir = os.path.dirname(png_path)
            if png_dir and not os.path.exists(png_dir):
                os.makedirs(png_dir, exist_ok=True)
                logger.info(f"Created output directory: {png_dir}")

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
            logger.info(f"Starting ghostscript: {' '.join(gs_command)}")

            result = subprocess.run(
                gs_command,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                if os.path.exists(png_path):
                    extract_success = True
                    logger.info(f"Ghostscript completed successfully. Output: {png_path}")
                else:
                    logger.error(f"Ghostscript returned success but output file not found: {png_path}")
                    logger.error(f"stdout: {result.stdout}")
                    logger.error(f"stderr: {result.stderr}")
            else:
                logger.error(f"Ghostscript failed with return code {result.returncode}")
                logger.error(f"stdout: {result.stdout}")
                logger.error(f"stderr: {result.stderr}")

            metric["cmd"] = " ".join(gs_command)
            metric["returncode"] = result.returncode
            metric["stdout"] = result.stdout
            metric["stderr"] = result.stderr

        except subprocess.TimeoutExpired:
            logger.error("Ghostscript command timed out after 5 minutes")
            metric["error"] = "Timeout after 300 seconds"
        except FileNotFoundError as e:
            logger.error(f"Ghostscript command '{gs_cmd}' not found. Make sure Ghostscript is installed and in PATH")
            metric["error"] = f"Ghostscript not found: {str(e)}"
        except Exception as e:
            logger.error(f"Ghostscript conversion failed: {e}")
            metric["error"] = str(e)
            traceback.print_exc()

        return extract_success, metric
