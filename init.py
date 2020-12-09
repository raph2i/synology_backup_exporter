#!/usr/bin/env python

from prometheus_client import start_http_server, Summary, Gauge, Enum
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import random
import time 
import datetime
import requests
import json
from synology_api import active_backup

with open('config.json') as config_file:
    config = json.load(config_file)

def active_backup_register_metrics():
    global gauge_active_backup_lastbackup_timestamp
    gauge_active_backup_lastbackup_timestamp = Gauge('synology_active_backup_lastbackup_timestamp','Timestamp of last backup', ['vmname', 'hostname', 'vmuuid', 'vmos'])
    global gauge_active_backup_lastbackup_duration
    gauge_active_backup_lastbackup_duration = Gauge('synology_active_backup_lastbackup_duration','Duration of last backup in Seconds', ['vmname', 'hostname', 'vmuuid', 'vmos'])
    global gauge_active_backup_lastbackup_transfered_bytes
    gauge_active_backup_lastbackup_transfered_bytes = Gauge('synology_active_backup_lastbackup_transfered_bytes','Transfered data of last backup in Bytes', ['vmname', 'hostname', 'vmuuid', 'vmos'])
    global gauge_active_backup_lastbackup_result
    gauge_active_backup_lastbackup_result = Gauge('synology_active_backup_lastbackup_result','Result of last backup - 2 = Good, 4 = Bad', ['vmname', 'hostname', 'vmuuid', 'vmos'])

def active_backup_login():
    global active_backup_session
    active_backup_session = active_backup.ActiveBackupBusiness(config['DSMAddress'], config['DSMPort'], config['Username'], config['Password'], config['Secure'], config['Cert_Verify'])

def active_backup_get_info():
    abb_hypervisor = active_backup_session.list_vm_hypervisor()
    abb_vms = active_backup_session.list_device_transfer_size()

    hypervisor_list = {}

    for hypervisor in abb_hypervisor['data']:
        hypervisor_list[hypervisor['inventory_id']] = hypervisor['host_name']

    for vm in abb_vms['data']['device_list']:
        vm_hypervisor = hypervisor_list[vm['device']['inventory_id']]
        vm_hostname = vm['device']['host_name']
        vm_uuid = vm['device']['device_uuid']
        vm_os = vm['device']['os_name']

        try: #trying, if no backup is existing, this will fail.
            vm_backup_start_timestamp = vm['transfer_list'][0]['time_start']
            vm_backup_end_timestamp = vm['transfer_list'][0]['time_end']
            vm_backup_duration_seconds = vm_backup_end_timestamp - vm_backup_start_timestamp
            vm_backup_status = vm['transfer_list'][0]['status']
            vm_backup_transfered_bytes = vm['transfer_list'][0]['transfered_bytes']
            gauge_active_backup_lastbackup_timestamp.labels(vm_hostname, vm_hypervisor, vm_uuid, vm_os).set(vm_backup_end_timestamp)
            gauge_active_backup_lastbackup_duration.labels(vm_hostname, vm_hypervisor, vm_uuid, vm_os).set(vm_backup_duration_seconds)
            gauge_active_backup_lastbackup_transfered_bytes.labels(vm_hostname, vm_hypervisor, vm_uuid, vm_os).set(vm_backup_transfered_bytes)
            gauge_active_backup_lastbackup_result.labels(vm_hostname, vm_hypervisor, vm_uuid, vm_os).set(vm_backup_status)
        except IndexError:
            print('Failed to load Backups')

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

if __name__ == '__main__':
    print("Synology Backup Exporter")
    print("2020 - raphii / Raphael Pertl")


    if config['ActiveBackup']:
        active_backup_register_metrics()
        active_backup_login()
        active_backup_get_info()

    # Start up the server to expose the metrics.
    start_http_server(int(config['ExporterPort']))
    print("Web Server running on Port " + str(config['ExporterPort']))
    
    while True:
        process_request(random.random())
        time.sleep(5)
        if config['ActiveBackup']:
            active_backup_get_info()
