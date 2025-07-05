from repositories.export_repository import ExportRepository
import pandas as pd
import io

class ExportService:
    def __init__(self):
        self.repository = ExportRepository()

    def generate_kerumunan_csv_file(self):
        """
        Memproses data kerumunan dan menghasilkan file CSV.
        """
        data, error = self.repository.get_kerumunan_export_data()
        if error:
            return None, error
        if not data:
            return None, "Tidak ada data untuk diekspor."

        # Buat DataFrame dari pandas
        df = pd.DataFrame(data)

        # Ubah nama kolom
        df.rename(columns={
            'id_kerumunan': 'ID Laporan',
            'nama_halte': 'Nama Halte',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
            'waktu': 'Waktu Pencatatan',
            'jumlah_kerumunan': 'Jumlah Kerumunan'
        }, inplace=True)

        df = df[['ID Laporan', 'Nama Halte', 'Latitude', 'Longitude', 'Waktu Pencatatan', 'Jumlah Kerumunan']]

        # Format kolom waktu
        if 'Waktu Pencatatan' in df.columns:
            df['Waktu Pencatatan'] = pd.to_datetime(df['Waktu Pencatatan']).dt.strftime('%Y-%m-%d %H:%M:%S')

        # Gunakan io.StringIO untuk menangani output string sebagai file
        # .to_csv() secara default akan menggunakan koma sebagai pemisah, 
        # yang memastikan data berada di kolom terpisah.
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8')
        
        # Dapatkan nilai string dari buffer
        return output.getvalue(), None