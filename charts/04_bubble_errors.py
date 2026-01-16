"""
Gráfico 4: Bubble Chart - Análise de Erros por Frequência e Impacto
Referência: Bourque & Fairley (2014) - SWEBOK Guide

O bubble chart visualiza três dimensões simultaneamente:
- Tipo de erro (posição X)
- Impacto no F1-Score médio (posição Y)  
- Frequência de ocorrência (tamanho da bolha)
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict

# Configuração
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'

BASE_PATH = Path(__file__).parent.parent
RESULTS_PATH = BASE_PATH / "evaluation_results"
CHARTS_PATH = BASE_PATH / "charts"

def load_reports():
    tools = ['FSTMerge', 'IntelliMerge', 'JDime']
    reports = {}
    for tool in tools:
        report_path = RESULTS_PATH / tool / "report.json"
        if report_path.exists():
            with open(report_path, 'r') as f:
                reports[tool] = json.load(f)
    return reports

def create_bubble_chart():
    reports = load_reports()
    
    # Analisar erros de cada ferramenta
    error_analysis = []
    
    for tool_name, report in reports.items():
        error_counts = defaultdict(int)
        error_f1_sum = defaultdict(float)
        error_f1_count = defaultdict(int)
        
        for scenario in report.get('scenarios', []):
            f1 = scenario['metrics']['f1_score']
            
            for file_eval in scenario.get('file_evaluations', []):
                for error in file_eval.get('errors', []):
                    error_counts[error] += 1
                    error_f1_sum[error] += f1
                    error_f1_count[error] += 1
        
        for error_type, count in error_counts.items():
            avg_f1 = error_f1_sum[error_type] / error_f1_count[error_type] if error_f1_count[error_type] > 0 else 0
            error_analysis.append({
                'tool': tool_name,
                'error_type': error_type,
                'frequency': count,
                'avg_f1_when_present': avg_f1,
                'impact': 1 - avg_f1  # Impacto = quanto menor o F1, maior o impacto
            })
    
    df = pd.DataFrame(error_analysis)
    
    if df.empty:
        print("Não há dados de erro para plotar")
        return None
    
    # Mapear erros para categorias mais legíveis
    error_labels = {
        'missing_file': 'Arquivo\nFaltando',
        'missing_files': 'Arquivos\nFaltando',
        'extra_file': 'Arquivo\nExtra',
        'extra_files': 'Arquivos\nExtras',
        'missing_class': 'Classe\nFaltando',
        'unresolved_conflicts': 'Conflitos\nNão Resolvidos',
        'unbalanced_braces': 'Chaves\nDesbalanceadas',
        'syntax_error': 'Erro de\nSintaxe'
    }
    
    df['error_label'] = df['error_type'].map(lambda x: error_labels.get(x, x))
    
    # Agregar por tipo de erro (somando todas as ferramentas)
    df_agg = df.groupby('error_type').agg({
        'frequency': 'sum',
        'impact': 'mean',
        'error_label': 'first'
    }).reset_index()
    
    # Criar figura com dois subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Subplot 1: Bubble por ferramenta
    ax1 = axes[0]
    colors = {'FSTMerge': '#2ecc71', 'IntelliMerge': '#3498db', 'JDime': '#e74c3c'}
    
    for i, tool in enumerate(['FSTMerge', 'IntelliMerge', 'JDime']):
        tool_df = df[df['tool'] == tool]
        if not tool_df.empty:
            # Posição X baseada no erro + offset por ferramenta
            x_positions = np.arange(len(tool_df)) + i * 0.25
            
            scatter = ax1.scatter(
                tool_df['error_label'],
                tool_df['impact'],
                s=tool_df['frequency'] * 15 + 100,  # Tamanho proporcional à frequência
                c=colors[tool],
                alpha=0.6,
                label=tool,
                edgecolors='white',
                linewidth=1
            )
    
    ax1.set_xlabel('\nTipo de Erro', fontsize=12)
    ax1.set_ylabel('Impacto (1 - F1-Score)\n', fontsize=12)
    ax1.set_title('Frequência e Impacto de Erros por Ferramenta\n', fontsize=14, fontweight='bold')
    ax1.legend(title='Ferramenta', loc='upper right')
    ax1.tick_params(axis='x', rotation=45)
    ax1.set_ylim(-0.1, 1.1)
    
    # Subplot 2: Bubble agregado (todas as ferramentas)
    ax2 = axes[1]
    
    scatter = ax2.scatter(
        df_agg['error_label'],
        df_agg['impact'],
        s=df_agg['frequency'] * 8 + 200,
        c=df_agg['impact'],
        cmap='RdYlGn_r',
        alpha=0.7,
        edgecolors='black',
        linewidth=1
    )
    
    # Adicionar labels de frequência
    for _, row in df_agg.iterrows():
        ax2.annotate(f"n={int(row['frequency'])}", 
                    (row['error_label'], row['impact']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=9,
                    fontweight='bold')
    
    ax2.set_xlabel('\nTipo de Erro', fontsize=12)
    ax2.set_ylabel('Impacto Médio (1 - F1-Score)\n', fontsize=12)
    ax2.set_title('Impacto Agregado dos Erros\n(Tamanho = Frequência Total)\n', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.set_ylim(-0.1, 1.1)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax2, shrink=0.8)
    cbar.set_label('Severidade do Impacto', fontsize=10)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "04_bubble_error_analysis.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "04_bubble_error_analysis.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Bubble chart salvo em: {output_path}")
    
    plt.close()
    
    # Imprimir resumo
    print("\nAnálise de Erros Agregada:")
    print("-" * 50)
    print(df_agg[['error_type', 'frequency', 'impact']].sort_values('frequency', ascending=False).to_string(index=False))
    
    return df

if __name__ == "__main__":
    print("Gerando Bubble Chart de Análise de Erros...")
    df = create_bubble_chart()
