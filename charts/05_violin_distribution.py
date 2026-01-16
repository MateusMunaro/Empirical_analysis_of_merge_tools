"""
Gráfico 5: Violin Plot - Distribuição de Métricas por Qualidade
Referência: Estudos estatísticos em Engenharia de Software (Shaw, 2002)

O violin plot combina:
- Box plot (mediana, quartis, outliers)
- Kernel density estimation (distribuição)
- Comparação entre grupos de qualidade
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

def create_violin_plot():
    reports = load_reports()
    
    # Extrair dados
    data = []
    for tool_name, report in reports.items():
        for scenario in report.get('scenarios', []):
            data.append({
                'tool': tool_name,
                'scenario': scenario['scenario_id'],
                'quality': scenario['scenario_quality'],
                'precision': scenario['metrics']['precision'],
                'recall': scenario['metrics']['recall'],
                'f1_score': scenario['metrics']['f1_score'],
                'accuracy': scenario['metrics']['accuracy']
            })
    
    df = pd.DataFrame(data)
    
    # Ordenar qualidade
    quality_order = ['perfect', 'excellent', 'good', 'acceptable', 'poor', 'failed']
    df['quality'] = pd.Categorical(df['quality'], categories=quality_order, ordered=True)
    
    # Criar figura com subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    metrics = ['precision', 'recall', 'f1_score', 'accuracy']
    titles = ['Precision', 'Recall', 'F1-Score', 'Accuracy']
    
    palette = {'FSTMerge': '#2ecc71', 'IntelliMerge': '#3498db', 'JDime': '#e74c3c'}
    
    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 2, idx % 2]
        
        # Violin plot
        sns.violinplot(
            data=df,
            x='tool',
            y=metric,
            hue='tool',
            palette=palette,
            inner='box',
            ax=ax,
            legend=False
        )
        
        # Adicionar pontos individuais
        sns.stripplot(
            data=df,
            x='tool',
            y=metric,
            color='black',
            alpha=0.3,
            size=4,
            ax=ax
        )
        
        ax.set_title(f'Distribuição de {title} por Ferramenta\n', fontsize=12, fontweight='bold')
        ax.set_xlabel('')
        ax.set_ylabel(title, fontsize=11)
        ax.set_ylim(-0.1, 1.1)
        
        # Adicionar linhas de referência
        ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Limiar de Alta Qualidade')
        ax.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Limiar Mediano')
    
    # Título geral
    fig.suptitle('Distribuição das Métricas de Avaliação por Ferramenta de Merge\n', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "05_violin_metrics_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "05_violin_metrics_distribution.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Violin plot salvo em: {output_path}")
    
    plt.close()
    
    # Estatísticas descritivas
    print("\nEstatísticas Descritivas por Ferramenta:")
    print("=" * 70)
    for tool in ['FSTMerge', 'IntelliMerge', 'JDime']:
        tool_df = df[df['tool'] == tool]
        print(f"\n{tool}:")
        print(tool_df[['precision', 'recall', 'f1_score', 'accuracy']].describe().round(3))
    
    return df

if __name__ == "__main__":
    print("Gerando Violin Plot de Distribuição de Métricas...")
    df = create_violin_plot()
