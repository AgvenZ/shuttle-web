from repositories.halte_repository import HalteRepository
from entities.halte_entity import Halte

class HalteService:
    def __init__(self):
        self.repository = HalteRepository()

    def get_all_halte(self):
        haltes, error = self.repository.get_all()
        if error:
            return None, error
        return [halte.to_dict() for halte in haltes], None

    def get_halte_by_id(self, id_halte: int):
        halte, error = self.repository.get_by_id(id_halte)
        if error:
            return None, error
        if halte:
            return halte.to_dict(), None
        return None, "Halte not found"

    def create_halte(self, nama_halte: str, cctv: str, latitude: float = None, longitude: float = None):
        if not nama_halte:
            return None, "Nama halte and CCTV are required"
        
        # Validasi sederhana untuk latitude dan longitude
        if latitude is not None and not isinstance(latitude, (int, float)):
            return None, "Latitude harus berupa angka"
        if longitude is not None and not isinstance(longitude, (int, float)):
            return None, "Longitude harus berupa angka"
        
        halte = Halte(nama_halte=nama_halte, cctv=cctv, latitude=latitude, longitude=longitude)
        created_halte, error = self.repository.create(halte)
        if error:
            return None, error
        return created_halte.to_dict(), None

    def update_halte(self, id_halte: int, nama_halte: str, cctv: str, latitude: float = None, longitude: float = None):
        if not nama_halte:
            return None, "Nama halte and CCTV are required"
        
        if latitude is not None and not isinstance(latitude, (int, float)):
            return None, "Latitude harus berupa angka"
        if longitude is not None and not isinstance(longitude, (int, float)):
            return None, "Longitude harus berupa angka"
        
        halte_data = Halte(nama_halte=nama_halte, cctv=cctv, latitude=latitude, longitude=longitude)
        updated_halte, error = self.repository.update(id_halte, halte_data)
        if error:
            return None, error
        if updated_halte:
            return updated_halte.to_dict(), None
        return None, "Halte not found or no changes made"

    def delete_halte(self, id_halte: int):
        success, error = self.repository.delete(id_halte)
        if error:
            return False, error
        return success, None