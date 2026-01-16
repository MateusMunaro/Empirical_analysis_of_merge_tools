"""
Gráfico 6: Stacked Bar - Composição de Qualidade por Faixa de Complexidade
Referência: Estudos de categorização em análise de software merge (Accioly et al., 2018)

Este gráfico mostra:
- Como a complexidade afeta a distribuição de qualidade
- Proporção de sucessos/falhas por categoria de complexidade
- Comparação entre ferramentas em diferentes níveis de dificuldade
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

def create_stacked_bar():
    reports = load_reports()
    
    # Extrair dados
    data = []
    for tool_name, report in reports.items():
        for scenario in report.get('scenarios', []):
            expected = scenario['files']['total_expected']
            
            # Categorizar complexidade
            if expected == 1:
                complexity_cat = '1 arquivo'
            elif expected <= 2:
                complexity_cat = '2 arquivos'
            elif expected <= 3:
                complexity_cat = '3 arquivos'
            else:
                complexity_cat = '4+ arquivos'
            
            # Simplificar qualidade
            quality = scenario['scenario_quality']
            if quality in ['perfect', 'excellent']:
                quality_simple = 'Perfeito/Excelente'
            elif quality in ['good', 'acceptable']:
                quality_simple = 'Bom/Aceitável'
            elif quality == 'poor':
                quality_simple = 'Ruim'
            else:
                quality_simple = 'Falhou'
            
            data.append({
                'tool': tool_name,
                'complexity': complexity_cat,
                'quality': quality_simple,
                'quality_original': quality
            })
    
    df = pd.DataFrame(data)
    
    # Ordenar categorias
    complexity_order = ['1 arquivo', '2 arquivos', '3 arquivos', '4+ arquivos']
    quality_order = ['Perfeito/Excelente', 'Bom/Aceitável', 'Ruim', 'Falhou']
    
    # Cores para qualidade
    colors = {
        'Perfeito/Excelente': '#27ae60',
        'Bom/Aceitável': '#f1c40f',
        'Ruim': '#e67e22',
        'Falhou': '#c0392b'
    }
    
    # Criar figura
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    
    tools = ['FSTMerge', 'IntelliMerge', 'JDime']
    
    for ax, tool in zip(axes, tools):
        tool_df = df[df['tool'] == tool]
        
        # Pivot para stacked bar
        pivot = tool_df.groupby(['complexity', 'quality']).size().unstack(fill_value=0)
        
        # Reordenar
        pivot = pivot.reindex(complexity_order)
        pivot = pivot.reindex(columns=[q for q in quality_order if q in pivot.columns])
        
        # Calcular percentuais
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
        
        # Plotar
        pivot_pct.plot(
            kind='bar',
            stacked=True,
            ax=ax,
            color=[colors[q] for q in pivot_pct.columns],
            edgecolor='white',
            linewidth=0.5
        )
        
        ax.set_title(f'{tool}\n', fontsize=12, fontweight='bold')
        ax.set_xlabel('\nComplexidade (Arquivos Esperados)', fontsize=10)
        ax.set_ylabel('Proporção (%)' if ax == axes[0] else '', fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        ax.set_ylim(0, 100)
        
        # Remover legenda individual
        ax.legend().remove()
        
        # Adicionar contagens em cada barra
        for i, (idx, row) in enumerate(pivot.iterrows()):
            total = row.sum()
            ax.annotate(f'n={int(total)}', 
                       xy=(i, 102), 
                       ha='center', 
                       fontsize=9,
                       fontweight='bold')
    
    # Legenda compartilhada
    handles = [plt.Rectangle((0,0),1,1, color=colors[q]) for q in quality_order]
    fig.legend(handles, quality_order, 
               loc='upper center', 
               bbox_to_anchor=(0.5, 0.02),
               ncol=4,
               title='Qualidade do Merge',
               frameon=True)
    
    # Título geral
    fig.suptitle('Distribuição de Qualidade por Complexidade do Cenário\n', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    
    # Salvar
    output_path = CHARTS_PATH / "06_stacked_bar_complexity_quality.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "06_stacked_bar_complexity_quality.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Stacked bar chart salvo em: {output_path}")
    
    plt.close()
    
    # Tabela de contingência
    print("\nTabela de Contingência (Complexidade x Qualidade):")
    print("=" * 60)
    for tool in tools:
        print(f"\n{tool}:")
        tool_df = df[df['tool'] == tool]
        ct = pd.crosstab(tool_df['complexity'], tool_df['quality'])
        ct = ct.reindex(complexity_order)
        ct = ct.reindex(columns=[q for q in quality_order if q in ct.columns])
        print(ct)
    
    return df

if __name__ == "__main__":
    print("Gerando Stacked Bar Chart de Complexidade vs Qualidade...")
    df = create_stacked_bar()
