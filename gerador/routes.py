import os, queue, threading
from flask import Blueprint, request, flash, redirect, render_template, send_file, url_for, json, jsonify, Response, session
from werkzeug.utils import secure_filename
from gerador.config import Config
from gerador.constants import ERRO_COMPLEMENTO2, ERRO_COMPLEMENTO3, LOG_COMPLEMENTOS, MESSAGE_QUEUE, RESULTS_LOCK, PROCESSING_RESULTS
from gerador.services.process_csv import processar_csv
from gerador.services.processar_conversor_csv import processar_conversor_csv
from gerador.services.processar_conversor_csv_grande import processar_conversor_csv_grande
from gerador.utils import update_progress
from gerador.validators import FileValidator, CSVValidator  # NOVO: Import dos validadores

routes_bP = Blueprint('main', __name__)

@routes_bP.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Validação do arquivo
        file_validator = FileValidator()
        validation_result = file_validator.validate_upload(request.files.get('file'), allowed_extensions={'csv'})
        
        if not validation_result['is_valid']:
            for error in validation_result['errors']:
                flash(error, 'danger')
            return redirect(request.url)
        
        # Se houver avisos, mostra como warning
        for warning in validation_result['warnings']:
            flash(warning, 'warning')
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Primeiro validar a estrutura do CSV
            csv_validator = CSVValidator()
            csv_validation = csv_validator.validate_conversor_structure(filepath)
            
            if not csv_validation['is_valid']:
                flash(f'Erro na validação do CSV: {csv_validation["errors"][0]}', 'danger')
                return redirect(request.url)
            
            # Processar de acordo com o tipo de conversão determinado
            tipo_conversao = csv_validation['tipo_conversao']
            flash(f'Arquivo validado com sucesso! Tipo de conversão: {tipo_conversao.replace("_", " ")}', 'success')
            
            zip_filename, total_registros, log = processar_csv(filepath, tipo_conversao)
            flash(f'Processamento concluído! {total_registros} registros processados.', 'success')
            
            # ... resto do código ...
            
        except Exception as e:
            flash(f'Erro no processamento: {str(e)}', 'danger')
            return redirect(request.url)
        
        finally:
            # Limpar arquivo temporário
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return render_template('index.html')

