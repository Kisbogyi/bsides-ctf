# TODO: Create youtrack article

variable "vm_count" {
    type = number 
        default = 1
}

variable "vm_names" {
    type = list(string)
    default = []
}

terraform {
    required_providers {
        proxmox = {
            source = "bpg/proxmox"
                version = "0.70.0"
        }
    }
}


provider "proxmox" {
    endpoint  = "https://10.97.42.42:8006/"
        api_token = "terraform api token"
        username = "terraform@pam"
        insecure  = true

        ssh {
            //use `ssh-add` to add key to ssh agent so tf can use it
            agent    = true
            username = "terraform"
        }
}

resource "proxmox_virtual_environment_vm" "ubuntu_clone" {
    for_each = toset(var.vm_names)
    name      = each.key
    node_name = "securiteam-node3"

    agent {
        enabled = true
        trim = true
        timeout = "5m"
    }

    clone {
        vm_id = 106
        full = false
    }

    network_device {
        bridge = "vmbr4"
    }


    memory {
        dedicated = 8192
    }

}

output "vm_ipv4_address" {
    # value = proxmox_virtual_environment_vm.ubuntu_clone[each.key].ipv4_addresses[1][0]
    value =  [for vm in proxmox_virtual_environment_vm.ubuntu_clone : vm.ipv4_addresses[1][0]]
}
