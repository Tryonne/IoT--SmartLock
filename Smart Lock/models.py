class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tipo = db.Column(db.String(50), nullable=False)  # 'PIN' ou 'QR'
    status = db.Column(db.String(50), nullable=False)  # 'autorizado' ou 'negado'
    metodo = db.Column(db.String(50), nullable=False)