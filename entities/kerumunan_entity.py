from datetime import datetime

class Kerumunan:
    def __init__(self, id_halte: int, waktu: datetime, jumlah_kerumunan: int, id_kerumunan: int = None):
        self.id_kerumunan = id_kerumunan
        self.id_halte = id_halte
        self.waktu = waktu
        self.jumlah_kerumunan = jumlah_kerumunan

    def to_dict(self):
        return {
            "id_kerumunan": self.id_kerumunan,
            "id_halte": self.id_halte,
            "waktu": self.waktu.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.waktu, datetime) else self.waktu,
            "jumlah_kerumunan": self.jumlah_kerumunan
        }