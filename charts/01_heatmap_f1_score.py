"""
Gráfico 1: Heatmap de Qualidade por Cenário e Ferramenta
Referência: Cavalcanti et al. (2017) - "Understanding Semi-structured Merge Conflict Characteristics"

Este heatmap permite identificar visualmente:
- Padrões de sucesso/falha por faixas de cenário
- Clusters de problemas específicos de cada ferramenta
- Comparação direta entre ferramentas no mesmo cenário
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuração
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

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

def create_heatmap():
    reports = load_reports()
    
    # Criar matriz de F1-scores
    scenarios = [f"scenario_{i}" for i in range(1, 40)]
    tools = ['FSTMerge', 'IntelliMerge', 'JDime']
    
    # Matriz para F1-score
    f1_matrix = np.zeros((len(scenarios), len(tools)))
    f1_matrix[:] = np.nan
    
    for j, tool in enumerate(tools):
        if tool in reports:
            for scenario in reports[tool].get('scenarios', []):
                try:
                    idx = scenarios.index(scenario['scenario_id'])
                    f1_matrix[idx, j] = scenario['metrics']['f1_score']
                except (ValueError, KeyError):
                    continue
    
    # Criar DataFrame
    df = pd.DataFrame(f1_matrix, index=scenarios, columns=tools)
    
    # Plotar heatmap
    fig, ax = plt.subplots(figsize=(10, 16))
    
    # Máscara para valores NaN
    mask = df.isnull()
    
    # Heatmap com anotações
    sns.heatmap(df, 
                annot=True, 
                fmt='.2f',
                cmap='RdYlGn',
                vmin=0, 
                vmax=1,
                mask=mask,
                cbar_kws={'label': 'F1-Score', 'shrink': 0.5},
                linewidths=0.5,
                linecolor='white',
                ax=ax)
    
    ax.set_title('Heatmap de F1-Score por Cenário e Ferramenta de Merge\n', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('\nFerramenta de Merge', fontsize=12)
    ax.set_ylabel('Cenário\n', fontsize=12)
    
    # Adicionar linha divisória entre grupos de cenários
    for y in [12, 23, 33]:  # Divisões baseadas em padrões observados
        ax.axhline(y=y, color='black', linewidth=2, linestyle='--', alpha=0.5)
    
    # Rotação dos labels
    plt.xticks(rotation=0)
    plt.yticks(rotation=0, fontsize=9)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "01_heatmap_f1_score.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "01_heatmap_f1_score.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Heatmap salvo em: {output_path}")
    
    plt.close()
    
    return df

if __name__ == "__main__":
    print("Gerando Heatmap de F1-Score...")
    df = create_heatmap()
    print("\nResumo estatístico por ferramenta:")
    print(df.describe())
