from flask import Blueprint
from controllers import export_controller

export_bp = Blueprint('export_bp', __name__, url_prefix='/export')

export_bp.route('/kerumunan', methods=['GET'])(export_controller.export_kerumunan_data)