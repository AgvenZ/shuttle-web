from flask import jsonify, request
from services.halte_service import HalteService

halte_service = HalteService()

def get_all_halte():
    haltes, error = halte_service.get_all_halte()
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if haltes is None or not haltes:
        return jsonify({"meta": {"status": "success", "message": "No halte found"}, "data": []}), 200
    return jsonify({"meta": {"status": "success", "message": "Halte retrieved successfully"}, "data": haltes}), 200

def get_halte_by_id(id_halte):
    halte, error = halte_service.get_halte_by_id(id_halte)
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 500
    if halte:
        return jsonify({"meta": {"status": "success", "message": "Halte found"}, "data": halte}), 200
    return jsonify({"meta": {"status": "error", "message": "Halte not found"}}), 404

def create_halte():
    data = request.json
    nama_halte = data.get('nama_halte')
    cctv = data.get('cctv')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not nama_halte or not cctv:
        return jsonify({"meta": {"status": "error", "message": "Missing 'nama_halte' or 'cctv'"}}), 400

    new_halte, error = halte_service.create_halte(nama_halte, cctv, latitude, longitude)
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 400
    return jsonify({"meta": {"status": "success", "message": "Halte created successfully"}, "data": new_halte}), 201

def update_halte(id_halte):
    data = request.json
    nama_halte = data.get('nama_halte')
    cctv = data.get('cctv')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not nama_halte or not cctv:
        return jsonify({"meta": {"status": "error", "message": "Missing 'nama_halte' or 'cctv'"}}), 400

    updated_halte, error = halte_service.update_halte(id_halte, nama_halte, cctv, latitude, longitude)
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 400
    if updated_halte:
        return jsonify({"meta": {"status": "success", "message": "Halte updated successfully"}, "data": updated_halte}), 200
    return jsonify({"meta": {"status": "error", "message": "Halte not found or no changes made"}}), 404

def delete_halte(id_halte):
    success, error = halte_service.delete_halte(id_halte)
    if error:
        return jsonify({"meta": {"status": "error", "message": error}}), 400
    if success:
        return jsonify({"meta": {"status": "success", "message": "Halte deleted successfully"}}), 200
    return jsonify({"meta": {"status": "error", "message": "Halte not found"}}), 404