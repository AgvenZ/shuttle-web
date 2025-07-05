from flask import jsonify, request
from services.kerumunan_service import KerumunanService

kerumunan_service = KerumunanService()

def get_all_kerumunan():
    kerumunans, error = kerumunan_service.get_all_kerumunan()
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if kerumunans is None or not kerumunans:
        return jsonify({"meta": {"status": "success", "message": "No kerumunan found"}, "data": []}), 200
    return jsonify({"meta": {"status": "success", "message": "Kerumunan retrieved successfully"}, "data": kerumunans}), 200

def get_kerumunan_by_id(id_kerumunan):
    kerumunan, error = kerumunan_service.get_kerumunan_by_id(id_kerumunan)
    if error:
        if "not found" in str(error).lower():
            return jsonify({"meta": {"status": "error", "message": error}}), 404
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if kerumunan:
        return jsonify({"meta": {"status": "success", "message": "Kerumunan found"}, "data": kerumunan}), 200
    return jsonify({"meta": {"status": "error", "message": "Kerumunan not found"}}), 404

def get_kerumunan_by_id_halte_controller(id_halte):
    kerumunans, error = kerumunan_service.get_kerumunan_by_id_halte(id_halte)
    if error:
        if f"Halte with id {id_halte} not found" in error or f"Halte with id {id_halte} does not exist" in error :
             return jsonify({"meta": {"status": "error", "message": error}}), 404
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if kerumunans is None or not kerumunans:
        return jsonify({"meta": {"status": "success", "message": f"No kerumunan found for halte id {id_halte}"}, "data": []}), 200
    return jsonify({"meta": {"status": "success", "message": f"Kerumunan for halte id {id_halte} retrieved successfully"}, "data": kerumunans}), 200

def create_kerumunan():
    data = request.json
    if not data:
        return jsonify({"meta": {"status": "error", "message": "Request body JSON need fulfilled"}}), 400

    id_halte = data.get('id_halte')
    jumlah_kerumunan = data.get('jumlah_kerumunan')

    if id_halte is None or jumlah_kerumunan is None:
        return jsonify({"meta": {"status": "error", "message": "Missing 'id_halte', or 'jumlah_kerumunan'"}}), 400

    try:
        id_halte = int(id_halte)
        jumlah_kerumunan = int(jumlah_kerumunan)
    except ValueError:
        return jsonify({"meta": {"status": "error", "message": "'id_halte' and 'jumlah_kerumunan' must be integers"}}), 400

    new_kerumunan, error = kerumunan_service.create_kerumunan(id_halte, jumlah_kerumunan)
    if error:
        if f"Halte with id {id_halte} does not exist" in error or \
            "need fulfilled" in error or "must integer" in error:
                return jsonify({"meta": {"status": "error", "message": error}}), 400
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    return jsonify({"meta": {"status": "success", "message": "Kerumunan created successfully"}, "data": new_kerumunan}), 201

def update_kerumunan(id_kerumunan):
    data = request.json
    if not data:
        return jsonify({"meta": {"status": "error", "message": "Request body JSON need fulfilled"}}), 400

    id_halte = data.get('id_halte')
    jumlah_kerumunan = data.get('jumlah_kerumunan')

    if id_halte is None or jumlah_kerumunan is None:
        return jsonify({"meta": {"status": "error", "message": "Missing 'id_halte', or 'jumlah_kerumunan'"}}), 400

    try:
        id_halte = int(id_halte)
        jumlah_kerumunan = int(jumlah_kerumunan)
    except ValueError:
        return jsonify({"meta": {"status": "error", "message": "'id_halte' and 'jumlah_kerumunan' must be integers"}}), 400

    updated_kerumunan, error = kerumunan_service.update_kerumunan(id_kerumunan, id_halte, jumlah_kerumunan)
    if error:
        if f"Halte with id {id_halte} does not exist" in error or \
            "not found" in error or \
            "need fulfilled" in error or "must integer" in error:
                return jsonify({"meta": {"status": "error", "message": error}}), 404
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if updated_kerumunan:
        return jsonify({"meta": {"status": "success", "message": "Kerumunan updated successfully"}, "data": updated_kerumunan}), 200
    return jsonify({"meta": {"status": "error", "message": "Kerumunan no changes made"}}), 404

def delete_kerumunan(id_kerumunan):
    success, error = kerumunan_service.delete_kerumunan(id_kerumunan)
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if success:
        return jsonify({"meta": {"status": "success", "message": "Kerumunan deleted successfully"}}), 200
    return jsonify({"meta": {"status": "error", "message": "Kerumunan not found"}}), 404