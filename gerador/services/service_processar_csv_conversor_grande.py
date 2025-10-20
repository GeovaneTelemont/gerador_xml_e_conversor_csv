import pandas as pd
from datetime import datetime
from ..utils import update_progress, carregar_roteiros, processar_enderecos_otimizado
from ..config import Config
import os


def processar_csv_conversor_grande(arquivo_path):
    """Processa o arquivo CSV para conversão - OTIMIZADO PARA ARQUIVOS GRANDES"""
    try:
        update_progress("📂 Iniciando carregamento do arquivo...", progress=5, status='processing')
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(arquivo_path) / (1024 * 1024)  # Tamanho em MB
        update_progress(f"📊 Tamanho do arquivo: {file_size:.2f} MB", progress=10)
        
        # Carrega os roteiros primeiro (uma vez só)
        update_progress("📁 Carregando arquivos de roteiro...", progress=15)
        df_roteiro_aparecida, df_roteiro_goiania = carregar_roteiros()
        if df_roteiro_aparecida is None or df_roteiro_goiania is None:
            raise Exception("Erro ao carregar arquivos de roteiro. Verifique se os arquivos estão na pasta 'roteiros'.")
        
        update_progress("✅ Roteiros carregados com sucesso", progress=20)

        # Processamento em chunks para arquivos grandes
        chunk_size = 50000  # Ajuste conforme a memória disponível
        chunks_processed = 0
        total_rows = 0
        
        # Primeiro passagem: contar linhas totais
        update_progress("🔢 Contando linhas totais...", progress=25)
        with open(arquivo_path, 'r', encoding='latin-1') as f:
            total_rows = sum(1 for line in f) - 1  # -1 para o cabeçalho
        
        update_progress(f"📊 Total de linhas encontradas: {total_rows:,}", progress=30, total=total_rows)
        
        # Lista para armazenar chunks processados
        chunks_processados = []
        
        # Processar em chunks
        update_progress("🔄 Iniciando processamento em chunks...", progress=35)
        
        for chunk_number, chunk in enumerate(pd.read_csv(arquivo_path, 
                                encoding='latin-1',
                                sep='|',
                                chunksize=chunk_size,
                                low_memory=False), 1):
            
            chunks_processed += 1
            current_row = chunk_number * chunk_size
            if current_row > total_rows:
                current_row = total_rows
                
            progress_percent = 35 + (chunk_number * 55 / (total_rows / chunk_size))
            progress_percent = min(progress_percent, 90)
            
            update_progress(
                f"📦 Processando chunk {chunk_number} ({len(chunk):,} linhas)...", 
                progress=progress_percent,
                current=current_row
            )
            
            # Processa o chunk
            chunk_processado = processar_enderecos_otimizado(chunk, df_roteiro_aparecida, df_roteiro_goiania)
            chunks_processados.append(chunk_processado)
            
            # Limpar memória
            del chunk
            del chunk_processado
            
            update_progress(f"✅ Chunk {chunk_number} processado", progress=progress_percent)
        
        # Combinar todos os chunks
        update_progress("🔗 Combinando chunks processados...", progress=92)
        df_final = pd.concat(chunks_processados, ignore_index=True)
        
        # Gera nome do arquivo
        nome_arquivo = f"Enderecos_Totais_CO_Convertido_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        caminho_arquivo = os.path.join(Config.DOWNLOAD_FOLDER, nome_arquivo)
        
        # Salva o arquivo em chunks também (para evitar problemas de memória)
        update_progress("💾 Salvando arquivo final...", progress=95)
        df_final.to_csv(
            caminho_arquivo,
            index=False,
            encoding='utf-8-sig',
            sep=';',
            quoting=1,
            quotechar='"',
            na_rep='',
            chunksize=10000  # Salva em chunks também
        )
        
        update_progress(
            f"✅ Conversão concluída! Arquivo salvo: {nome_arquivo}", 
            progress=100, 
            current=total_rows,
            status='completed'
        )
        
        print(f"✅ Arquivo convertido salvo: {nome_arquivo}")
        print(f"📊 Total processado: {len(df_final):,} linhas")
        
        return nome_arquivo, len(df_final)
        
    except Exception as e:
        error_msg = f"❌ Erro no processamento: {str(e)}"
        update_progress(error_msg, status='error')
        print(error_msg)
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        raise Exception(f"Erro ao processar arquivo: {str(e)}")