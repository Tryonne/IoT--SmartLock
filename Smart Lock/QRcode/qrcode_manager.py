from datetime import datetime, timedelta
import qrcode
import os
from Firebase.firebase_crud import base_ref, registar_log

class QRCodeManager:
    def __init__(self):
        self.temp_dir = "static/temp_qr"
        self.current_qr = None
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def generate_qr_code(self, validity_minutes):
        """Generate a new QR code with specified validity"""
        # First clean any expired resources
        self.clean_resources()
        
        # Check if there's an active QR code (both locally and in Firebase)
        active_qr = self.get_active_qr()
        if active_qr:
            valid_until = datetime.fromisoformat(active_qr['valid_until'])
            remaining_seconds = (valid_until - datetime.now()).total_seconds()
            
            # Format expiration message
            if remaining_seconds < 60:
                time_msg = "em menos de um minuto"
            else:
                remaining_minutes = int(remaining_seconds / 60)
                time_msg = f"em aproximadamente {remaining_minutes} minuto{'s' if remaining_minutes > 1 else ''}"
            
            expiration_time = valid_until.strftime("%H:%M:%S")
            raise Exception(
                f"Já existe um QR Code ativo que expira às {expiration_time} ({time_msg}). "
                "Aguarde a expiração ou cancele manualmente."
            )

        # Generate new QR code data
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        qr_data = f"SMARTLOCK_{timestamp}"
        valid_until = datetime.now() + timedelta(minutes=validity_minutes)
        
        # Save to Firebase
        ref = base_ref.child(f"qrcodes/{qr_data}")
        ref.set({
            'created_at': datetime.now().isoformat(),
            'expires_at': valid_until.isoformat(),
            'is_valid': True
        })
        
        # Generate and save QR image
        img_path = os.path.join(self.temp_dir, f"{qr_data}.png")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(img_path)
        
        # Update current QR reference
        self.current_qr = {
            'qr_data': qr_data,
            'valid_until': valid_until.isoformat(),
            'img_path': img_path
        }
        
        return self.current_qr

    def verify_qr_code(self, qr_data):
        """Verify if a QR code is valid and not expired"""
        if not qr_data or not qr_data.startswith("SMARTLOCK_"):
            registar_log(qr_data, "qr", "negado - formato inválido")
            return False
            
        ref = base_ref.child(f"qrcodes/{qr_data}")
        qr_info = ref.get()
        
        if not qr_info or not qr_info.get('is_valid', False):
            registar_log(qr_data, "qr", "negado - não encontrado")
            return False
            
        try:
            expires_at = datetime.fromisoformat(qr_info['expires_at'])
            if datetime.now() > expires_at:
                # Clean up expired code
                self.force_delete(qr_data)
                registar_log(qr_data, "qr", "negado - expirado")
                return False
                
            registar_log(qr_data, "qr", "autorizado")
            return True
            
        except Exception as e:
            print(f"Error verifying QR {qr_data}: {e}")
            registar_log(qr_data, "qr", "negado - erro de verificação")
            return False

    def force_delete(self, qr_data):
        """Force delete a QR code (manual cancellation)"""
        try:
            # Delete from Firebase
            base_ref.child(f"qrcodes/{qr_data}").delete()
            
            # Delete image file
            img_path = os.path.join(self.temp_dir, f"{qr_data}.png")
            if os.path.exists(img_path):
                os.remove(img_path)
            
            # Clear current reference if it matches
            if self.current_qr and self.current_qr['qr_data'] == qr_data:
                self.current_qr = None
                
            print(f"QR code {qr_data} deleted successfully")
            return True
            
        except Exception as e:
            print(f"Error deleting QR {qr_data}: {e}")
            return False

    def clean_resources(self):
        """Clean up expired QR codes from both database and filesystem"""
        try:
            # First check current QR
            if self.current_qr:
                if self.is_expired(self.current_qr['qr_data']):
                    self.force_delete(self.current_qr['qr_data'])
            
            # Then check all QR codes in Firebase
            ref = base_ref.child("qrcodes")
            qrcodes = ref.get() or {}
            
            now = datetime.now()
            for qr_data, info in qrcodes.items():
                try:
                    expires_at = datetime.fromisoformat(info['expires_at'])
                    if now > expires_at:
                        self.force_delete(qr_data)
                except Exception as e:
                    print(f"Error cleaning QR {qr_data}: {e}")
                    
        except Exception as e:
            print(f"Error in clean_resources: {e}")

    def is_expired(self, qr_data):
        """Check if a QR code is expired"""
        ref = base_ref.child(f"qrcodes/{qr_data}")
        qr_info = ref.get()
        
        if not qr_info:
            return True
            
        try:
            expires_at = datetime.fromisoformat(qr_info['expires_at'])
            return datetime.now() > expires_at
        except:
            return True

    def get_active_qr(self):
    # First check our local reference
        if self.current_qr and not self.is_expired(self.current_qr['qr_data']):
            expires_at = datetime.fromisoformat(self.current_qr['valid_until'])
            remaining = int((expires_at - datetime.now()).total_seconds())
            return {
                'qr_data': self.current_qr['qr_data'],
                'valid_until': self.current_qr['valid_until'],
                'remaining': remaining,
                'img_path': self.current_qr['img_path']
            }
        
        # If no local reference or it's expired, check Firebase
        ref = base_ref.child("qrcodes")
        qrcodes = ref.get() or {}
        
        now = datetime.now()
        for qr_data, info in qrcodes.items():
            try:
                expires_at = datetime.fromisoformat(info['expires_at'])
                if now < expires_at:
                    remaining = int((expires_at - now).total_seconds())
                    img_path = os.path.join(self.temp_dir, f"{qr_data}.png")
                    
                    # Update current_qr reference
                    self.current_qr = {
                        'qr_data': qr_data,
                        'valid_until': info['expires_at'],
                        'img_path': img_path
                    }
                    
                    return {
                        'qr_data': qr_data,
                        'valid_until': info['expires_at'],
                        'remaining': remaining,
                        'img_path': img_path
                    }
            except Exception as e:
                print(f"Error checking QR {qr_data}: {e}")
        
        # No active QR found
        self.current_qr = None
        return None


    def refresh_status(self):
        """Refresh the current status from database"""
        if not self.current_qr:
            return
            
        # Check if QR still exists in Firebase
        ref = base_ref.child(f"qrcodes/{self.current_qr['qr_data']}")
        qr_info = ref.get()
        
        if not qr_info or self.is_expired(self.current_qr['qr_data']):
            self.force_delete(self.current_qr['qr_data'])