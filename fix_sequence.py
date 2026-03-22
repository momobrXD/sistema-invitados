from app import app, db

with app.app_context():
    db.session.execute(db.text("SELECT setval('invitados_id_seq', (SELECT MAX(id) FROM invitados))"))
    db.session.commit()
    print("Secuencia reseteada OK")
