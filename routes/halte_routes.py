from flask import Blueprint
from controllers import halte_controller

halte_bp = Blueprint('halte_bp', __name__, url_prefix='/halte')

halte_bp.route('', methods=['GET'])(halte_controller.get_all_halte)
halte_bp.route('/<int:id_halte>', methods=['GET'])(halte_controller.get_halte_by_id)
halte_bp.route('', methods=['POST'])(halte_controller.create_halte)
halte_bp.route('/<int:id_halte>', methods=['PUT'])(halte_controller.update_halte)
halte_bp.route('/<int:id_halte>', methods=['DELETE'])(halte_controller.delete_halte)