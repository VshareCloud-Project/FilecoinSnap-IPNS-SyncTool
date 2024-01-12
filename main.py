import os
import configloader
import requests
import subprocess
import logging
from logging import handlers
from CloudFlare import CloudFlare
import tools.ipfs_mfs as ipfs_mfs_tools

def download_file(config):
    if config.snapshot_dowload_mode == "url":
        url = config.getkey("snapshot_url")  
        path = config.getkey("snapshot_file_folder")
        logging.info(f"Downloading {url} to {path}")

        try:
            subprocess.run(["aria2c", url, "-d", path], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to download {url}. Process returned non-zero exit status.")
            logging.error(e)
            return
        except Exception as e:
            logging.error(f"An error occurred while trying to download {url} to {path}")
            logging.error(e)
            return
    else:
        #foo
        pass
    logging.info(f"Downloaded {url} to {path}")

def upload_file(config):
    # Upload file to IPFS
    path = config.getkey("snapshot_file_folder")
    logging.info(f"Uploading {path} to IPFS")
    try:
        """
        Check if the mfs path exists. If it doesn't, create it.
        """
        files = os.listdir(path)
        if len(files) == 1:
            file_path = os.path.join(path, files[0])
            file_cid = subprocess.run(["ipfs", "add", "-Q", "--api", config.getkey("ipfs_api_host"), file_path], check=True, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
            return file_cid, str(files[0])
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to upload {path} to IPFS. Process returned non-zero exit status.")
        logging.error(e)
        return
    except Exception as e:
        logging.error(f"An error occurred while trying to upload {path} to IPFS")
        logging.error(e)
        return

def add_file_to_mfs(config, file_cid, filename):
    ipfs_mfs = ipfs_mfs_tools()
    mfs_path_uuid = config.getkey("mfs_path_uuid")
    if ipfs_mfs.list_directory(mfs_path_uuid) == []:
        ipfs_mfs.create_directory(mfs_path_uuid)
        logging.info(f"Created {mfs_path_uuid} directory in IPFS")
    else:
        logging.info(f"{mfs_path_uuid} directory already exists in IPFS , adding file to mfs path")
        ipfs_mfs.add_file_to_directory(file_cid, mfs_path_uuid, filename)
        ipfs_mfs.add_file_to_directory(file_cid, mfs_path_uuid, "latest")
        logging.info(f"Added {filename} to {mfs_path_uuid} directory in IPFS , and latest file has been updated")
    return ipfs_mfs.get_cid(f"{mfs_path_uuid}")

def update_ipns_to_domain(config, mfs_cid):
    cf = CloudFlare(email=config.getkey("ddns_cloudflare_email") ,token=config.getkey("ddns_cloudflare_api_key"))  
    ipns_domain = config.getkey("ipns_domain")
    domain_name = '.'.join(ipns_domain.split('.')[-2:])  # get the domain name without the subdomain
    zones = cf.zones.get(params={'name': domain_name})
    if not zones:
        logging.error(f"Zone for domain {domain_name} not found. Please check your domain name.")
        return
    zone_id = zones[0]['id']
    logging.info(f"Zone ID for domain {domain_name} is: {zone_id}")
    dns_records = cf.zones.dns_records.get(zone_id, params={'name': ipns_domain})
    if not dns_records:
        # Create DNS record for the subdomain with the IPFS hash
        cf.zones.dns_records.post(zone_id, data={'type': 'TXT', 'name': ipns_domain, 'content': "dnslink=/ipns/" + mfs_cid, 'ttl': 120})
    else:
        # Update DNS record for the subdomain with the IPFS hash
        dns_record_id = dns_records[0]['id']
        cf.zones.dns_records.put(zone_id, dns_record_id, data={'type': 'TXT', 'name': ipns_domain, 'content': "dnslink=/ipns/" + mfs_cid, 'ttl': 120})
    logging.info(f"IPNS domain {ipns_domain} has been updated to point to {mfs_cid}")
    

    


def main():
    c = configloader.config()
    logging.basicConfig(
        level=getattr(logging,c.getkey("log_level")), format="%(asctime)s [%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s"
    )
    if c.getkey("log_file") != "" and c.getkey("log_file") is not None:
        file_log_handler = handlers.RotatingFileHandler(c.getkey("log_file"), mode="a", encoding=c.getkey("log_file_encoding"), maxBytes=c.getkey("log_file_size"), backupCount=c.getkey("log_file_backup_count"))
        formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s")
        file_log_handler.setFormatter(formatter)
        file_log_handler.setLevel(getattr(logging,c.getkey("log_level")))
        logging.getLogger('').addHandler(file_log_handler)
    if c.getkey("log_error_file") != "" and c.getkey("log_error_file") is not None:
        file_error_handler = handlers.RotatingFileHandler(c.getkey("log_error_file"), mode="a", encoding=c.getkey("log_file_encoding"), maxBytes=c.getkey("log_file_size"), backupCount=c.getkey("log_file_backup_count"))
        formatter = logging.Formatter("%(asctime)s [%(levelname)s][%(pathname)s:%(lineno)d]: %(message)s")
        file_error_handler.setFormatter(formatter)
        file_error_handler.setLevel(getattr(logging,c.getkey("log_error_level")))
        logging.getLogger('').addHandler(file_error_handler)
    logging.info("Starting process")
    download_file(c)
    file_cid, filename = upload_file(c)
    mfs_cid = add_file_to_mfs(c, file_cid, filename)

