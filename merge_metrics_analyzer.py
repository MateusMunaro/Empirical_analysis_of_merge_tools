import json
import pandas as pd
from pathlib import Path
from tabulate import tabulate
import numpy as np
from typing import Dict, List, Any
import os
import glob

class InteractiveFileSelector:
    def __init__(self, base_path: str = '.'):
        self.base_path = Path(base_path)
        
    def find_json_files(self, directory: Path) -> List[Path]:
        """Encontra todos os arquivos JSON em um diretório"""
        json_files = []
        for pattern in ['**/*.json', '**/*report*.json', '**/*result*.json']:
            json_files.extend(directory.glob(pattern))
        return sorted(set(json_files))
    
    def display_menu(self, items: List[str], title: str = "Selecione uma opção:") -> int:
        """Exibe um menu numerado e retorna a seleção do usuário"""
        print(f"\n{title}")
        print("-" * len(title))
        for i, item in enumerate(items, 1):
            print(f"{i:2d}. {item}")
        print(f"{len(items)+1:2d}. Voltar/Cancelar")
        
        while True:
            try:
                choice = input(f"\nEscolha (1-{len(items)+1}): ").strip()
                if not choice:
                    continue
                choice = int(choice)
                if 1 <= choice <= len(items) + 1:
                    return choice - 1 if choice <= len(items) else -1
                else:
                    print(f"Por favor, digite um número entre 1 e {len(items)+1}")
            except ValueError:
                print("Por favor, digite um número válido")
            except KeyboardInterrupt:
                print("\nOperação cancelada")
                return -1
    
    def navigate_directories(self, current_path: Path = None) -> Path:
        """Navega pelos diretórios interativamente"""
        if current_path is None:
            current_path = self.base_path
        
        while True:
            print(f"\n📁 Diretório atual: {current_path}")
            
            # Lista subdiretórios
            subdirs = [d for d in current_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            subdirs.sort()
            
            # Lista arquivos JSON no diretório atual
            json_files = self.find_json_files(current_path)
            local_json = [f for f in json_files if f.parent == current_path]
            
            options = []
            actions = []
            
            # Adiciona opção para voltar (se não estiver no diretório base)
            if current_path != self.base_path:
                options.append("📁 .. (Voltar)")
                actions.append("back")
            
            # Adiciona subdiretórios
            for subdir in subdirs:
                json_count = len(self.find_json_files(subdir))
                options.append(f"📁 {subdir.name} ({json_count} JSON{'s' if json_count != 1 else ''})")
                actions.append(("dir", subdir))
            
            # Adiciona arquivos JSON locais
            for json_file in local_json:
                size_kb = json_file.stat().st_size / 1024
                options.append(f"📄 {json_file.name} ({size_kb:.1f} KB)")
                actions.append(("file", json_file))
            
            if not options:
                print("❌ Nenhum diretório ou arquivo JSON encontrado")
                return None
            
            # Adiciona opções especiais
            options.append("🔍 Buscar recursivamente neste diretório")
            actions.append("search")
            
            choice = self.display_menu(options, f"Navegar em {current_path.name or 'raiz'}")
            
            if choice == -1:  # Cancelar
                return None
            
            action = actions[choice]
            
            if action == "back":
                current_path = current_path.parent
            elif action == "search":
                return self.search_json_files(current_path)
            elif isinstance(action, tuple):
                action_type, path = action
                if action_type == "dir":
                    current_path = path
                elif action_type == "file":
                    return path
    
    def search_json_files(self, search_path: Path) -> Path:
        """Busca recursivamente por arquivos JSON"""
        print(f"\n🔍 Buscando arquivos JSON em {search_path}...")
        json_files = self.find_json_files(search_path)
        
        if not json_files:
            print("❌ Nenhum arquivo JSON encontrado")
            input("Pressione Enter para continuar...")
            return None
        
        # Organiza por diretório
        files_by_dir = {}
        for file in json_files:
            rel_dir = file.parent.relative_to(search_path)
            if rel_dir not in files_by_dir:
                files_by_dir[rel_dir] = []
            files_by_dir[rel_dir].append(file)
        
        options = []
        files_list = []
        
        for rel_dir in sorted(files_by_dir.keys()):
            for file in sorted(files_by_dir[rel_dir]):
                size_kb = file.stat().st_size / 1024
                rel_path = file.relative_to(search_path)
                options.append(f"📄 {rel_path} ({size_kb:.1f} KB)")
                files_list.append(file)
        
        choice = self.display_menu(options, f"Arquivos JSON encontrados ({len(options)} total)")
        
        if choice == -1:
            return None
        
        return files_list[choice]
    
    def select_multiple_files(self) -> List[Path]:
        """Permite selecionar múltiplos arquivos"""
        selected_files = []
        
        while True:
            print(f"\n📋 Arquivos selecionados: {len(selected_files)}")
            for i, file in enumerate(selected_files, 1):
                print(f"  {i}. {file.name}")
            
            options = [
                "➕ Adicionar arquivo",
                "➖ Remover arquivo",
                "✅ Finalizar seleção",
                "🧹 Limpar seleção"
            ]
            
            choice = self.display_menu(options, "Gerenciar seleção de arquivos")
            
            if choice == -1:  # Cancelar
                return []
            elif choice == 0:  # Adicionar arquivo
                file = self.navigate_directories()
                if file and file not in selected_files:
                    selected_files.append(file)
                    print(f"✅ Adicionado: {file.name}")
                elif file in selected_files:
                    print(f"⚠️  Arquivo já selecionado: {file.name}")
            elif choice == 1:  # Remover arquivo
                if not selected_files:
                    print("❌ Nenhum arquivo selecionado")
                    continue
                
                file_options = [f.name for f in selected_files]
                remove_choice = self.display_menu(file_options, "Remover arquivo")
                if remove_choice != -1:
                    removed = selected_files.pop(remove_choice)
                    print(f"🗑️  Removido: {removed.name}")
            elif choice == 2:  # Finalizar
                if selected_files:
                    return selected_files
                else:
                    print("❌ Nenhum arquivo selecionado")
            elif choice == 3:  # Limpar
                selected_files.clear()
                print("🧹 Seleção limpa")

class MergeMetricsAnalyzer:
    def __init__(self):
        self.tools_data = {}
        
    def load_json(self, filepath: str, tool_name: str = None):
        """Carrega um arquivo JSON e armazena os dados"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Extrai o nome da ferramenta do caminho se não fornecido
        if tool_name is None:
            tool_name = Path(filepath).stem
            # Tenta extrair do diretório merge se possível
            if 'directories' in data and 'merge' in data['directories']:
                merge_path = data['directories']['merge']
                if 'IntelliMerge' in merge_path:
                    tool_name = 'IntelliMerge'
                elif 'JDime' in merge_path:
                    tool_name = 'JDime'
                elif 'GitMerge' in merge_path:
                    tool_name = 'GitMerge'
                else:
                    tool_name = Path(filepath).stem
        
        self.tools_data[tool_name] = data
        return tool_name
    
    def get_summary_table(self):
        """Gera tabela com métricas resumidas de todas as ferramentas"""
        if not self.tools_data:
            return "Nenhum dado carregado"
        
        summary_data = []
        for tool_name, data in self.tools_data.items():
            summary = data.get('summary', {})
            summary_data.append({
                'Ferramenta': tool_name,
                'Total Arquivos': summary.get('total_files', 0),
                'Matches Perfeitos': summary.get('perfect_matches', 0),
                'Alta Qualidade': summary.get('high_quality', 0),
                'Média Qualidade': summary.get('medium_quality', 0),
                'Baixa Qualidade': summary.get('low_quality', 0),
                'Precisão Média': f"{summary.get('avg_precision', 0):.3f}",
                'Recall Médio': f"{summary.get('avg_recall', 0):.3f}",
                'F1 Score Médio': f"{summary.get('avg_f1_score', 0):.3f}",
                'Similaridade Média': f"{summary.get('avg_similarity', 0):.3f}"
            })
        
        df = pd.DataFrame(summary_data)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def get_detailed_scenario_table(self, tool_name: str = None):
        """Gera tabela detalhada por cenário para uma ferramenta específica"""
        if tool_name is None and len(self.tools_data) == 1:
            tool_name = list(self.tools_data.keys())[0]
        
        if tool_name not in self.tools_data:
            return f"Ferramenta '{tool_name}' não encontrada"
        
        data = self.tools_data[tool_name]
        detailed_results = data.get('detailed_results', [])
        
        if not detailed_results:
            return "Sem resultados detalhados disponíveis"
        
        scenario_data = []
        for result in detailed_results:
            scenario_data.append({
                'Cenário': result.get('scenario', '').split('/')[0],
                'Arquivo': result.get('scenario', '').split('/')[-1],
                'Precisão': f"{result.get('precision', 0):.3f}",
                'Recall': f"{result.get('recall', 0):.3f}",
                'F1 Score': f"{result.get('f1_score', 0):.3f}",
                'Acurácia Ordem': f"{result.get('line_order_accuracy', 0):.3f}",
                'Taxa Similaridade': f"{result.get('similarity_ratio', 0):.3f}",
                'Linhas Esperadas': result.get('total_expected_lines', 0),
                'Linhas Merge': result.get('total_merge_lines', 0),
                'Taxa de Erro': f"{result.get('error_rate', 0):.3f}"
            })
        
        df = pd.DataFrame(scenario_data)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def get_correspondence_stats_table(self):
        """Gera tabela com estatísticas de correspondência para todas as ferramentas"""
        if not self.tools_data:
            return "Nenhum dado carregado"
        
        corr_data = []
        for tool_name, data in self.tools_data.items():
            corr_stats = data.get('correspondence_stats', {})
            corr_data.append({
                'Ferramenta': tool_name,
                'Matches Exatos': corr_stats.get('exact_matches', 0),
                'Matches Fuzzy': corr_stats.get('fuzzy_matches', 0),
                'Sem Match': corr_stats.get('no_matches', 0),
                'Arquivos em Conflito': corr_stats.get('conflict_files', 0)
            })
        
        df = pd.DataFrame(corr_data)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def get_missing_files_analysis(self, tool_name: str = None):
        """Analisa arquivos faltantes por cenário"""
        if tool_name is None and len(self.tools_data) == 1:
            tool_name = list(self.tools_data.keys())[0]
        
        if tool_name not in self.tools_data:
            return f"Ferramenta '{tool_name}' não encontrada"
        
        data = self.tools_data[tool_name]
        all_corr = data.get('all_correspondences', [])
        
        missing_by_scenario = {}
        for corr in all_corr:
            if corr.get('type') == 'missing_in_merge':
                scenario = corr.get('scenario', '').split('/')[0]
                if scenario not in missing_by_scenario:
                    missing_by_scenario[scenario] = []
                missing_by_scenario[scenario].append(corr.get('expected_file', ''))
        
        if not missing_by_scenario:
            return "Nenhum arquivo faltante encontrado"
        
        missing_data = []
        for scenario, files in sorted(missing_by_scenario.items()):
            missing_data.append({
                'Cenário': scenario,
                'Quantidade de Arquivos Faltantes': len(files),
                'Arquivos': ', '.join(files)
            })
        
        df = pd.DataFrame(missing_data)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def get_performance_by_scenario_type(self, tool_name: str = None):
        """Agrupa métricas por tipo de cenário"""
        if tool_name is None and len(self.tools_data) == 1:
            tool_name = list(self.tools_data.keys())[0]
        
        if tool_name not in self.tools_data:
            return f"Ferramenta '{tool_name}' não encontrada"
        
        data = self.tools_data[tool_name]
        detailed_results = data.get('detailed_results', [])
        
        if not detailed_results:
            return "Sem resultados detalhados disponíveis"
        
        # Agrupa por cenário
        scenario_groups = {}
        for result in detailed_results:
            scenario = result.get('scenario', '').split('/')[0]
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(result)
        
        # Calcula métricas médias por cenário
        scenario_metrics = []
        for scenario, results in sorted(scenario_groups.items()):
            avg_precision = np.mean([r.get('precision', 0) for r in results])
            avg_recall = np.mean([r.get('recall', 0) for r in results])
            avg_f1 = np.mean([r.get('f1_score', 0) for r in results])
            avg_similarity = np.mean([r.get('similarity_ratio', 0) for r in results])
            
            scenario_metrics.append({
                'Cenário': scenario,
                'Arquivos': len(results),
                'Precisão Média': f"{avg_precision:.3f}",
                'Recall Médio': f"{avg_recall:.3f}",
                'F1 Score Médio': f"{avg_f1:.3f}",
                'Similaridade Média': f"{avg_similarity:.3f}"
            })
        
        df = pd.DataFrame(scenario_metrics)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def compare_tools_by_scenario(self):
        """Compara desempenho das ferramentas por cenário"""
        if len(self.tools_data) < 2:
            return "Necessário carregar dados de pelo menos 2 ferramentas para comparação"
        
        # Coleta métricas por cenário para cada ferramenta
        scenario_comparison = {}
        
        for tool_name, data in self.tools_data.items():
            detailed_results = data.get('detailed_results', [])
            
            for result in detailed_results:
                scenario = result.get('scenario', '').split('/')[0]
                if scenario not in scenario_comparison:
                    scenario_comparison[scenario] = {}
                
                if tool_name not in scenario_comparison[scenario]:
                    scenario_comparison[scenario][tool_name] = {
                        'f1_scores': [],
                        'precisions': [],
                        'recalls': []
                    }
                
                scenario_comparison[scenario][tool_name]['f1_scores'].append(result.get('f1_score', 0))
                scenario_comparison[scenario][tool_name]['precisions'].append(result.get('precision', 0))
                scenario_comparison[scenario][tool_name]['recalls'].append(result.get('recall', 0))
        
        # Cria tabela comparativa
        comparison_data = []
        for scenario in sorted(scenario_comparison.keys()):
            row = {'Cenário': scenario}
            for tool_name in sorted(self.tools_data.keys()):
                if tool_name in scenario_comparison[scenario]:
                    tool_data = scenario_comparison[scenario][tool_name]
                    avg_f1 = np.mean(tool_data['f1_scores'])
                    row[f'{tool_name} F1'] = f"{avg_f1:.3f}"
                else:
                    row[f'{tool_name} F1'] = "N/A"
            comparison_data.append(row)
        
        df = pd.DataFrame(comparison_data)
        return tabulate(df, headers='keys', tablefmt='grid', showindex=False)
    
    def export_to_csv(self, output_dir: str = '.'):
        """Exporta todas as tabelas para arquivos CSV"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Exporta resumo geral
        if self.tools_data:
            # Summary
            summary_data = []
            for tool_name, data in self.tools_data.items():
                summary = data.get('summary', {})
                summary_data.append({
                    'tool': tool_name,
                    **summary
                })
            pd.DataFrame(summary_data).to_csv(output_path / 'summary_metrics.csv', index=False)
            
            # Detailed results por ferramenta
            for tool_name, data in self.tools_data.items():
                detailed_results = data.get('detailed_results', [])
                if detailed_results:
                    df = pd.DataFrame(detailed_results)
                    df.to_csv(output_path / f'{tool_name}_detailed_results.csv', index=False)
            
            print(f"Arquivos CSV exportados para: {output_path}")
    
    def print_all_tables(self):
        """Imprime todas as tabelas disponíveis"""
        print("\n" + "="*80)
        print("RESUMO GERAL DAS FERRAMENTAS")
        print("="*80)
        print(self.get_summary_table())
        
        print("\n" + "="*80)
        print("ESTATÍSTICAS DE CORRESPONDÊNCIA")
        print("="*80)
        print(self.get_correspondence_stats_table())
        
        for tool_name in self.tools_data.keys():
            print("\n" + "="*80)
            print(f"DETALHES POR CENÁRIO - {tool_name}")
            print("="*80)
            print(self.get_detailed_scenario_table(tool_name))
            
            print("\n" + "="*80)
            print(f"ARQUIVOS FALTANTES - {tool_name}")
            print("="*80)
            print(self.get_missing_files_analysis(tool_name))
            
            print("\n" + "="*80)
            print(f"DESEMPENHO POR TIPO DE CENÁRIO - {tool_name}")
            print("="*80)
            print(self.get_performance_by_scenario_type(tool_name))
        
        if len(self.tools_data) >= 2:
            print("\n" + "="*80)
            print("COMPARAÇÃO ENTRE FERRAMENTAS POR CENÁRIO")
            print("="*80)
            print(self.compare_tools_by_scenario())
    
    def interactive_load_files(self):
        """Interface interativa para carregar arquivos"""
        selector = InteractiveFileSelector()
        
        print("🚀 ANALISADOR DE MÉTRICAS DE MERGE")
        print("=" * 50)
        
        while True:
            options = [
                "📁 Selecionar arquivo único",
                "📁 Selecionar múltiplos arquivos",
                "📋 Ver arquivos carregados",
                "🗑️  Limpar dados carregados",
                "▶️  Executar análise",
                "💾 Exportar para CSV"
            ]
            
            choice = selector.display_menu(options, "Menu Principal")
            
            if choice == -1:  # Sair
                print("👋 Saindo...")
                break
            elif choice == 0:  # Arquivo único
                file_path = selector.navigate_directories()
                if file_path:
                    try:
                        tool_name = self.detect_tool_name(file_path)
                        suggested_name = input(f"Nome da ferramenta (sugerido: {tool_name}): ").strip()
                        if suggested_name:
                            tool_name = suggested_name
                        
                        self.load_json(str(file_path), tool_name)
                        print(f"✅ Arquivo carregado: {file_path.name} como '{tool_name}'")
                    except Exception as e:
                        print(f"❌ Erro ao carregar arquivo: {e}")
            elif choice == 1:  # Múltiplos arquivos
                files = selector.select_multiple_files()
                for file_path in files:
                    try:
                        tool_name = self.detect_tool_name(file_path)
                        self.load_json(str(file_path), tool_name)
                        print(f"✅ Carregado: {file_path.name} como '{tool_name}'")
                    except Exception as e:
                        print(f"❌ Erro ao carregar {file_path.name}: {e}")
            elif choice == 2:  # Ver carregados
                if self.tools_data:
                    print("\n📋 Arquivos carregados:")
                    for tool, data in self.tools_data.items():
                        summary = data.get('summary', {})
                        total_files = summary.get('total_files', 0)
                        print(f"  • {tool}: {total_files} arquivos analisados")
                else:
                    print("📭 Nenhum arquivo carregado")
                input("\nPressione Enter para continuar...")
            elif choice == 3:  # Limpar dados
                self.tools_data.clear()
                print("🧹 Dados limpos")
            elif choice == 4:  # Executar análise
                if self.tools_data:
                    print("\n" + "="*80)
                    print("🔍 EXECUTANDO ANÁLISE...")
                    print("="*80)
                    self.print_all_tables()
                    input("\nPressione Enter para continuar...")
                else:
                    print("❌ Nenhum dado carregado para análise")
            elif choice == 5:  # Exportar CSV
                if self.tools_data:
                    output_dir = input("Diretório de saída (default: merge_analysis_output): ").strip()
                    if not output_dir:
                        output_dir = 'merge_analysis_output'
                    self.export_to_csv(output_dir)
                else:
                    print("❌ Nenhum dado carregado para exportar")
    
    def detect_tool_name(self, file_path: Path) -> str:
        """Detecta o nome da ferramenta baseado no caminho do arquivo"""
        path_str = str(file_path).lower()
        
        if 'intellimerge' in path_str:
            return 'IntelliMerge'
        elif 'jdime' in path_str:
            return 'JDime'
        elif 'gitmerge' in path_str or 'git' in path_str:
            return 'GitMerge'
        elif 'merge' in path_str:
            return 'UnknownMergeTool'
        else:
            return file_path.stem.replace('_', ' ').title()

# Exemplo de uso
if __name__ == "__main__":
    # Cria o analisador
    analyzer = MergeMetricsAnalyzer()
    
    # Inicia interface interativa
    analyzer.interactive_load_files()