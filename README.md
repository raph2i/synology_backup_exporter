# Synology Backup Exporter

### Install
#### Docker
docker-image available [Docker Hub](https://hub.docker.com/r/raphii/synology_backup_exporter)

#### Synology Docker

0. create config.json in /volume1/docker/synology_backup_exporter (or elsewhere)
1. Search for "synology_backup_exporter" in Docker Registry
2. select tag "dsm7"
3. wait for image download to finish
4. launch image
5. set config.json as filevolume to /app/config.json
6. add port settings (The default exporter-port is 9771)
7. ???
8. scrape metrics :)


### Configure

#### Configure with just a config file
Copy `config.json.dist` to `config.json` then change the settings in `config.json` to your needs

#### Configure with just Environment Variables
Look in the `config.json.dist` file, then simply uppercase the keys and provide the values, for example:
* `DSMAddress` becomes `DSMADDRESS`
* `Cert_Verify` becomes `CERT_VERIFY`
* etc

#### Configure with both the config file and Environment Variables
Copy `config.json.dist` to `config.json` then change the settings in `config.json` to your needs. Remove any lines that are not wanted in the config file, for example if having a password in the config file is not desired, remove that line, then provide the environment variable `PASSWORD`. If a value is provided in the config file and as an environment variable, the config file will take precedence. Note: JSON files should not have a `,` on the last configuration line, if the last line has a comma this exporter will not work


### Metrics
#### Active Backup for Business
Active Backup for Business metrics have these labels:
`hostname,vmname,vmos,vmuuid`


metrics:
```
synology_active_backup_lastbackup_timestamp
synology_active_backup_lastbackup_duration
synology_active_backup_lastbackup_transfered_bytes
synology_active_backup_lastbackup_result
```
#### Hyper Backup
Hyper Backup metrics have these labels:
`task_id,task_name,target_type`

```
synology_hyper_backup_lastbackup_successful_timestamp
synology_hyper_backup_lastbackup_timestamp
synology_hyper_backup_lastbackup_duration
```
**Note**: For the first time a Hyper Backup is run, the exporter will report the backup job as being successful with a duration of 0 seconds, and completion timestamps of whenever the exporter scraped the Synology.

#### Hyper Backup Vault
Hyper Backup Vault metrics have these labels:
`target_name,target_id,target_status`

```
synology_hyper_backup_vault_last_backup_duration_seconds
synology_hyper_backup_vault_last_backup_start_timestamp
synology_hyper_backup_vault_target_used_size_bytes

```

### Alert rules:

#### Last Backup not successful:
##### Active Backup
```
name: Synology Active Backup Last Backup not successful
expr: synology_active_backup_lastbackup_result != 2
for: 1m
```
##### Hyper Backup
```
name: Synology Hyper Backup Last Backup not successful
expr: synology_hyper_backup_lastbackup_timestamp != synology_hyper_backup_lastbackup_successful_timestamp
for: 1m
```

#### Last Backup older than 72 hours:
##### Active Backup
```
name: Synology Active Backup Last Backup older than 72 hours
expr: ((synology_active_backup_lastbackup_timestamp - time()) / 3600) < -72
for: 1m
```
##### Hyper Backup
```
name: Synology Hyper Backup Last Backup older than 72 hours
expr: ((synology_hyper_backup_lastbackup_successful_timestamp - time()) / 3600) < -72
for: 1m
```

### License
MIT // 2021 - Raphael Pertl

#### Special thanks to [synology-api](https://github.com/N4S4/synology-api)
