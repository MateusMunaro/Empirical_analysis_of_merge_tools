"""
Script Principal: Executa todos os scripts de geração de gráficos
Gera todos os gráficos científicos para o estudo de ferramentas de merge

Execute este script para gerar todos os gráficos de uma vez:
    python run_all_charts.py
"""

import subprocess
import sys
from pathlib import Path

CHARTS_PATH = Path(__file__).parent

scripts = [
    ("01_heatmap_f1_score.py", "Heatmap de F1-Score"),
    ("02_scatter_complexity.py", "Scatter Plot Complexidade vs Qualidade"),
    ("03_radar_comparison.py", "Radar Chart Comparativo"),
    ("04_bubble_errors.py", "Bubble Chart de Erros"),
    ("05_violin_distribution.py", "Violin Plot de Distribuição"),
    ("06_stacked_bar_quality.py", "Stacked Bar de Qualidade por Complexidade"),
    ("07_boxplot_outliers.py", "Box Plot de Variabilidade"),
]

def run_all():
    print("=" * 70)
    print("GERAÇÃO DE GRÁFICOS CIENTÍFICOS - ANÁLISE DE FERRAMENTAS DE MERGE")
    print("=" * 70)
    print()
    
    success_count = 0
    failed_scripts = []
    
    for script_name, description in scripts:
        print(f"\n{'─' * 60}")
        print(f"▶ Executando: {description}")
        print(f"  Script: {script_name}")
        print(f"{'─' * 60}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(CHARTS_PATH / script_name)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(result.stdout)
                success_count += 1
            else:
                print(f"⚠ Erro ao executar {script_name}:")
                print(result.stderr)
                failed_scripts.append(script_name)
                
        except subprocess.TimeoutExpired:
            print(f"⚠ Timeout ao executar {script_name}")
            failed_scripts.append(script_name)
        except Exception as e:
            print(f"⚠ Exceção ao executar {script_name}: {e}")
            failed_scripts.append(script_name)
    
    # Resumo final
    print("\n" + "=" * 70)
    print("RESUMO DA GERAÇÃO DE GRÁFICOS")
    print("=" * 70)
    print(f"✓ Gráficos gerados com sucesso: {success_count}/{len(scripts)}")
    
    if failed_scripts:
        print(f"✗ Scripts com falha: {', '.join(failed_scripts)}")
    
    # Listar arquivos gerados
    print("\nArquivos gerados:")
    for f in sorted(CHARTS_PATH.glob("*.png")):
        size = f.stat().st_size / 1024
        print(f"  📊 {f.name} ({size:.1f} KB)")
    
    print("\n" + "=" * 70)
    print("Concluído! Os gráficos estão disponíveis na pasta 'charts/'")
    print("=" * 70)

if __name__ == "__main__":
    run_all()
