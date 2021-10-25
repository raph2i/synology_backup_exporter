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
6. add port settings
7. ???
8. scrape metrics :)


### Configure
change the settings in config.json to your needs

The default exporter-port is 9771.


### Metrics
Active Backup for Business metrics have these labels:
`hostname,vmname,vmos,vmuuid`


metrics:
```
synology_active_backup_lastbackup_timestamp
synology_active_backup_lastbackup_duration
synology_active_backup_lastbackup_transfered_bytes
synology_active_backup_lastbackup_result
```

### Alert rules:

#### Last Backup not successful:
```
name: Synology Last Backup not successful
expr: synology_active_backup_lastbackup_result != 2
for: 1m
```

#### Last Backup older than 72 hours:
```
name: Synology Last Backup older than 72 hours
expr: ((synology_active_backup_lastbackup_timestamp - time()) / 3600) < -72
for: 1m
```

### License
MIT // 2021 - Raphael Pertl

#### Special thanks to [synology-api](https://github.com/N4S4/synology-api)