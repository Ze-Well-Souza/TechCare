from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.orm import Session
from src.services.auth_service import AuthService
from src.models.user import UserRole

user_bp = Blueprint('user', __name__)

class UserController:
    def __init__(self, db_session: Session):
        self.auth_service = AuthService(db_session)
        self.db = db_session

    @user_bp.route('/register', methods=['POST'])
    @jwt_required()  # Apenas usuários autenticados podem registrar novos usuários
    def register_user(self):
        current_user_role = get_jwt_identity()['role']
        
        # Apenas admin master pode registrar novos usuários
        if current_user_role != UserRole.ADMIN_MASTER.value:
            return jsonify({"msg": "Acesso não autorizado"}), 403

        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = UserRole(data.get('role'))

        try:
            user = self.auth_service.create_user(username, email, password, role)
            return jsonify({
                "msg": "Usuário criado com sucesso", 
                "user_id": user.id
            }), 201
        except Exception as e:
            return jsonify({"msg": str(e)}), 400

    @user_bp.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = UserController.auth_service.authenticate_user(username, password)
        if user:
            access_token = create_access_token(identity={
                'username': user.username, 
                'role': user.role.value
            })
            return jsonify({
                "access_token": access_token,
                "user_role": user.role.value
            }), 200
        return jsonify({"msg": "Credenciais inválidas"}), 401

    @user_bp.route('/change-password', methods=['POST'])
    @jwt_required()
    def change_password(self):
        current_user = get_jwt_identity()
        data = request.get_json()
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        user = self.db.query(User).filter_by(username=current_user['username']).first()
        
        if self.auth_service.change_password(user, old_password, new_password):
            return jsonify({"msg": "Senha alterada com sucesso"}), 200
        return jsonify({"msg": "Falha ao alterar senha"}), 400

    @user_bp.route('/profile', methods=['GET'])
    @jwt_required()
    def get_profile(self):
        current_user = get_jwt_identity()
        user = self.db.query(User).filter_by(username=current_user['username']).first()
        
        return jsonify({
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }), 200
