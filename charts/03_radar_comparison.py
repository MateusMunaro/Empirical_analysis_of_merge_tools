"""
Gráfico 3: Radar Chart - Perfil Comparativo de Ferramentas
Referência: Apel et al. (2011) - "Semistructured Merge: Rethinking Merge in Revision Control Systems"

O radar chart permite:
- Visualização holística do perfil de cada ferramenta
- Identificação de pontos fortes e fracos relativos
- Comparação multidimensional simultânea
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from math import pi

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

def create_radar_chart():
    reports = load_reports()
    
    # Métricas para o radar
    categories = [
        'Precision\nMédia',
        'Recall\nMédio',
        'F1-Score\nMédio',
        'Accuracy\nMédia',
        'Taxa de\nSucesso',
        'Consistência\n(1-StdDev)'
    ]
    
    # Extrair dados de cada ferramenta
    tool_data = {}
    for tool_name, report in reports.items():
        summary = report['summary']
        tool_data[tool_name] = [
            summary['avg_precision'],
            summary['avg_recall'],
            summary['avg_f1'],
            summary['avg_accuracy'],
            summary['success_rate'],
            1 - summary['std_f1']  # Inverter para que maior = mais consistente
        ]
    
    # Número de variáveis
    N = len(categories)
    
    # Ângulos para cada eixo
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Fechar o polígono
    
    # Cores
    colors = {'FSTMerge': '#2ecc71', 'IntelliMerge': '#3498db', 'JDime': '#e74c3c'}
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Plotar cada ferramenta
    for tool_name, values in tool_data.items():
        values_plot = values + values[:1]  # Fechar o polígono
        
        ax.plot(angles, values_plot, 'o-', linewidth=2, 
                label=tool_name, color=colors[tool_name])
        ax.fill(angles, values_plot, alpha=0.25, color=colors[tool_name])
    
    # Configurar eixos
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    
    # Configurar limites radiais
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    
    # Título
    ax.set_title('Perfil Comparativo de Ferramentas de Merge\n', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Legenda
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=True)
    
    plt.tight_layout()
    
    # Salvar
    output_path = CHARTS_PATH / "03_radar_tool_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(CHARTS_PATH / "03_radar_tool_comparison.pdf", bbox_inches='tight', facecolor='white')
    print(f"✓ Radar chart salvo em: {output_path}")
    
    plt.close()
    
    # Imprimir tabela resumo
    print("\nResumo das Métricas por Ferramenta:")
    print("-" * 60)
    print(f"{'Métrica':<20} {'FSTMerge':>12} {'IntelliMerge':>12} {'JDime':>12}")
    print("-" * 60)
    for i, cat in enumerate(['Precision', 'Recall', 'F1-Score', 'Accuracy', 'Success Rate', 'Consistência']):
        print(f"{cat:<20} {tool_data['FSTMerge'][i]:>12.3f} {tool_data['IntelliMerge'][i]:>12.3f} {tool_data['JDime'][i]:>12.3f}")
    print("-" * 60)
    
    return tool_data

if __name__ == "__main__":
    print("Gerando Radar Chart Comparativo...")
    data = create_radar_chart()
