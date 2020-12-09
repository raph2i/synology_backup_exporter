# Synology Backup Exporter

### Install
```
TBD
``` 

### Configure
change the settings in config.json to your needs

The default exporter-port is 9771.


### Metrics
Active Backup for Business metrics have these labels:
` hostname,vmname,vmos,vmuuid`


metrics:
```
synology_active_backup_lastbackup_timestamp
synology_active_backup_lastbackup_duration
synology_active_backup_lastbackup_transfered_bytes
synology_active_backup_lastbackup_result
```

### Alert rules:

```
TBD
```

### License
MIT // 2020 - Raphael Pertl

#### Special thanks to [synology-api](https://github.com/N4S4/synology-api)