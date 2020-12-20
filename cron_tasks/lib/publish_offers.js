use takent
var date_from = new Date(ISODate().getTime() - (1000*60*60*3))
db.offer.update({publication_date: {$lte: date_from}, state: {$eq: "programmed"}}, {$set: {state: "active"}}, false, true)
