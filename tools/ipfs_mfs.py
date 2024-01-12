import requests
import json

class IpfsMfsTools:
    def __init__(self,api_url="http://127.0.0.1:5001/api/v0"):
        self.api_url = api_url

    def create_directory(self, directory_path):
        response = requests.post(f"{self.api_url}/files/mkdir?arg={directory_path}")
        return response.json()

    def add_file_to_directory(self, file_cid, directory_path, filename, overwrite=False):
        response = requests.post(f"{self.api_url}/files/cp?arg=/ipfs/{file_cid}&arg={directory_path}/{filename}")
        if response.status_code != 200:
            if "directory already has entry by that name" in response.json().get("Message"):
                print(f"File {filename} already exists in {directory_path} directory in IPFS")
                if overwrite:
                    print(f"Overwriting {filename} in {directory_path} directory in IPFS")
                    response = requests.post(f"{self.api_url}/files/rm?arg={directory_path}/{filename}&force=false", data=file_cid)
                    response = requests.post(f"{self.api_url}/files/cp?arg=/ipfs/{file_cid}&arg={directory_path}/{filename}")
                    return response.json()
                else:
                    return response.json()
        else:
            return {"Message": "File added successfully"}
    def list_directory(self, directory_path):
        response = requests.post(f"{self.api_url}/files/ls?arg={directory_path}")
        return response.json()

    def read_file(self, file_path):
        response = requests.post(f"{self.api_url}/files/read?arg={file_path}")
        return response.content

    def delete_file_or_directory(self, path, recursive=False):
        rec_flag = '&recursive=true' if recursive else ''
        response = requests.post(f"{self.api_url}/files/rm?arg={path}{rec_flag}")
        return response.json()

    def move_or_rename(self, src_path, dest_path):
        response = requests.post(f"{self.api_url}/files/mv?arg={src_path}&arg={dest_path}")
        return response.json()

    def get_cid(self, path):
        response = requests.post(f"{self.api_url}/files/stat?arg={path}")
        return response.json()["Hash"]
