from flask import request, Response
from services.export_service import ExportService
from datetime import datetime

export_service = ExportService()

def export_kerumunan_data():
    """Menangani request untuk mengekspor data kerumunan ke format CSV."""
    file_data, error = export_service.generate_kerumunan_csv_file()

    if error:
        return Response(f"Error: {error}", status=400, mimetype='text/plain')

    # Siapkan nama file CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"laporan_kerumunan_{timestamp}.csv"
    mimetype = "text/csv"

    # Buat response untuk mengunduh file CSV
    return Response(
        file_data,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )