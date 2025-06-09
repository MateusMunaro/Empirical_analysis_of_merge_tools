import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import re
from merge_metrics_analyzer import MergeMetricsAnalyzer

class MergeMetricsVisualizer:
    def __init__(self, analyzer: MergeMetricsAnalyzer, output_dir: str = 'visualizations'):
        self.analyzer = analyzer
        self.output_dir = output_dir
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Cria o diretório se não existir
        import os
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_output_path(self, filename: str) -> str:
        """Retorna o caminho completo para salvar o arquivo"""
        import os
        return os.path.join(self.output_dir, filename)
    
    def _extract_scenario_number(self, scenario_name):
        """Extrai o número do cenário para ordenação correta"""
        match = re.search(r'scenario_(\d+)', scenario_name)
        if match:
            return int(match.group(1))
        return 999  # Valor alto para cenários sem número
    
    def _sort_scenarios(self, scenarios):
        """Ordena cenários numericamente"""
        return sorted(scenarios, key=self._extract_scenario_number)
        
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
        plt.savefig(self._get_output_path('summary_metrics.png'), dpi=300, bbox_inches='tight')
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
        plt.savefig(self._get_output_path('quality_distribution.png'), dpi=300, bbox_inches='tight')
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
        scenarios = self._sort_scenarios(list(scenario_data.keys()))
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
        plt.figure(figsize=(10, 12))
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
        plt.savefig(self._get_output_path('scenario_comparison_heatmap.png'), dpi=300, bbox_inches='tight')
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
        
        # Calcula médias com ordenação correta
        scenarios = self._sort_scenarios(list(scenario_metrics.keys()))
        avg_precision = [np.mean(scenario_metrics[s]['precision']) for s in scenarios]
        avg_recall = [np.mean(scenario_metrics[s]['recall']) for s in scenarios]
        avg_f1 = [np.mean(scenario_metrics[s]['f1_score']) for s in scenarios]
        avg_similarity = [np.mean(scenario_metrics[s]['similarity']) for s in scenarios]
        
        # Cria gráfico
        plt.figure(figsize=(16, 8))
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
        plt.savefig(self._get_output_path(f'{tool_name}_metrics_by_scenario.png'), dpi=300, bbox_inches='tight')
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
        plt.savefig(self._get_output_path('correspondence_stats.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_precision_recall_scatter(self, tool_name: str = None):
        """Scatterplot de Precisão vs Recall"""
        if tool_name is None and len(self.analyzer.tools_data) == 1:
            tool_name = list(self.analyzer.tools_data.keys())[0]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Se uma ferramenta específica foi solicitada
        if tool_name:
            if tool_name not in self.analyzer.tools_data:
                print(f"Ferramenta '{tool_name}' não encontrada")
                return
            
            data = self.analyzer.tools_data[tool_name]
            detailed_results = data.get('detailed_results', [])
            
            precisions = []
            recalls = []
            scenarios = []
            
            for result in detailed_results:
                precisions.append(result.get('precision', 0))
                recalls.append(result.get('recall', 0))
                scenario_num = self._extract_scenario_number(result.get('scenario', ''))
                scenarios.append(scenario_num)
            
            # Cria scatter plot com cores baseadas no número do cenário
            scatter = ax.scatter(recalls, precisions, c=scenarios, cmap='viridis', 
                               s=100, alpha=0.7, edgecolors='black', linewidth=1)
            
            # Adiciona colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Número do Cenário')
            
            # Adiciona linha diagonal de referência (F1 = 0.5)
            x = np.linspace(0, 1, 100)
            y = x  # Linha onde precision = recall
            ax.plot(x, y, 'k--', alpha=0.3, label='Precision = Recall')
            
            ax.set_title(f'Precisão vs Recall - {tool_name}')
        
        else:
            # Plota todas as ferramentas
            colors = plt.cm.Set3(np.linspace(0, 1, len(self.analyzer.tools_data)))
            
            for idx, (tool_name, data) in enumerate(self.analyzer.tools_data.items()):
                detailed_results = data.get('detailed_results', [])
                
                precisions = [r.get('precision', 0) for r in detailed_results]
                recalls = [r.get('recall', 0) for r in detailed_results]
                
                ax.scatter(recalls, precisions, c=[colors[idx]], s=100, alpha=0.7, 
                         label=tool_name, edgecolors='black', linewidth=1)
            
            ax.legend()
            ax.set_title('Precisão vs Recall - Todas as Ferramentas')
        
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precisão')
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = f'{tool_name}_precision_recall_scatter.png' if tool_name else 'all_tools_precision_recall_scatter.png'
        plt.savefig(self._get_output_path(filename), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_f1_similarity_scatter(self):
        """Scatterplot de F1 Score vs Similaridade"""
        plt.figure(figsize=(12, 8))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.analyzer.tools_data)))
        
        for idx, (tool_name, data) in enumerate(self.analyzer.tools_data.items()):
            detailed_results = data.get('detailed_results', [])
            
            f1_scores = []
            similarities = []
            
            for result in detailed_results:
                f1_scores.append(result.get('f1_score', 0))
                similarities.append(result.get('similarity_ratio', 0))
            
            plt.scatter(similarities, f1_scores, c=[colors[idx]], s=100, alpha=0.7,
                       label=tool_name, edgecolors='black', linewidth=1)
        
        plt.xlabel('Taxa de Similaridade')
        plt.ylabel('F1 Score')
        plt.title('F1 Score vs Similaridade')
        plt.xlim(-0.05, 1.05)
        plt.ylim(-0.05, 1.05)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Adiciona linha de tendência
        all_similarities = []
        all_f1_scores = []
        for tool_name, data in self.analyzer.tools_data.items():
            for result in data.get('detailed_results', []):
                all_similarities.append(result.get('similarity_ratio', 0))
                all_f1_scores.append(result.get('f1_score', 0))
        
        if all_similarities and all_f1_scores:
            z = np.polyfit(all_similarities, all_f1_scores, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(0, 1, 100)
            plt.plot(x_trend, p(x_trend), "r--", alpha=0.5, label=f'Tendência: y={z[0]:.2f}x+{z[1]:.2f}')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig(self._get_output_path('f1_similarity_scatter.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_scenario_performance_boxplot(self):
        """Boxplot de desempenho por cenário"""
        # Coleta dados de todas as ferramentas
        all_data = []
        
        for tool_name, data in self.analyzer.tools_data.items():
            detailed_results = data.get('detailed_results', [])
            
            for result in detailed_results:
                scenario = result.get('scenario', '').split('/')[0]
                all_data.append({
                    'Cenário': scenario,
                    'F1 Score': result.get('f1_score', 0),
                    'Ferramenta': tool_name
                })
        
        if not all_data:
            print("Sem dados para criar boxplot")
            return
        
        df = pd.DataFrame(all_data)
        
        # Ordena cenários
        scenario_order = self._sort_scenarios(df['Cenário'].unique())
        
        plt.figure(figsize=(16, 8))
        
        # Cria boxplot
        if len(self.analyzer.tools_data) > 1:
            sns.boxplot(data=df, x='Cenário', y='F1 Score', hue='Ferramenta', order=scenario_order)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            sns.boxplot(data=df, x='Cenário', y='F1 Score', order=scenario_order, color='skyblue')
        
        plt.xticks(rotation=45, ha='right')
        plt.title('Distribuição de F1 Score por Cenário')
        plt.ylim(0, 1.05)
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(self._get_output_path('scenario_performance_boxplot.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_error_rate_distribution(self):
        """Histograma de distribuição das taxas de erro"""
        fig, axes = plt.subplots(1, len(self.analyzer.tools_data), 
                                figsize=(6*len(self.analyzer.tools_data), 5))
        
        if len(self.analyzer.tools_data) == 1:
            axes = [axes]
        
        for idx, (tool_name, data) in enumerate(self.analyzer.tools_data.items()):
            detailed_results = data.get('detailed_results', [])
            error_rates = [r.get('error_rate', 0) for r in detailed_results]
            
            axes[idx].hist(error_rates, bins=20, color='salmon', edgecolor='black', alpha=0.7)
            axes[idx].set_xlabel('Taxa de Erro')
            axes[idx].set_ylabel('Frequência')
            axes[idx].set_title(f'Distribuição de Taxa de Erro - {tool_name}')
            axes[idx].set_xlim(0, 1)
            
            # Adiciona estatísticas
            mean_error = np.mean(error_rates)
            median_error = np.median(error_rates)
            axes[idx].axvline(mean_error, color='red', linestyle='--', linewidth=2, label=f'Média: {mean_error:.3f}')
            axes[idx].axvline(median_error, color='green', linestyle='--', linewidth=2, label=f'Mediana: {median_error:.3f}')
            axes[idx].legend()
        
        plt.tight_layout()
        plt.savefig(self._get_output_path('error_rate_distribution.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_metrics_correlation_matrix(self, tool_name: str = None):
        """Matriz de correlação entre métricas"""
        if tool_name is None and len(self.analyzer.tools_data) == 1:
            tool_name = list(self.analyzer.tools_data.keys())[0]
        
        if tool_name not in self.analyzer.tools_data:
            print(f"Ferramenta '{tool_name}' não encontrada")
            return
        
        data = self.analyzer.tools_data[tool_name]
        detailed_results = data.get('detailed_results', [])
        
        # Cria DataFrame com métricas
        metrics_data = []
        for result in detailed_results:
            metrics_data.append({
                'Precisão': result.get('precision', 0),
                'Recall': result.get('recall', 0),
                'F1 Score': result.get('f1_score', 0),
                'Similaridade': result.get('similarity_ratio', 0),
                'Taxa de Erro': result.get('error_rate', 0),
                'Acurácia de Ordem': result.get('line_order_accuracy', 0)
            })
        
        df = pd.DataFrame(metrics_data)
        
        # Calcula matriz de correlação
        corr_matrix = df.corr()
        
        # Cria heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                    square=True, linewidths=1, cbar_kws={"shrink": .8})
        
        plt.title(f'Matriz de Correlação entre Métricas - {tool_name}')
        plt.tight_layout()
        plt.savefig(self._get_output_path(f'{tool_name}_correlation_matrix.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_scenario_complexity_analysis(self):
        """Análise de complexidade dos cenários baseada no desempenho"""
        # Calcula desempenho médio por cenário
        scenario_performance = {}
        
        for tool_name, data in self.analyzer.tools_data.items():
            detailed_results = data.get('detailed_results', [])
            
            for result in detailed_results:
                scenario = result.get('scenario', '').split('/')[0]
                if scenario not in scenario_performance:
                    scenario_performance[scenario] = []
                scenario_performance[scenario].append(result.get('f1_score', 0))
        
        # Calcula média e desvio padrão por cenário
        scenario_stats = []
        for scenario, scores in scenario_performance.items():
            scenario_stats.append({
                'scenario': scenario,
                'mean_f1': np.mean(scores),
                'std_f1': np.std(scores),
                'num': self._extract_scenario_number(scenario)
            })
        
        # Ordena por número do cenário
        scenario_stats.sort(key=lambda x: x['num'])
        
        scenarios = [s['scenario'] for s in scenario_stats]
        mean_f1s = [s['mean_f1'] for s in scenario_stats]
        std_f1s = [s['std_f1'] for s in scenario_stats]
        
        # Cria gráfico de barras com barras de erro
        plt.figure(figsize=(16, 8))
        x = np.arange(len(scenarios))
        
        bars = plt.bar(x, mean_f1s, yerr=std_f1s, capsize=5, 
                       color=plt.cm.RdYlGn(mean_f1s), edgecolor='black', linewidth=1)
        
        # Adiciona linha de média geral
        overall_mean = np.mean(mean_f1s)
        plt.axhline(y=overall_mean, color='red', linestyle='--', 
                   label=f'Média Geral: {overall_mean:.3f}')
        
        plt.xlabel('Cenário')
        plt.ylabel('F1 Score Médio')
        plt.title('Análise de Complexidade dos Cenários (baseada em F1 Score)')
        plt.xticks(x, scenarios, rotation=45, ha='right')
        plt.ylim(0, 1.1)
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        # Adiciona colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(vmin=0, vmax=1))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), pad=0.01)
        cbar.set_label('Desempenho')
        
        plt.tight_layout()
        plt.savefig(self._get_output_path('scenario_complexity_analysis.png'), dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_all_visualizations(self):
        """Gera todas as visualizações disponíveis"""
        print(f"Gerando visualizações na pasta '{self.output_dir}'...")
        
        # Gráficos básicos
        self.plot_summary_metrics()
        print("✓ Métricas resumidas salvas em 'summary_metrics.png'")
        
        self.plot_quality_distribution()
        print("✓ Distribuição de qualidade salva em 'quality_distribution.png'")
        
        self.plot_correspondence_stats()
        print("✓ Estatísticas de correspondência salvas em 'correspondence_stats.png'")
        
        # Gráficos por ferramenta
        for tool_name in self.analyzer.tools_data.keys():
            self.plot_metrics_by_scenario(tool_name)
            print(f"✓ Métricas por cenário de {tool_name} salvas em '{tool_name}_metrics_by_scenario.png'")
            
            self.plot_precision_recall_scatter(tool_name)
            print(f"✓ Scatter Precisão vs Recall de {tool_name} salvo em '{tool_name}_precision_recall_scatter.png'")
            
            self.plot_metrics_correlation_matrix(tool_name)
            print(f"✓ Matriz de correlação de {tool_name} salva em '{tool_name}_correlation_matrix.png'")
        
        # Gráficos comparativos
        if len(self.analyzer.tools_data) >= 2:
            self.plot_scenario_comparison()
            print("✓ Comparação de cenários salva em 'scenario_comparison_heatmap.png'")
        
        # Gráficos gerais
        self.plot_precision_recall_scatter()  # Todas as ferramentas
        print("✓ Scatter Precisão vs Recall (todas) salvo em 'all_tools_precision_recall_scatter.png'")
        
        self.plot_f1_similarity_scatter()
        print("✓ Scatter F1 vs Similaridade salvo em 'f1_similarity_scatter.png'")
        
        self.plot_scenario_performance_boxplot()
        print("✓ Boxplot de desempenho salvo em 'scenario_performance_boxplot.png'")
        
        self.plot_error_rate_distribution()
        print("✓ Distribuição de taxa de erro salva em 'error_rate_distribution.png'")
        
        self.plot_scenario_complexity_analysis()
        print("✓ Análise de complexidade salva em 'scenario_complexity_analysis.png'")
        
        print(f"\nTodas as visualizações foram geradas com sucesso na pasta '{self.output_dir}'!")


# Exemplo de uso
if __name__ == "__main__":
    # Cria o analisador e carrega os dados
    analyzer = MergeMetricsAnalyzer()
    analyzer.load_json('/workspaces/Pesquisa-cientifica/reports/JDime/recursive_comparison_20250609_205859/full_recursive_report.json', 'JDime')
    
    # Se tiver outros JSONs:
    # analyzer.load_json('jdime_results.json', 'JDime')
    # analyzer.load_json('gitmerge_results.json', 'GitMerge')
    
    # Cria o visualizador com pasta personalizada (opcional)
    visualizer = MergeMetricsVisualizer(analyzer, output_dir='graficos_metricas')
    
    # Gera todas as visualizações
    visualizer.generate_all_visualizations()