"""
Gráfico 2: Scatter Plot - Complexidade vs. Taxa de Sucesso
Referência: Mens (2002) - "A State-of-the-Art Survey on Software Merging"

Este scatter plot revela:
- Correlação entre número de arquivos esperados e qualidade do merge
- Identificação de outliers de performance
- Comparação de robustez entre ferramentas com diferentes complexidades
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats

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

def create_scatter_plot():
    reports = load_reports()
    
    # Extrair dados
    data = []
    for tool_name, report in reports.items():
        for scenario in report.get('scenarios', []):
            data.append({
                'tool': tool_name,
                'scenario': scenario['scenario_id'],
                'complexity': scenario['files']['total_expected'],
                'f1_score': scenario['metrics']['f1_score'],
                'files_generated': scenario['files']['total_actual'],
                'quality': scenario['scenario_quality'],
                'extra_files': len(scenario['files'].get('extra', []))
            })
    
    df = pd.DataFrame(data)
    
    # Configurar cores e marcadores
    colors = {'FSTMerge': '#2ecc71', 'IntelliMerge': '#3498db', 'JDime': '#e74c3c'}
    markers = {'FSTMerge': 'o', 'IntelliMerge': 's', 'JDime': '^'}
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plotar cada ferramenta
    for tool in ['FSTMerge', 'IntelliMerge', 'JDime']:
        tool_data = df[df['tool'] == tool]
        
        # Adicionar jitter para melhor visualização
        jitter_x = np.random.normal(0, 0.1, len(tool_data))
        jitter_y = np.random.normal(0, 0.02, len(tool_data))
        
        scatter = ax.scatter(
            tool_data['complexity'] + jitter_x,
            tool_data['f1_score'] + jitter_y,
            c=colors[tool],
            marker=markers[tool],
            s=tool_data['files_generated'].clip(upper=100) * 3 + 50,  # Tamanho proporcional
            alpha=0.7,
            label=f'{tool} (n={len(tool_data)})',
            edgecolors='white',
            linewidth=0.5
        )
    
    # Adicionar linha de tendência geral
    z = np.polyfit(df['complexity'], df['f1_score'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df['complexity'].min(), df['complexity'].max(), 100)
    ax.plot(x_line, p(x_line), '--', color='gray', alpha=0.8, 
            label=f'Tendência (r={stats.pearsonr(df["complexity"], df["f1_score"])[0]:.3f})')
    
    # Configurações do gráfico
    ax.set_xlabel('Complexidade (Número de Arquivos Esperados)', fontsize=12)
    ax.set_ylabel('F1-Score', fontsize=12)
    ax.set_title('Relação entre Complexidade do Cenário e Qualidade do Merge\n', 
                 fontsize=14, fontweight='bold')
    
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlim(0, df['complexity'].max() + 1)
    
    # Áreas de referência
    ax.axhspan(0.8, 1.0, alpha=0.1, color='green', label='Zona de Alta Qualidade')
    ax.axhspan(0.0, 0.3, alpha=0.1, color='red', label='Zona de Falha')
    
    # Legenda
    ax.legend(loc='upper right', frameon=True, framealpha=0.9)
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    # Anotações para outliers notáveis
    outliers = df[(df['files_generated'] > 70) & (df['f1_score'] > 0.5)]
    for _, row in outliers.iterrows():
        ax.annotate(row['scenario'].replace('scenario_', 'C'),
                   (row['complexity'], row['f1_score']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.7)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "02_scatter_complexity_vs_quality.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "02_scatter_complexity_vs_quality.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Scatter plot salvo em: {output_path}")
    
    plt.close()
    
    # Calcular correlação
    print("\nCorrelação Pearson (Complexidade vs F1-Score):")
    for tool in ['FSTMerge', 'IntelliMerge', 'JDime']:
        tool_data = df[df['tool'] == tool]
        if len(tool_data) > 2:
            corr, pval = stats.pearsonr(tool_data['complexity'], tool_data['f1_score'])
            print(f"  {tool}: r={corr:.3f}, p={pval:.4f}")
    
    return df

if __name__ == "__main__":
    print("Gerando Scatter Plot de Complexidade vs Qualidade...")
    df = create_scatter_plot()
