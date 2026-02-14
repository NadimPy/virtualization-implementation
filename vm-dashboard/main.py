""" # main.py
This main.py backend file connects the frontend to libvirt.
It creates:
  - VM instances
  - Lists VMs and shows specific information of a VM (stored in a sqlite database)
  - Executes set action on a VM (actions set in a db table with the command name and the execution logic)
  - Delete a VM
"""
## fastapi related imports
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import staticfiles
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader

## Simple imports
from pydantic import BaseModel
import random, time, asyncio, sys, uuid
from typing import Dict, List, Annotated
## Access to a simple sqlite database that holds all information about a VM
import sqlite3

#---

## client starters
### Fast API client
app = FastAPI()
### Libvirt client
conn = libvirt.open('qemu:///system')
### sqlite3 connection to db
with sqlite3.connect('vms.db') as connection:
    cursor = connection.cursor()

#---

# FastAPI Endpoints
app.post("/vms")
async def create_vm(vm: VMCreate):
    try:
        print("hello")
    except:
        pass
    return None

app.get("/vms")
async def list_all_vms():
    return {"List":{"vm1":"data","vm2":"data"}}

### Endpoint to get all data on an identified Vm
app.get("/vms/{id}")
async def get_vm_data():
    try:
        return{}
    except:
        return {}

app.post("/vms/{id}/action")
async def vm_action(id, action):
    try:
        return{}
    except:
        return{}

app.delete("/vms/{id}")
async def del_vm(id):
    try:
        return{"VM deleted"}
    except:
        return{"Vm deleted unsuccessfully, please try again *eyeroll*"}