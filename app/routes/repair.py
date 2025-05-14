from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import json
from app.services.repair_service import RepairService
from app.models.diagnostic import Diagnostic
from app import db
from app.services.service_factory import ServiceFactory

repair = Blueprint('repair', __name__)


@repair.route('/')
@login_required
def index():
    """Rota principal da página de reparos"""
    # Obtém os últimos diagnósticos do usuário para possíveis reparos
    user_diagnostics = Diagnostic.query.filter_by(user_id=current_user.id).order_by(Diagnostic.date.desc()).limit(5).all()
    
    # Serviço de reparo para estatísticas e outros dados
    repair_service = ServiceFactory.get_service(RepairService)
    
    return render_template('repair/index.html', 
                           diagnostics=user_diagnostics,
                           title="Reparo e Otimização")


@repair.route('/diagnostic/<int:diagnostic_id>/repair')
@login_required
def generate_repair_plan(diagnostic_id):
    """Gera um plano de reparo para um diagnóstico específico"""
    try:
        # Carrega o diagnóstico
        diagnostic = Diagnostic.query.get_or_404(diagnostic_id)
        
        # Verifica se o usuário tem permissão para acessar este diagnóstico
        if diagnostic.user_id != current_user.id and not current_user.is_admin() and not current_user.is_technician():
            return render_template('errors/403.html', message="Você não tem permissão para acessar este diagnóstico"), 403
        
        # Carrega os problemas do diagnóstico
        problems = json.loads(diagnostic.notes) if diagnostic.notes else []
        
        if not problems:
            # Não há problemas para reparar
            return render_template('repair/no_problems.html', diagnostic=diagnostic)
        
        # Cria o serviço de reparo
        repair_service = RepairService()
        
        # Gera o plano de reparo
        repair_plan = repair_service.generate_repair_plan(problems)
        
        # Formato da resposta baseado no parâmetro 'format'
        response_format = request.args.get('format', 'html')
        
        if response_format == 'json':
            return jsonify(repair_plan)
        else:
            return render_template('repair/plan.html', 
                                   diagnostic=diagnostic, 
                                   plan=repair_plan)
    
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500


@repair.route('/step/<int:diagnostic_id>/<int:step_index>')
@login_required
def repair_step(diagnostic_id, step_index):
    """Exibe um passo específico do reparo"""
    try:
        # Carrega o diagnóstico
        diagnostic = Diagnostic.query.get_or_404(diagnostic_id)
        
        # Verifica se o usuário tem permissão para acessar este diagnóstico
        if diagnostic.user_id != current_user.id and not current_user.is_admin() and not current_user.is_technician():
            return render_template('errors/403.html', message="Você não tem permissão para acessar este diagnóstico"), 403
        
        # Carrega os problemas do diagnóstico
        problems = json.loads(diagnostic.notes) if diagnostic.notes else []
        
        if not problems or step_index >= len(problems):
            # Não há problemas para reparar ou índice inválido
            return redirect(url_for('repair.generate_repair_plan', diagnostic_id=diagnostic_id))
        
        # Cria o serviço de reparo
        repair_service = RepairService()
        
        # Gera o plano de reparo para este problema específico
        problem = problems[step_index]
        repair_step = repair_service.generate_repair_plan([problem])
        
        # Verifica se há passos anteriores e próximos
        has_previous = step_index > 0
        has_next = step_index < len(problems) - 1
        
        return render_template('repair/step.html', 
                               diagnostic=diagnostic, 
                               step=repair_step['repair_steps'][0],
                               current_index=step_index,
                               has_previous=has_previous,
                               has_next=has_next,
                               total_steps=len(problems))
    
    except Exception as e:
        return render_template('errors/500.html', message=str(e)), 500


