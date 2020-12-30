BASEDIR=$(dirname "$0")
mongo < $BASEDIR/lib/expire_services.js
