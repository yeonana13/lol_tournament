"""챔피언 데이터 API"""
from flask import Blueprint, jsonify, request
from database.connection import SessionLocal
from database.champion_models import Champion

champion_bp = Blueprint('champion', __name__)

@champion_bp.route('/api/champions', methods=['GET'])
def get_all_champions():
    """모든 챔피언 목록 조회"""
    db = SessionLocal()
    try:
        champions = db.query(Champion).order_by(Champion.korean_name).all()
        return jsonify([champ.to_dict() for champ in champions])
    finally:
        db.close()

@champion_bp.route('/api/champions/search', methods=['GET'])
def search_champions():
    """챔피언 검색"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    db = SessionLocal()
    try:
        champions = db.query(Champion).filter(
            (Champion.korean_name.contains(query)) |
            (Champion.english_name.ilike(f'%{query}%'))
        ).order_by(Champion.korean_name).all()
        
        return jsonify([champ.to_dict() for champ in champions])
    finally:
        db.close()

@champion_bp.route('/api/champions/<champion_name>', methods=['GET'])
def get_champion_by_name(champion_name):
    """특정 챔피언 정보 조회"""
    db = SessionLocal()
    try:
        champion = db.query(Champion).filter(
            (Champion.korean_name == champion_name) |
            (Champion.english_name.ilike(champion_name))
        ).first()
        
        if champion:
            return jsonify(champion.to_dict())
        else:
            return jsonify({'error': 'Champion not found'}), 404
    finally:
        db.close()
