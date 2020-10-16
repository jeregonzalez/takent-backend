use takent
var date_from = new Date(ISODate().getTime() - (1000*60*60*3) - (30*24*60*60*1000))
date_from
db.offer.update({publication_date: {$lte: date_from}}, {$set: {state: "finished"}}, false, true)
