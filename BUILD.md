Build Image
```
sudo docker build . -t raphii/synology_backup_exporter:dsm7
```

Test Image
```
sudo docker run -v "/home/raphael/Projekte/synology_backup_exporter/config.json:/app/config.json" raphii/synology_backup_exporter:dsm7
```

Push Image

```
sudo docker push raphii/synology_backup_exporter:dsm7
```