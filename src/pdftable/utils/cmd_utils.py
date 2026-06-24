#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project ：PdfTable 
# @File    ：cmd_utils.py
# @Author  ：cycloneboy
# @Date    ：20xx/12/23 10:28
import subprocess
import traceback

from .base_utils import BaseUtil


class CmdUtils(BaseUtil):

    def init(self):
        pass

    @staticmethod
    def run_cmd(cmd, timeout=300):
    def run_cmd(cmd, timeout=300):
        """

        :param cmd:
        :return:
        """
        r = None
        try:
            if isinstance(cmd, str):
                p = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                p = subprocess.Popen(
                    cmd,
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            r, err = p.communicate(timeout=timeout)

            if p.returncode != 0 and err:
                print(f"Command stderr: {err.decode('utf-8', errors='ignore')}")

        except subprocess.TimeoutExpired:
            p.kill()
            print(f"Command timed out after {timeout} seconds")        
        except Exception as e:
            traceback.print_exc()

        return r
