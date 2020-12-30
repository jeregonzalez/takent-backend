use takent
var date_from = new Date(ISODate().getTime() - (1000*60*60*3) - (30*24*60*60*1000))
db.service.update({publication_date: {$lte: date_from}, state: {$ne: "finished"}}, {$set: {state: "finished"}}, false, true)
