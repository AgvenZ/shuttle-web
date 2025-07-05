from flask import Blueprint
from controllers import kerumunan_controller

kerumunan_bp = Blueprint('kerumunan_bp', __name__, url_prefix='/kerumunan')

kerumunan_bp.route('', methods=['GET'])(kerumunan_controller.get_all_kerumunan)
kerumunan_bp.route('/<int:id_kerumunan>', methods=['GET'])(kerumunan_controller.get_kerumunan_by_id)
kerumunan_bp.route('/halte/<int:id_halte>', methods=['GET'])(kerumunan_controller.get_kerumunan_by_id_halte_controller)
kerumunan_bp.route('', methods=['POST'])(kerumunan_controller.create_kerumunan)
kerumunan_bp.route('/<int:id_kerumunan>', methods=['PUT'])(kerumunan_controller.update_kerumunan)
kerumunan_bp.route('/<int:id_kerumunan>', methods=['DELETE'])(kerumunan_controller.delete_kerumunan)