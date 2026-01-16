"""
Gráfico 7: Box Plot com Outliers - Análise de Variabilidade
Referência: Análise estatística robusta em estudos empíricos (Kitchenham et al., 2002)

O box plot permite:
- Identificar outliers de performance (cenários anômalos)
- Comparar medianas e IQR entre ferramentas
- Avaliar a dispersão e consistência das ferramentas
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

def create_boxplot():
    reports = load_reports()
    
    # Extrair dados
    data = []
    for tool_name, report in reports.items():
        for scenario in report.get('scenarios', []):
            scenario_num = int(scenario['scenario_id'].replace('scenario_', ''))
            data.append({
                'tool': tool_name,
                'scenario': scenario['scenario_id'],
                'scenario_num': scenario_num,
                'f1_score': scenario['metrics']['f1_score'],
                'files_generated': scenario['files']['total_actual'],
                'files_expected': scenario['files']['total_expected'],
                'overflow_ratio': scenario['files']['total_actual'] / max(scenario['files']['total_expected'], 1)
            })
    
    df = pd.DataFrame(data)
    
    # Criar figura com múltiplos aspectos
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    colors = {'FSTMerge': '#2ecc71', 'IntelliMerge': '#3498db', 'JDime': '#e74c3c'}
    
    # 1. Box plot de F1-Score
    ax1 = axes[0, 0]
    box1 = sns.boxplot(data=df, x='tool', y='f1_score', hue='tool', palette=colors, legend=False, ax=ax1)
    sns.stripplot(data=df, x='tool', y='f1_score', color='black', alpha=0.4, size=5, ax=ax1)
    ax1.set_title('Distribuição de F1-Score\n', fontsize=12, fontweight='bold')
    ax1.set_xlabel('')
    ax1.set_ylabel('F1-Score')
    ax1.axhline(y=df['f1_score'].median(), color='red', linestyle='--', alpha=0.5, label='Mediana Geral')
    ax1.legend()
    
    # Anotar outliers
    for tool in df['tool'].unique():
        tool_data = df[df['tool'] == tool]
        Q1 = tool_data['f1_score'].quantile(0.25)
        Q3 = tool_data['f1_score'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = tool_data[(tool_data['f1_score'] < Q1 - 1.5*IQR) | (tool_data['f1_score'] > Q3 + 1.5*IQR)]
        
        for _, row in outliers.iterrows():
            ax1.annotate(row['scenario'].replace('scenario_', 'C'),
                        (list(df['tool'].unique()).index(tool), row['f1_score']),
                        xytext=(5, 0), textcoords='offset points',
                        fontsize=8, alpha=0.7)
    
    # 2. Box plot de arquivos gerados vs esperados
    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='tool', y='overflow_ratio', hue='tool', palette=colors, legend=False, ax=ax2)
    ax2.set_title('Razão: Arquivos Gerados / Esperados\n(Overflow de Arquivos)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('')
    ax2.set_ylabel('Razão (Gerados/Esperados)')
    ax2.axhline(y=1, color='green', linestyle='--', alpha=0.7, label='Ideal (1:1)')
    ax2.set_yscale('log')
    ax2.legend()
    
    # 3. Comparação de métricas por quartil de complexidade
    ax3 = axes[1, 0]
    # Usar categorias customizadas baseadas nos valores reais
    df['complexity_cat'] = df['files_expected'].apply(
        lambda x: 'Simples\n(1 arq)' if x == 1 else ('Médio\n(2 arqs)' if x == 2 else 'Complexo\n(3+ arqs)')
    )
    
    sns.boxplot(data=df, x='complexity_cat', y='f1_score', hue='tool', palette=colors, ax=ax3)
    ax3.set_title('F1-Score por Categoria de Complexidade\n', fontsize=12, fontweight='bold')
    ax3.set_xlabel('\nCategoria de Complexidade')
    ax3.set_ylabel('F1-Score')
    ax3.legend(title='Ferramenta', loc='lower left')
    
    # 4. Análise temporal/sequencial dos cenários
    ax4 = axes[1, 1]
    for tool in ['FSTMerge', 'IntelliMerge', 'JDime']:
        tool_data = df[df['tool'] == tool].sort_values('scenario_num')
        ax4.plot(tool_data['scenario_num'], tool_data['f1_score'], 
                 'o-', color=colors[tool], label=tool, alpha=0.7, markersize=4)
    
    ax4.set_title('F1-Score por Sequência de Cenário\n', fontsize=12, fontweight='bold')
    ax4.set_xlabel('\nNúmero do Cenário')
    ax4.set_ylabel('F1-Score')
    ax4.legend(title='Ferramenta')
    ax4.set_xlim(0, 40)
    ax4.set_ylim(-0.1, 1.1)
    
    # Adicionar áreas de cenários problemáticos
    ax4.axvspan(1, 12, alpha=0.1, color='red', label='Grupo 1-12')
    ax4.axvspan(34, 39, alpha=0.1, color='orange', label='Grupo 34-39')
    
    # Título geral
    fig.suptitle('Análise de Variabilidade e Outliers nas Ferramentas de Merge\n', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "07_boxplot_variability.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "07_boxplot_variability.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Box plot salvo em: {output_path}")
    
    plt.close()
    
    # Estatísticas de outliers
    print("\nAnálise de Outliers por Ferramenta:")
    print("=" * 60)
    for tool in ['FSTMerge', 'IntelliMerge', 'JDime']:
        tool_data = df[df['tool'] == tool]
        Q1 = tool_data['f1_score'].quantile(0.25)
        Q3 = tool_data['f1_score'].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = tool_data[(tool_data['f1_score'] < lower_bound) | (tool_data['f1_score'] > upper_bound)]
        
        print(f"\n{tool}:")
        print(f"  Q1: {Q1:.3f}, Q3: {Q3:.3f}, IQR: {IQR:.3f}")
        print(f"  Limites: [{lower_bound:.3f}, {upper_bound:.3f}]")
        print(f"  Outliers: {len(outliers)} cenários")
        if len(outliers) > 0:
            print(f"  Cenários: {list(outliers['scenario'])}")
    
    return df

if __name__ == "__main__":
    print("Gerando Box Plot de Variabilidade...")
    df = create_boxplot()
