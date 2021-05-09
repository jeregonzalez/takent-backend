curl -X GET http://localhost:5000/api/v1/task/generate_notifications
curl -X GET http://localhost:5000/api/v1/task/expire_services
curl -X GET http://localhost:5000/api/v1/task/expire_offers
curl -X GET http://localhost:5000/api/v1/task/publish_programmed_offers
mongodump --db=takent --gzip --archive="$HOME"/backups/mongobackup_"$(date +'%d-%m-%Y_%H-%M')".gz
find "$HOME"/backups -type f -mtime +7 -name '*.gz' -execdir rm -- '{}' \;
