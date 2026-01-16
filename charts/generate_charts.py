"""
Script principal para geração de gráficos científicos para análise de ferramentas de merge.
Baseado em metodologias de estudos empíricos como Cavalcanti et al. (2017), Apel et al. (2011).

Autor: Análise Empírica de Ferramentas de Merge
Data: Janeiro 2026
"""

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Configuração de estilo científico
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 150

# Caminhos
BASE_PATH = Path(__file__).parent.parent
RESULTS_PATH = BASE_PATH / "evaluation_results"
CHARTS_PATH = BASE_PATH / "charts"

def load_reports():
    """Carrega os relatórios JSON de todas as ferramentas."""
    tools = ['FSTMerge', 'IntelliMerge', 'JDime']
    reports = {}
    
    for tool in tools:
        report_path = RESULTS_PATH / tool / "report.json"
        if report_path.exists():
            with open(report_path, 'r') as f:
                reports[tool] = json.load(f)
    
    return reports

def extract_scenario_data(reports):
    """Extrai dados de cenários para análise."""
    data = []
    
    for tool_name, report in reports.items():
        for scenario in report.get('scenarios', []):
            scenario_num = int(scenario['scenario_id'].replace('scenario_', ''))
            data.append({
                'tool': tool_name,
                'scenario_id': scenario['scenario_id'],
                'scenario_num': scenario_num,
                'quality': scenario['scenario_quality'],
                'precision': scenario['metrics']['precision'],
                'recall': scenario['metrics']['recall'],
                'f1_score': scenario['metrics']['f1_score'],
                'accuracy': scenario['metrics']['accuracy'],
                'completeness_rate': scenario['metrics']['completeness_rate'],
                'total_expected': scenario['files']['total_expected'],
                'total_actual': scenario['files']['total_actual'],
                'perfect_files': scenario['files']['perfect'],
                'files_with_issues': scenario['files']['with_issues'],
                'missing_files': len(scenario['files'].get('missing', [])),
                'extra_files': len(scenario['files'].get('extra', []))
            })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Carregando dados...")
    reports = load_reports()
    df = extract_scenario_data(reports)
    
    print(f"Dados carregados: {len(df)} registros de {df['tool'].nunique()} ferramentas")
    print(f"Cenários: {df['scenario_num'].min()} a {df['scenario_num'].max()}")
    
    # Salvar DataFrame para uso pelos outros scripts
    df.to_csv(CHARTS_PATH / "scenario_data.csv", index=False)
    print(f"Dados salvos em {CHARTS_PATH / 'scenario_data.csv'}")
