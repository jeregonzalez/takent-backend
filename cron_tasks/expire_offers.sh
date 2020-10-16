BASEDIR=$(dirname "$0")
mongo < $BASEDIR/lib/expire_offers.js
