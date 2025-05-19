import json
import threading
from datetime import datetime
from fastapi import HTTPException
from typing import List, Dict, Any

from fastapi import FastAPI
from VirtualMachine import VirtualMachine
from uuid import uuid4
from terraform import Terraform

@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hou
def cleanup_vms():
    global running_vms
    list_lock.acquire()
    for vm in running_vms:
        if vm.last_update + 1800 < datetime.now().timestamp():
            running_vms.remove(vm)

    tf.set_variables([vm.name for vm in running_vms])
    tf.apply()
    list_lock.release()


app = FastAPI()
tf: Terraform = Terraform()

running_vms: List[VirtualMachine] = []
list_lock = threading.Lock()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/create")
async def create() -> Dict[str, str]:
    token: str = str(uuid4())
    now: float = datetime.now().timestamp()

    list_lock.acquire()
    print("locked")
    running_vms.append(VirtualMachine(name=f"vm-{token}", token=token, last_update=now))


    tf.set_variables([vm.name for vm in running_vms])
    retry_count: int = 0

    while retry_count < 5:
        try:
            tf.apply()
            break
        except Exception as e:
            print(f"Error: {e}")
            retry_count += 1
    else:
        list_lock.release()
        raise HTTPException(status_code=500, detail="Failed to create VMs after 5 attempts")

    # Wait for the VMs to be created, because terraform says it is done, but Proxmox can still be creating the VMs
    # time.sleep(15)

    output: str = tf.output()
    print(output)

    # Parse output
    json_output: Dict[str, Any] = json.loads(output)
    new_ips = json_output["vm_ipv4_address"]["value"]
    print(new_ips)

    # Get newly created VM's ip
    ips = [vm.ip for vm in running_vms if vm.ip is not None]
    new_ip = list(filter(lambda ip: ip not in ips, new_ips))[0]

    # Get newly created VM, based on token
    newly_created_vm: filter = filter(lambda vm: vm.token == token, running_vms)
    new_vm = list(newly_created_vm)[0]
    new_vm.ip = new_ip
    list_lock.release()

    return {"token": token, "ip": new_ip}

@app.get("/update/{token}")
async def update(token: str):
    list_lock.acquire()
    for vm in running_vms:
        if vm.token == token:
            vm.last_update = datetime.now().timestamp()
            break
    list_lock.release()

@app.get("/delete/{token}")
async def delete(token: str):
    list_lock.acquire()
    for vm in running_vms:
        if vm.token == token:
            running_vms.remove(vm)
            break

    tf.set_variables([vm.name for vm in running_vms])
    tf.apply()
    list_lock.release()