@repair.route('/finish/<int:diagnostic_id>', methods=['POST'])
@login_required
def finish_repair(diagnostic_id):
    """Marca o reparo como concluído"""
    try:
        # Carrega o diagnóstico
        diagnostic = Diagnostic.query.get_or_404(diagnostic_id)
        
        # Verifica se o usuário tem permissão para acessar este diagnóstico
        if diagnostic.user_id != current_user.id and not current_user.is_admin() and not current_user.is_technician():
            return jsonify({'success': False, 'message': 'Permissão negada'}), 403
        
        # Atualiza o status do diagnóstico para indicar que foi reparado
        diagnostic.status = "Reparado"
        
        # Adiciona uma nota sobre o reparo
        notes = json.loads(diagnostic.notes) if diagnostic.notes else []
        
        # Marca cada problema como resolvido
        for problem in notes:
            problem['resolved'] = True
        
        diagnostic.notes = json.dumps(notes)
        
        # Salva as alterações
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Rotas da API para serviço de reparo
@repair.route('/api/repair/plan/<diagnostic_id>', methods=['POST'])
@login_required
def api_create_repair_plan(diagnostic_id):
    """API para criar um plano de reparo baseado em um diagnóstico"""
    try:
        from app.services.repair_service import RepairService
        service = RepairService()
        plan = service.create_repair_plan(diagnostic_id)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@repair.route('/api/repair/execute/<plan_id>/<step_id>', methods=['POST'])
@login_required
def api_execute_repair_step(plan_id, step_id):
    """API para executar um passo específico de um plano de reparo"""
    try:
        from app.services.repair_service import RepairService
        service = RepairService()
        result = service.execute_repair_step(plan_id, step_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Rotas da API para planos de manutenção
@repair.route('/api/maintenance/plan', methods=['POST'])
@login_required
def api_create_maintenance_plan():
    """API para criar um plano de manutenção"""
    try:
        data = request.get_json() or {}
        name = data.get('name', 'Plano de Manutenção')
        description = data.get('description', 'Plano de manutenção automático')
        tasks = data.get('tasks', [])
        
        from app.services.cleaner_service import CleanerService
        service = CleanerService()
        plan = service.create_maintenance_plan(name, description, tasks)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@repair.route('/api/maintenance/schedule/<plan_id>', methods=['POST'])
@login_required
def api_schedule_maintenance(plan_id):
    """API para agendar um plano de manutenção"""
    try:
        data = request.get_json() or {}
        frequency = data.get('frequency', 'weekly')
        day_of_week = data.get('day_of_week', 1)  # Segunda-feira por padrão
        time = data.get('time', '03:00')  # 3 AM por padrão
        
        from app.services.cleaner_service import CleanerService
        service = CleanerService()
        schedule = service.schedule_maintenance(plan_id, frequency, day_of_week, time)
        
        return jsonify({
            'success': True,
            'schedule': schedule
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
@repair.route('/api/maintenance/execute/<plan_id>/<task_id>', methods=['POST'])
@login_required
def api_execute_maintenance_task(plan_id, task_id):
    """API para executar uma tarefa de manutenção"""
    try:
        from app.services.cleaner_service import CleanerService
        service = CleanerService()
        result = service.execute_maintenance_task(plan_id, task_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@repair.route('/api/maintenance/history')
@login_required
def api_maintenance_history():
    """API para obter o histórico de manutenções"""
    try:
        from app.services.cleaner_service import CleanerService
        service = CleanerService()
        
        # Obtém o número máximo de registros
        limit = request.args.get('limit', 10, type=int)
        
        # Se o usuário não é admin, filtra pelo próprio usuário
        user_id = None if current_user.is_admin() else current_user.id
        
        # Obtém o histórico de manutenções
        history = service.get_maintenance_history(user_id=user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@repair.route('/api/repair/plan/<plan_id>', methods=['GET'])
@login_required
def get_repair_plan_api(plan_id):
    """API para obter um plano de reparo"""
    # Obtém o serviço de reparo
    repair_service = ServiceFactory.get_service(RepairService)
    
    try:
        # Obtém o plano de reparo
        plan = repair_service.get_repair_plan(plan_id)
        
        return jsonify({
            'success': True,
            'plan': plan
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 