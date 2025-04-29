import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
from config import DATABASE_URL

# Initialize Firebase app
cred = credentials.Certificate("Firebase/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL  
})

base_ref = db.reference('smarlock')

# === CRUD ===
def criar_autorizacao(entrada, tipo, autorizado):
    chave = f"{tipo}_{entrada}"
    ref = base_ref.child(f"autorizacoes/{chave}")
    ref.set({
        "tipo": tipo,
        "autorizado": autorizado,
        "entrada": entrada 
    })

def atualizar_autorizacao(entrada_original, nova_entrada, tipo, autorizado):
    chave_original = f"{tipo}_{entrada_original}"
    base_ref.child(f"autorizacoes/{chave_original}").delete()
    
    chave_nova = f"{tipo}_{nova_entrada}"
    base_ref.child(f"autorizacoes/{chave_nova}").set({
        "tipo": tipo,
        "autorizado": autorizado,
        "entrada": nova_entrada
    })

def apagar_autorizacao(entrada, tipo):
    chave = f"{tipo}_{entrada}"
    base_ref.child(f"autorizacoes/{chave}").delete()

def ler_autorizacoes():
    ref = base_ref.child("autorizacoes")
    autorizacoes = ref.get() or {}
    
    result = {}
    for key, value in autorizacoes.items():
        entrada = value.get("entrada", key.split("_")[1])
        result[entrada] = {
            "tipo": value["tipo"],
            "autorizado": value["autorizado"]
        }
    return result


# === HISTORICO ===
def registar_log(entrada, tipo, resultado, timestamp=None):
    try:
        log_data = {
            "entrada": entrada,
            "tipo": tipo,
            "resultado": resultado,
            "data": timestamp if timestamp else datetime.now().isoformat()
        }
        ref = db.reference('smarlock/logs')
        ref.push(log_data)
        return True
    except Exception as e:
        print(f"Erro ao registrar log: {str(e)}")
        return False

def ler_logs():
    try:
        ref = base_ref.child('logs') 
        logs = ref.get()
        return logs if logs else {}
    except Exception as e:
        print(f"Erro ao ler logs: {e}")
        return {}

def limpar_logs():
    try:
        base_ref.child('logs').delete()
        return True
    except Exception as e:
        print(f"Error clearing logs: {str(e)}")
        return False

# === DEFINICOES ===
def atualizar_configuracoes(config):
    ref = base_ref.child('settings')  
    ref.update({
        'two_factor_enabled': config.get('two_factor_enabled', False),
        'pin_enabled': config.get('pin_enabled', True)
    })

def ler_configuracoes():
    ref = base_ref.child('settings')
    settings = ref.get() or {
        'two_factor_enabled': False,
        'pin_enabled': True
    }
    return settings


def ler_qrcode(qr_code):
    """Read QR code data from Firebase"""
    try:
        qr_data = base_ref.child('qrcodes').child(qr_code).get()
        return qr_data is not None  # Return True if QR exists, False otherwise
    except Exception as e:
        print(f"Error reading QR code: {str(e)}")
        return False


# === VERIFICAR ===
def verificar_autorizacao(entrada, tipo, registrar_log=True):
    try:
        if not entrada or not tipo:
            return False
            
        chave = f"{tipo}_{entrada}"
        ref = base_ref.child(f"autorizacoes/{chave}")
        dados = ref.get()
        
        if dados and dados.get("autorizado"):
            if registrar_log:
                registar_log(entrada, tipo, "autorizado")
            return True
        else:
            if registrar_log:
                registar_log(entrada, tipo, "negado")
            return False
            
    except Exception as e:
        print(f"Erro ao verificar autorização: {str(e)}")
        if registrar_log:
            registar_log(entrada, tipo, "erro")
        return False