@routes_bP.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
        
        # NOVA VALIDAÇÃO: Usar FileValidator
        file_validator = FileValidator()
        validation_result = file_validator.validate_file_exists(file_path)
        
        if not validation_result['is_valid']:
            flash('Arquivo não encontrado', 'danger')
            return redirect(url_for('main.index'))
        
        # Enviar o arquivo para download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
    
    except Exception as e:
        flash(f'Erro ao fazer download: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@routes_bP.route('/sobre')
def sobre():
    return render_template('sobre.html')

@routes_bP.route('/download-modelo-csv')
def download_modelo_csv():
    modelo_path = os.path.join(os.path.dirname(__file__), 'csv_modelo', 'modelo.csv')
    
    # NOVA VALIDAÇÃO: Usar FileValidator
    file_validator = FileValidator()
    validation_result = file_validator.validate_file_exists(modelo_path)
    
    if not validation_result['is_valid']:
        flash('Arquivo modelo não encontrado.', 'danger')
        return redirect(url_for('main.index'))
        
    return send_file(
        modelo_path,
        as_attachment=True,
        download_name='modelo.csv',
        mimetype='text/csv'
    )

@routes_bP.route('/progress')
def progress():
    """Rota para SSE do progresso"""
    def generate():
        try:
            # Envia um ping inicial para manter a conexão
            yield f"data: {json.dumps({'message': 'Conectado...', 'status': 'connected'})}\n\n"
            
            last_data = None
            while True:
                try:
                    # Pega a mensagem mais recente da fila (com timeout)
                    data = MESSAGE_QUEUE.get(timeout=30)
                    
                    # Só envia se os dados mudaram
                    if data != last_data:
                        yield f"data: {json.dumps(data)}\n\n"
                        last_data = data
                        
                        # Se o processamento terminou, encerra a conexão
                        if data.get('status') in ['completed', 'error']:
                            break
                    
                    MESSAGE_QUEUE.task_done()
                    
                except queue.Empty:
                    # Timeout - envia ping para manter conexão
                    yield f"data: {json.dumps({'message': 'Aguardando...', 'status': 'waiting'})}\n\n"
                    
        except GeneratorExit:
            # Cliente desconectou
            print("Cliente desconectou do SSE")
        except Exception as e:
            print(f"Erro no SSE: {e}")
            yield f"data: {json.dumps({'message': f'Erro: {str(e)}', 'status': 'error'})}\n\n"
    
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@routes_bP.route('/validar-csv', methods=['POST'])
def validar_csv():
    print("\n🟢 Iniciando rota /validar-csv", flush=True)

    if 'file' not in request.files:
        print("❌ Nenhum arquivo em request.files", flush=True)
        return jsonify({'valido': False, 'erro': 'Nenhum arquivo enviado'})
    
    file = request.files['file']
    print(f"📁 Recebido arquivo: {file.filename}", flush=True)

    # Validação do arquivo
    file_validator = FileValidator()
    file_validation_result = file_validator.validate_upload(file, allowed_extensions={'csv'})
    
    if not file_validation_result['is_valid']:
        return jsonify({'valido': False, 'erro': file_validation_result['errors'][0]})

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, f"temp_{filename}")
        print(f"💾 Salvando arquivo temporário em: {filepath}", flush=True)
        file.save(filepath)
        
        print("🔍 Iniciando validação de estrutura CSV...", flush=True)
        
        # Validação da estrutura CSV
        csv_validator = CSVValidator()
        separator = request.form.get('separador', '|')
        csv_validation_result = csv_validator.validate_conversor_structure(filepath, separator=separator)
        
        print("✅ Resultado da validação:", csv_validation_result, flush=True)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            print("🧹 Arquivo temporário removido", flush=True)
        
        # Formatar resposta para o frontend
        if csv_validation_result['is_valid']:
            return jsonify({
                'valido': True,
                'total_colunas': csv_validation_result['total_colunas'],
                'colunas_extras': csv_validation_result['colunas_extras'],
                'tipo_conversao': csv_validation_result['tipo_conversao'],
                'complementos_info': csv_validation_result['complementos_info'],
                'total_registros': csv_validation_result['total_registros'],
                'mensagem': f"Arquivo válido! Será gerado com {csv_validation_result['tipo_conversao'].replace('_', ' ')}"
            })
        else:
            return jsonify({
                'valido': False,
                'erro': csv_validation_result['errors'][0] if csv_validation_result['errors'] else 'Estrutura CSV inválida',
                'colunas_faltantes': csv_validation_result['colunas_faltantes'],
                'colunas_encontradas': csv_validation_result['colunas_encontradas']
            })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        if os.path.exists(filepath):
            os.remove(filepath)
        print(f"❌ Erro na validação: {str(e)}", flush=True)
        return jsonify({'valido': False, 'erro': f'Erro na validação: {str(e)}'})
    
