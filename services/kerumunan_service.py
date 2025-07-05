from repositories.kerumunan_repository import KerumunanRepository
from repositories.halte_repository import HalteRepository
from entities.kerumunan_entity import Kerumunan
from datetime import datetime

class KerumunanService:
    def __init__(self):
        self.repository = KerumunanRepository()
        self.halte_repository = HalteRepository()

    def get_all_kerumunan(self):
        kerumunans, error = self.repository.get_all()
        if error:
            return None, error
        return [kerumunan.to_dict() for kerumunan in kerumunans], None

    def get_kerumunan_by_id(self, id_kerumunan: int):
        kerumunan, error = self.repository.get_by_id(id_kerumunan)
        if error:
            return None, error
        if kerumunan:
            return kerumunan.to_dict(), None
        return None, "Kerumunan not found"

    def get_kerumunan_by_id_halte(self, id_halte: int):
        # Pastikan halte ada
        halte, err_halte = self.halte_repository.get_by_id(id_halte)
        if err_halte:
            return None, err_halte
        if not halte:
            return None, f"Halte with id {id_halte} not found."

        kerumunans, error = self.repository.get_by_id_halte(id_halte)
        if error:
            return None, error
        return [kerumunan.to_dict() for kerumunan in kerumunans], None

    def create_kerumunan(self, id_halte: int, jumlah_kerumunan: int):
        if not id_halte or jumlah_kerumunan is None:
            return None, "id_halte and jumlah_kerumunan are required"

        if not isinstance(jumlah_kerumunan, int) or jumlah_kerumunan < 0:
            return None, "jumlah_kerumunan must be a non-negative integer"

        # Cek apakah halte dengan id_halte tersebut ada
        halte, err_halte = self.halte_repository.get_by_id(id_halte)
        if err_halte:
             return None, f"Error checking halte: {err_halte}"
        if not halte:
            return None, f"Halte with id {id_halte} does not exist."

        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kerumunan = Kerumunan(id_halte=id_halte, waktu=waktu, jumlah_kerumunan=jumlah_kerumunan)
        created_kerumunan, error = self.repository.create(kerumunan)
        if error:
            return None, error
        return created_kerumunan.to_dict(), None

    def update_kerumunan(self, id_kerumunan: int, id_halte: int, jumlah_kerumunan: int):
        if not id_halte or jumlah_kerumunan is None:
            return None, "id_halte and jumlah_kerumunan are required"
        
        if not isinstance(jumlah_kerumunan, int) or jumlah_kerumunan < 0:
            return None, "jumlah_kerumunan must be a non-negative integer"

        # Cek apakah halte dengan id_halte tersebut ada jika diubah
        if id_halte is not None:
            halte, err_halte = self.halte_repository.get_by_id(id_halte)
            if err_halte:
                return None, f"Error checking halte: {err_halte}"
            if not halte:
                return None, f"Halte with id {id_halte} does not exist."

        kerumunan_existing, err_existing = self.repository.get_by_id(id_kerumunan)
        if err_existing:
            return None, f"Error checking kerumunan: {err_existing}"
        if not kerumunan_existing:
            return None, f"Kerumunan with id {id_kerumunan} does not exist."

        waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kerumunan_data = Kerumunan(id_halte=id_halte, waktu=waktu, jumlah_kerumunan=jumlah_kerumunan)
        updated_kerumunan, error = self.repository.update(id_kerumunan, kerumunan_data)
        if error:
            return None, error
        if updated_kerumunan:
            return updated_kerumunan.to_dict(), None
        return None, "Kerumunan not found or no changes made"

    def delete_kerumunan(self, id_kerumunan: int):
        success, error = self.repository.delete(id_kerumunan)
        if error:
            return False, error
        return success, None