# -*- coding: utf-8 -*-
#
# gdb-frontend is a easy, flexible and extensionable gui debugger
#
# https://github.com/rohanrhu/gdb-frontend
# https://oguzhaneroglu.com/projects/gdb-frontend/
#
# Licensed under GNU/GPLv3
# Copyright (C) 2019, Oğuzhan Eroğlu (https://oguzhaneroglu.com/) <rohanrhu2@gmail.com>

"""
GDBFrontend Process Management API
"""

import importlib
import json
import threading
import os
import os.path

import config
import settings
import util
import api.debug
import api.flags
import api.globalvars

gdb = importlib.import_module("gdb")

api.globalvars.init()

state = api.globalvars.collabration_state

lock = False

def init():
    global lock
    lock = threading.Lock()

    global state

def access(function):
    global lock
    global state

    lock.acquire()
    function()
    lock.release()

def getProcessDetails(pid):
    pid = str(pid)
    
    proc_status = open("/proc/" + pid + "/status", encoding="utf-8").read()
    cmdline = open("/proc/" + pid + "/cmdline", encoding="utf-8").read()

    status = {}
    
    for i in proc_status.split("\n"):
        kv = i.split("\t")

        if not kv or len(kv) < 2:
            continue
        
        status[kv[0][:-1].strip()] = kv[1].strip()
    
    return {
        "status": status,
        "cmdline": cmdline.replace("\x00", " "),
        "start_time": os.stat("/proc/" + pid).st_ctime
    }

def getAllProcesses():
    pids = {}

    for pid in os.listdir("/proc"):
        if pid.isnumeric() and os.path.isdir("/proc/" + pid):
            pid = int(pid)
            
            try:
                pids[pid] = getProcessDetails(pid)
            except Exception as e:
                util.verbose("[Error] Could not get process details (PID: %s)" % str(pid), e)
    
    return pids