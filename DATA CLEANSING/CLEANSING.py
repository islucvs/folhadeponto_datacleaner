import pandas as pd
import os
from datetime import datetime

def enriquecer_arquivo_csv(arquivo_original, arquivo_novos_dados, arquivo_saida=None):
    """
    Insere novos dados de um arquivo CSV em outro arquivo CSV, mantendo a ordenação pela coluna 'Dia'
    
    Args:
        arquivo_original (str): Caminho do arquivo Y (base original)
        arquivo_novos_dados (str): Caminho do arquivo X (novos dados)
        arquivo_saida (str): Caminho do arquivo de saída (opcional)
    """
    
    try:
        # Ler os arquivos CSV
        print(f"Lendo arquivo original: {arquivo_original}")
        df_original = pd.read_csv(arquivo_original)
        
        print(f"Lendo arquivo com novos dados: {arquivo_novos_dados}")
        df_novos = pd.read_csv(arquivo_novos_dados)
        
        # Verificar se as colunas são compatíveis
        if list(df_original.columns) != list(df_novos.columns):
            print("Aviso: As colunas dos arquivos não são idênticas!")
            print(f"Colunas do original: {list(df_original.columns)}")
            print(f"Colunas dos novos dados: {list(df_novos.columns)}")
            return
        
        # Concatenar os dataframes
        df_combinado = pd.concat([df_original, df_novos], ignore_index=True)
        
        # Converter a coluna 'Dia' para datetime para ordenação correta
        df_combinado['Dia'] = pd.to_datetime(df_combinado['Dia'], format='%d%m%Y', errors='coerce')
        
        # Ordenar pelo campo 'Dia'
        df_combinado = df_combinado.sort_values('Dia')
        
        # Converter a coluna 'Dia' de volta para o formato original (DDMMYYYY)
        df_combinado['Dia'] = df_combinado['Dia'].dt.strftime('%d%m%Y')
        
        # Determinar o arquivo de saída
        if arquivo_saida is None:
            arquivo_saida = arquivo_original
        
        # Salvar o resultado
        df_combinado.to_csv(arquivo_saida, index=False)
        
        print(f"Arquivo atualizado com sucesso: {arquivo_saida}")
        print(f"Registros originais: {len(df_original)}")
        print(f"Novos registros: {len(df_novos)}")
        print(f"Total de registros: {len(df_combinado)}")
        
    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado - {e}")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")

def enriquecer_arquivo_csv_com_verificacao(arquivo_original, arquivo_novos_dados, arquivo_saida=None):
    """
    Versão alternativa que verifica por duplicatas antes de inserir
    """
    
    try:
        # Ler os arquivos CSV
        df_original = pd.read_csv(arquivo_original)
        df_novos = pd.read_csv(arquivo_novos_dados)
        
        # Verificar compatibilidade de colunas
        if list(df_original.columns) != list(df_novos.columns):
            print("Erro: As colunas dos arquivos não são compatíveis!")
            return
        
        # Converter para string para comparação
        df_original_str = df_original.astype(str)
        df_novos_str = df_novos.astype(str)
        
        # Encontrar registros duplicados
        duplicatas = pd.merge(df_original_str, df_novos_str, how='inner')
        
        if len(duplicatas) > 0:
            print(f"Aviso: {len(duplicatas)} registros duplicados encontrados. Serão ignorados.")
            # Remover duplicatas dos novos dados
            df_novos_sem_duplicatas = pd.concat([df_original_str, df_novos_str]).drop_duplicates(keep=False)
            # Filtrar apenas os registros que estão no arquivo de novos dados originais
            mask = df_novos_str.apply(tuple, 1).isin(df_novos_sem_duplicatas.apply(tuple, 1))
            df_novos = df_novos[mask]
        
        # Concatenar e ordenar
        df_combinado = pd.concat([df_original, df_novos], ignore_index=True)
        df_combinado['Dia'] = pd.to_datetime(df_combinado['Dia'], format='%d%m%Y', errors='coerce')
        df_combinado = df_combinado.sort_values('Dia')
        df_combinado['Dia'] = df_combinado['Dia'].dt.strftime('%d%m%Y')
        
        # Salvar
        if arquivo_saida is None:
            arquivo_saida = arquivo_original
        
        df_combinado.to_csv(arquivo_saida, index=False)
        
        print(f"Processamento concluído!")
        print(f"Registros originais: {len(df_original)}")
        print(f"Novos registros adicionados: {len(df_novos)}")
        print(f"Total no arquivo final: {len(df_combinado)}")
        
    except Exception as e:
        print(f"Erro: {e}")

# Exemplo de uso
if __name__ == "__main__":
    # Configurar os caminhos dos arquivos
    arquivo_Y = "arquivo_original.csv"  # Seu arquivo base
    arquivo_X = "novos_dados.csv"       # Arquivo com novos dados
    arquivo_resultado = "arquivo_atualizado.csv"  # Arquivo de saída (opcional)
    
    # Usar a função básica
    print("=== Método Básico ===")
    enriquecer_arquivo_csv(arquivo_Y, arquivo_X, arquivo_resultado)
    
    print("\n=== Método com Verificação de Duplicatas ===")
    # Ou usar a versão com verificação de duplicatas
    enriquecer_arquivo_csv_com_verificacao(arquivo_Y, arquivo_X, arquivo_resultado)