class Halte:
    def __init__(self, nama_halte: str, cctv: str, latitude: float = None, longitude: float = None, id_halte: int = None):
        self.id_halte = id_halte
        self.nama_halte = nama_halte
        self.cctv = cctv
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "id_halte": self.id_halte,
            "nama_halte": self.nama_halte,
            "cctv": self.cctv,
            "latitude": self.latitude,
            "longitude": self.longitude
        }