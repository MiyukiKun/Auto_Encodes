import heroku3
key = "88ee4dd4-37f8-44ca-97e2-0cbcded99841"


h = heroku3.from_key(key)
app = h.apps()[0]
app.restart()
