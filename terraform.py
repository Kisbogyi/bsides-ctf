import subprocess
import os
from subprocess import CompletedProcess
from typing import List


class Terraform:
    terraform_folder: str
    tfvars_path: str

    def __init__(self, terraform_folder: str = "terraform", tfvars_path: str = "vm_names.tfvars"):
        self.terraform_folder = terraform_folder
        self.tfvars_path = tfvars_path

        current_directory: str = os.getcwd()

        # Initialize Terraform
        os.chdir(self.terraform_folder)
        subprocess.run(["terraform", "init"], check=True)

        # Change back to the original directory
        os.chdir(current_directory)

    def apply(self):

        current_directory: str = os.getcwd()

        # Change to the terraform folder
        os.chdir(self.terraform_folder)

        # Apply the configuration
        # tfvars_path should not come from user input!
        try:
            subprocess.run(["terraform", "apply", "-auto-approve", f"-var-file={self.tfvars_path}"], check=True)
        finally:
            # Change back to the original directory
            os.chdir(current_directory)


    def output(self) -> str:
        current_directory: str = os.getcwd()

        os.chdir(self.terraform_folder)

        result: CompletedProcess[str] = subprocess.run(["terraform", "output", "-json"], check=True, capture_output=True, text=True)

        os.chdir(current_directory)

        return result.stdout

    def set_variables(self, vm_names: List[str]):
        current_directory: str = os.getcwd()

        # Change to the terraform folder
        os.chdir(self.terraform_folder)

        # Set the variables
        names = [f'\"{name}\"' for name in vm_names]
        formatted_vm_names: str = ", ".join(names)

        # Set the variables
        with open(self.tfvars_path, "w") as tfvars_file:
            tfvars_file.write(f"vm_names = [{formatted_vm_names}]\n")

        # Change back to the original directory
        os.chdir(current_directory)
