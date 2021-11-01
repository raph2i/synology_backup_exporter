#!/usr/bin/env python

from prometheus_client import start_http_server, Summary, Gauge, Enum
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import random
import time 
import datetime
import requests
import json

import sys
sys.path.insert(0, '/home/raphael/Projekte/synology-api')
from synology_api import core_active_backup as active_backup
from synology_api import core_backup as hyper_backup

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
    active_backup_session = active_backup.ActiveBackupBusiness(config['DSMAddress'], config['DSMPort'], config['Username'], config['Password'], config['Secure'], config['Cert_Verify'], config['DSM_Version'])

def active_backup_get_info():
    abb_hypervisor = active_backup_session.list_vm_hypervisor()
    abb_vms = active_backup_session.list_device_transfer_size()

    hypervisor_list = {}

    for hypervisor in abb_hypervisor['data']:
        hypervisor_list[hypervisor['inventory_id']] = hypervisor['host_name']

    for vm in abb_vms['data']['device_list']:
        if vm['device']['inventory_id'] != 0:
            vm_hypervisor = hypervisor_list[vm['device']['inventory_id']]
        else:
            vm_hypervisor = vm['device']['host_name']
        
        vm_hostname = vm['device']['host_name']
        vm_uuid = vm['device']['device_uuid']
        vm_os = vm['device']['os_name']

        try: #trying, if no backup is existing, this will fail.
            if vm['transfer_list']:
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
            print('ERROR - Failed to load Backups.')

def hyper_backup_register_metrics():
    global gauge_hyper_backup_lastbackup_successful_timestamp
    gauge_hyper_backup_lastbackup_successful_timestamp = Gauge('synology_hyper_backup_lastbackup_successful_timestamp','Timestamp of last successful backup', ['task_id', 'task_name', 'target_type'])
    global gauge_hyper_backup_lastbackup_timestamp
    gauge_hyper_backup_lastbackup_timestamp = Gauge('synology_hyper_backup_lastbackup_timestamp','Timestamp of last backup', ['task_id', 'task_name', 'target_type'])
    global gauge_hyper_backup_lastbackup_duration
    gauge_hyper_backup_lastbackup_duration = Gauge('synology_hyper_backup_lastbackup_duration','Duration of last backup in Seconds', ['task_id', 'task_name', 'target_type'])

def hyper_backup_login():
    global hyper_backup_session
    hyper_backup_session = hyper_backup.Backup(config['DSMAddress'], config['DSMPort'], config['Username'], config['Password'], config['Secure'], config['Cert_Verify'], config['DSM_Version'])

def hyper_backup_get_info():
    hyper_backup_data = hyper_backup_session.backup_task_list()

    hyper_backup_tasklist = {}
    hyper_backup_taskname = {}
    hyper_backup_tasktype = {}

    for task in hyper_backup_data['data']['task_list']:
        hyper_backup_tasklist[task['task_id']] = task['task_id']
        hyper_backup_taskname[task['task_id']] = task['name']
        hyper_backup_tasktype[task['task_id']] = task['target_type']

    for result in hyper_backup_tasklist:
        hyper_backup_taskresult = hyper_backup_session.backup_task_result(result)

        hyper_backup_task = hyper_backup_taskname[result] #taskname
        hyper_backup_last_success = hyper_backup_taskresult['data']['last_bkp_success_time'] #last success

        hyper_backup_last_success_timestamp = time.mktime(time.strptime(hyper_backup_last_success, "%Y/%m/%d %H:%M"))

        hyper_backup_start_time = hyper_backup_taskresult['data']['last_bkp_time']
        hyper_backup_end_time = hyper_backup_taskresult['data']['last_bkp_end_time']

        hyper_backup_start_timestamp = time.mktime(time.strptime(hyper_backup_start_time, "%Y/%m/%d %H:%M"))
        hyper_backup_end_timestamp = time.mktime(time.strptime(hyper_backup_end_time, "%Y/%m/%d %H:%M"))
    
        hyper_backup_duration_seconds = hyper_backup_end_timestamp - hyper_backup_start_timestamp

        try: #trying, if no backup is existing, this will fail.
            gauge_hyper_backup_lastbackup_successful_timestamp.labels(hyper_backup_tasklist[result],hyper_backup_taskname[result],hyper_backup_tasktype[result]).set(hyper_backup_last_success_timestamp)
            gauge_hyper_backup_lastbackup_timestamp.labels(hyper_backup_tasklist[result],hyper_backup_taskname[result],hyper_backup_tasktype[result]).set(hyper_backup_end_timestamp)
            gauge_hyper_backup_lastbackup_duration.labels(hyper_backup_tasklist[result],hyper_backup_taskname[result],hyper_backup_tasktype[result]).set(hyper_backup_duration_seconds)

        except IndexError:
            print('ERROR - Failed to load Backups.')

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

if __name__ == '__main__':
    print("Synology Backup Exporter")
    print("2021 - raphii / Raphael Pertl")


    if config['ActiveBackup']:
        active_backup_register_metrics()
        active_backup_login()
        active_backup_get_info()

    if config['HyperBackup']:
        hyper_backup_register_metrics()
        hyper_backup_login()
        hyper_backup_get_info()

    # Start up the server to expose the metrics.
    start_http_server(int(config['ExporterPort']))
    print("INFO - Web Server running on Port " + str(config['ExporterPort']))
    
    while True:
        process_request(random.random())
        time.sleep(5)
        if config['ActiveBackup']:
            active_backup_get_info()
        if config['HyperBackup']:
            hyper_backup_get_info()
