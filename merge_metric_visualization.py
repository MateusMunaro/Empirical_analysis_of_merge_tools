import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from merge_metrics_analyzer import MergeMetricsAnalyzer

class MergeMetricsVisualizer:
    def __init__(self, analyzer: MergeMetricsAnalyzer):
        self.analyzer = analyzer
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def plot_summary_metrics(self):
        """Gráfico de barras com métricas resumidas"""
        if not self.analyzer.tools_data:
            print("Nenhum dado carregado")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Métricas Resumidas das Ferramentas de Merge', fontsize=16)
        
        tools = []
        precision_values = []
        recall_values = []
        f1_values = []
        similarity_values = []
        
        for tool_name, data in self.analyzer.tools_data.items():
            summary = data.get('summary', {})
            tools.append(tool_name)
            precision_values.append(summary.get('avg_precision', 0))
            recall_values.append(summary.get('avg_recall', 0))
            f1_values.append(summary.get('avg_f1_score', 0))
            similarity_values.append(summary.get('avg_similarity', 0))
        
        # Precisão
        axes[0, 0].bar(tools, precision_values, color='skyblue')
        axes[0, 0].set_title('Precisão Média')
        axes[0, 0].set_ylim(0, 1)
        axes[0, 0].set_ylabel('Valor')
        
        # Recall
        axes[0, 1].bar(tools, recall_values, color='lightgreen')
        axes[0, 1].set_title('Recall Médio')
        axes[0, 1].set_ylim(0, 1)
        axes[0, 1].set_ylabel('Valor')
        
        # F1 Score
        axes[1, 0].bar(tools, f1_values, color='salmon')
        axes[1, 0].set_title('F1 Score Médio')
        axes[1, 0].set_ylim(0, 1)
        axes[1, 0].set_ylabel('Valor')
        
        # Similaridade
        axes[1, 1].bar(tools, similarity_values, color='gold')
        axes[1, 1].set_title('Similaridade Média')
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].set_ylabel('Valor')
        
        plt.tight_layout()
        plt.savefig('summary_metrics.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_quality_distribution(self):
        """Gráfico de pizza com distribuição de qualidade"""
        if not self.analyzer.tools_data:
            print("Nenhum dado carregado")
            return
        
        n_tools = len(self.analyzer.tools_data)
        fig, axes = plt.subplots(1, n_tools, figsize=(6*n_tools, 5))
        if n_tools == 1:
            axes = [axes]
        
        for idx, (tool_name, data) in enumerate(self.analyzer.tools_data.items()):
            summary = data.get('summary', {})
            
            sizes = [
                summary.get('perfect_matches', 0),
                summary.get('high_quality', 0),
                summary.get('medium_quality', 0),
                summary.get('low_quality', 0)
            ]
            labels = ['Perfeito', 'Alta', 'Média', 'Baixa']
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            
            axes[idx].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            axes[idx].set_title(f'Distribuição de Qualidade - {tool_name}')
        
        plt.tight_layout()
        plt.savefig('quality_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_scenario_comparison(self):
        """Heatmap comparando F1 scores por cenário"""
        if len(self.analyzer.tools_data) < 2:
            print("Necessário pelo menos 2 ferramentas para comparação")
            return
        
        # Coleta dados
        scenario_data = {}
        for tool_name, data in self.analyzer.tools_data.items():
            detailed_results = data.get('detailed_results', [])
            for result in detailed_results:
                scenario = result.get('scenario', '').split('/')[0]
                if scenario not in scenario_data:
                    scenario_data[scenario] = {}
                if tool_name not in scenario_data[scenario]:
                    scenario_data[scenario][tool_name] = []
                scenario_data[scenario][tool_name].append(result.get('f1_score', 0))
        
        # Calcula médias
        matrix_data = []
        scenarios = sorted(scenario_data.keys())
        tools = sorted(self.analyzer.tools_data.keys())
        
        for scenario in scenarios:
            row = []
            for tool in tools:
                if tool in scenario_data[scenario]:
                    avg_f1 = np.mean(scenario_data[scenario][tool])
                    row.append(avg_f1)
                else:
                    row.append(0)
            matrix_data.append(row)
        
        # Cria heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(matrix_data, 
                    xticklabels=tools, 
                    yticklabels=scenarios,
                    annot=True, 
                    fmt='.3f',
                    cmap='RdYlGn',
                    cbar_kws={'label': 'F1 Score'},
                    vmin=0, vmax=1)
        
        plt.title('Comparação de F1 Score por Cenário e Ferramenta')
        plt.xlabel('Ferramenta')
        plt.ylabel('Cenário')
        plt.tight_layout()
        plt.savefig('scenario_comparison_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_metrics_by_scenario(self, tool_name: str):
        """Gráfico de linha com métricas por cenário"""
        if tool_name not in self.analyzer.tools_data:
            print(f"Ferramenta '{tool_name}' não encontrada")
            return
        
        data = self.analyzer.tools_data[tool_name]
        detailed_results = data.get('detailed_results', [])
        
        if not detailed_results:
            print("Sem resultados detalhados")
            return
        
        # Organiza dados por cenário
        scenario_metrics = {}
        for result in detailed_results:
            scenario = result.get('scenario', '').split('/')[0]
            if scenario not in scenario_metrics:
                scenario_metrics[scenario] = {
                    'precision': [],
                    'recall': [],
                    'f1_score': [],
                    'similarity': []
                }
            scenario_metrics[scenario]['precision'].append(result.get('precision', 0))
            scenario_metrics[scenario]['recall'].append(result.get('recall', 0))
            scenario_metrics[scenario]['f1_score'].append(result.get('f1_score', 0))
            scenario_metrics[scenario]['similarity'].append(result.get('similarity_ratio', 0))
        
        # Calcula médias
        scenarios = sorted(scenario_metrics.keys())
        avg_precision = [np.mean(scenario_metrics[s]['precision']) for s in scenarios]
        avg_recall = [np.mean(scenario_metrics[s]['recall']) for s in scenarios]
        avg_f1 = [np.mean(scenario_metrics[s]['f1_score']) for s in scenarios]
        avg_similarity = [np.mean(scenario_metrics[s]['similarity']) for s in scenarios]
        
        # Cria gráfico
        plt.figure(figsize=(14, 8))
        x = np.arange(len(scenarios))
        
        plt.plot(x, avg_precision, 'o-', label='Precisão', linewidth=2, markersize=8)
        plt.plot(x, avg_recall, 's-', label='Recall', linewidth=2, markersize=8)
        plt.plot(x, avg_f1, '^-', label='F1 Score', linewidth=2, markersize=8)
        plt.plot(x, avg_similarity, 'd-', label='Similaridade', linewidth=2, markersize=8)
        
        plt.xlabel('Cenário')
        plt.ylabel('Valor da Métrica')
        plt.title(f'Métricas por Cenário - {tool_name}')
        plt.xticks(x, scenarios, rotation=45, ha='right')
        plt.ylim(0, 1.05)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{tool_name}_metrics_by_scenario.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_correspondence_stats(self):
        """Gráfico de barras empilhadas com tipos de correspondência"""
        if not self.analyzer.tools_data:
            print("Nenhum dado carregado")
            return
        
        tools = []
        exact_matches = []
        fuzzy_matches = []
        no_matches = []
        
        for tool_name, data in self.analyzer.tools_data.items():
            corr_stats = data.get('correspondence_stats', {})
            tools.append(tool_name)
            exact_matches.append(corr_stats.get('exact_matches', 0))
            fuzzy_matches.append(corr_stats.get('fuzzy_matches', 0))
            no_matches.append(corr_stats.get('no_matches', 0))
        
        x = np.arange(len(tools))
        width = 0.6
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        p1 = ax.bar(x, exact_matches, width, label='Matches Exatos', color='#2ecc71')
        p2 = ax.bar(x, fuzzy_matches, width, bottom=exact_matches, label='Matches Fuzzy', color='#3498db')
        p3 = ax.bar(x, no_matches, width, bottom=np.array(exact_matches)+np.array(fuzzy_matches), 
                   label='Sem Match', color='#e74c3c')
        
        ax.set_xlabel('Ferramenta')
        ax.set_ylabel('Número de Arquivos')
        ax.set_title('Tipos de Correspondência por Ferramenta')
        ax.set_xticks(x)
        ax.set_xticklabels(tools)
        ax.legend()
        
        # Adiciona valores nas barras
        for i, (e, f, n) in enumerate(zip(exact_matches, fuzzy_matches, no_matches)):
            if e > 0:
                ax.text(i, e/2, str(e), ha='center', va='center')
            if f > 0:
                ax.text(i, e + f/2, str(f), ha='center', va='center')
            if n > 0:
                ax.text(i, e + f + n/2, str(n), ha='center', va='center')
        
        plt.tight_layout()
        plt.savefig('correspondence_stats.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_all_visualizations(self):
        """Gera todas as visualizações disponíveis"""
        print("Gerando visualizações...")
        
        self.plot_summary_metrics()
        print("✓ Métricas resumidas salvas em 'summary_metrics.png'")
        
        self.plot_quality_distribution()
        print("✓ Distribuição de qualidade salva em 'quality_distribution.png'")
        
        self.plot_correspondence_stats()
        print("✓ Estatísticas de correspondência salvas em 'correspondence_stats.png'")
        
        for tool_name in self.analyzer.tools_data.keys():
            self.plot_metrics_by_scenario(tool_name)
            print(f"✓ Métricas por cenário de {tool_name} salvas em '{tool_name}_metrics_by_scenario.png'")
        
        if len(self.analyzer.tools_data) >= 2:
            self.plot_scenario_comparison()
            print("✓ Comparação de cenários salva em 'scenario_comparison_heatmap.png'")
        
        print("\nTodas as visualizações foram geradas com sucesso!")


# Exemplo de uso
if __name__ == "__main__":
    # Cria o analisador e carrega os dados
    analyzer = MergeMetricsAnalyzer()
    analyzer.load_json('paste.txt', 'IntelliMerge')
    
    # Se tiver outros JSONs:
    # analyzer.load_json('jdime_results.json', 'JDime')
    # analyzer.load_json('gitmerge_results.json', 'GitMerge')
    
    # Cria o visualizador
    visualizer = MergeMetricsVisualizer(analyzer)
    
    # Gera todas as visualizações
    visualizer.generate_all_visualizations()