@routes_bP.route('/conversor-csv', methods=['GET', 'POST'])
def conversor_csv():
    if request.method == 'POST':
        # NOVA VALIDAÇÃO: Usar FileValidator
        file_validator = FileValidator()
        validation_result = file_validator.validate_upload(request.files.get('file'), allowed_extensions={'csv'})
        
        if not validation_result['is_valid']:
            for error in validation_result['errors']:
                flash(error, 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Reset progress data
        update_progress('🕒 Iniciando processamento...', progress=0, current=0, total=0, status='processing')
        
        try:
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            
            # Limpar a fila de mensagens antigas
            while not MESSAGE_QUEUE.empty():
                try:
                    MESSAGE_QUEUE.get_nowait()
                    MESSAGE_QUEUE.task_done()
                except queue.Empty:
                    break
            
            # Gerar um ID único para este processamento
            import uuid
            process_id = str(uuid.uuid4())
            
            # Iniciar processamento em thread separada
            def processar_arquivo(process_id, filepath, file_size):
                try:
                    update_progress(f'📊 Arquivo validado: {file_size:.2f} MB', progress=5)
                    
                    if file_size > 100:
                        update_progress('🔧 Usando processamento otimizado para arquivo grande...', progress=10)
                        zip_filename, total_registros = processar_conversor_csv_grande(filepath)
                    else:
                        update_progress('🔧 Processando arquivo...', progress=10)
                        zip_filename, total_registros = processar_conversor_csv(filepath)
                    
                    # Armazenar resultado no dicionário global
                    with RESULTS_LOCK:
                        PROCESSING_RESULTS[process_id] = {
                            'filename': zip_filename,
                            'total_registros': total_registros,
                            'status': 'success'
                        }
                    
                    update_progress('✅ Processamento concluído com sucesso!', progress=100, status='completed')
                    
                except Exception as e:
                    error_msg = f'❌ Erro no processamento: {str(e)}'
                    print(error_msg)
                    
                    # Armazenar erro no dicionário global
                    with RESULTS_LOCK:
                        PROCESSING_RESULTS[process_id] = {
                            'error': str(e),
                            'status': 'error'
                        }
                    
                    update_progress(error_msg, status='error')
                finally:
                    # Limpar arquivo temporário
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            thread = threading.Thread(target=processar_arquivo, args=(process_id, filepath, file_size))
            thread.daemon = True
            thread.start()
            
            # Armazenar o process_id na session para recuperar depois
            session['current_process_id'] = process_id
            
            return redirect(url_for('main.progress_page'))
            
        except Exception as e:
            flash(f'❌ Erro ao iniciar processamento: {str(e)}', 'danger')
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(request.url)
    
    return render_template('conversor_csv.html')

@routes_bP.route('/progress-page')
def progress_page():
    """Página que mostra o progresso"""
    return render_template('progresso.html')

@routes_bP.route('/conversor-result')
def conversor_result():
    """Página de resultado após processamento"""
    process_id = session.get('current_process_id')
    
    if not process_id:
        flash('Nenhum processamento em andamento', 'warning')
        return redirect(url_for('main.conversor_csv'))
    
    with RESULTS_LOCK:
        result = PROCESSING_RESULTS.get(process_id)
    
    if not result:
        flash('Resultado não encontrado. O processamento pode ainda estar em andamento.', 'warning')
        return redirect(url_for('main.conversor_csv'))
    
    if result.get('status') == 'success':
        # Limpar o resultado após usar
        with RESULTS_LOCK:
            PROCESSING_RESULTS.pop(process_id, None)
        session.pop('current_process_id', None)
        
        return render_template('resultado_conversor.html', 
                            total_registros=result['total_registros'],
                            zip_filename=result['filename'])
    
    elif result.get('status') == 'error':
        error_msg = result.get('error', 'Erro desconhecido')
        # Limpar o resultado após usar
        with RESULTS_LOCK:
            PROCESSING_RESULTS.pop(process_id, None)
        session.pop('current_process_id', None)
        
        flash(f'❌ Erro na conversão: {error_msg}', 'danger')
        return redirect(url_for('main.conversor_csv'))
    
    else:
        flash('Processamento ainda em andamento...', 'info')
        return redirect(url_for('main.progress_page'))

@routes_bP.route('/download-convertido/<filename>')
def download_convertido(filename):
    try:
        file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
        
        # NOVA VALIDAÇÃO: Usar FileValidator
        file_validator = FileValidator()
        validation_result = file_validator.validate_file_exists(file_path)
        
        if not validation_result['is_valid']:
            flash('Arquivo não encontrado', 'danger')
            return redirect(url_for('main.conversor_csv'))
        
        # Enviar o arquivo para download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    
    except Exception as e:
        flash(f'Erro ao fazer download: {str(e)}', 'danger')
        return redirect(url_for('main.conversor_csv'))

# Adicionar tratamento de erro para arquivos grandes
@routes_bP.errorhandler(413)
def too_large(e):
    flash('O arquivo é muito grande. O tamanho máximo permitido é 2GB.', 'danger')
    return redirect(request.url)