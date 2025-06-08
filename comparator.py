#!/usr/bin/env python3
"""
Script para comparar resultados de merge com arquivos esperados e calcular métricas de qualidade.
Versão 3.0 - Comparação recursiva com análise de nomes de arquivos
"""

import os
import sys
import difflib
from pathlib import Path
from typing import List, Tuple, Dict, Set
import argparse
import platform
import json
import datetime
import re
from collections import defaultdict


# Cores ANSI para melhor visualização (opcional)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.ENDC = ''
        Colors.BOLD = ''

# Desabilita cores no Windows se não suportado
if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except:
        Colors.disable()


class FileNameAnalyzer:
    """Analisa e compara nomes de arquivos para detectar padrões de merge"""
    
    def __init__(self):
        self.conflict_patterns = [
            r'\.BASE\.',
            r'\.LOCAL\.',
            r'\.REMOTE\.',
            r'\.BACKUP\.',
            r'_BACKUP_',
            r'_BASE_',
            r'_LOCAL_',
            r'_REMOTE_',
            r'<<<<<<< ',
            r'=======',
            r'>>>>>>> ',
            r'\.orig$',
            r'\.rej$',
            r'\.mine$',
            r'\.r\d+$',
            r'\.working$',
            r'\.merge-\w+$',
            r'_conflict_',
            r'_merged_',
            r'\.conflicted\.',
        ]
        
        self.temp_patterns = [
            r'^\.#',
            r'^#.*#$',
            r'^\..*\.swp$',
            r'^\..*\.tmp$',
            r'~$',
            r'\.bak$',
        ]
    
    def is_conflict_file(self, filename: str) -> bool:
        """Verifica se um arquivo tem padrão de arquivo de conflito"""
        for pattern in self.conflict_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False
    
    def is_temp_file(self, filename: str) -> bool:
        """Verifica se um arquivo é temporário"""
        for pattern in self.temp_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False
    
    def extract_base_name(self, filename: str) -> str:
        """Extrai o nome base removendo sufixos de merge/conflito"""
        base_name = filename
        
        # Remove extensões de conflito conhecidas
        patterns_to_remove = [
            r'\.BASE\.[^.]+$',
            r'\.LOCAL\.[^.]+$', 
            r'\.REMOTE\.[^.]+$',
            r'\.BACKUP\.[^.]+$',
            r'_BACKUP_\d+',
            r'_BASE_\d+',
            r'_LOCAL_\d+',
            r'_REMOTE_\d+',
            r'\.orig$',
            r'\.rej$',
            r'\.mine$',
            r'\.r\d+$',
            r'\.working$',
            r'\.merge-\w+$',
            r'_conflict_\d*',
            r'_merged_\d*',
            r'\.conflicted\.\w+$',
        ]
        
        for pattern in patterns_to_remove:
            base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        
        return base_name
    
    def calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcula similaridade entre dois nomes de arquivo"""
        # Remove extensões para comparar apenas o nome
        base1 = os.path.splitext(name1)[0]
        base2 = os.path.splitext(name2)[0]
        
        # Usa SequenceMatcher para calcular similaridade
        sm = difflib.SequenceMatcher(None, base1.lower(), base2.lower())
        return sm.ratio()
    
    def find_best_match(self, target_name: str, candidate_names: List[str], threshold: float = 0.6) -> Tuple[str, float]:
        """Encontra o melhor match para um nome de arquivo"""
        best_match = None
        best_score = 0.0
        
        target_base = self.extract_base_name(target_name)
        
        for candidate in candidate_names:
            candidate_base = self.extract_base_name(candidate)
            
            # Primeiro tenta match exato
            if target_base.lower() == candidate_base.lower():
                return candidate, 1.0
            
            # Calcula similaridade
            similarity = self.calculate_name_similarity(target_base, candidate_base)
            
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = candidate
        
        return best_match, best_score


class RecursiveFileScanner:
    """Escaneia diretórios recursivamente e organiza arquivos"""
    
    def __init__(self, file_extensions: List[str] = None):
        self.file_extensions = file_extensions or ['.java', '.py', '.cpp', '.c', '.h', '.hpp', '.js', '.ts', '.xml', '.json']
        self.name_analyzer = FileNameAnalyzer()
    
    def scan_directory(self, directory: str) -> Dict[str, List[str]]:
        """Escaneia um diretório recursivamente e organiza arquivos por caminho relativo"""
        files_by_path = defaultdict(list)
        
        for root, dirs, files in os.walk(directory):
            # Calcula caminho relativo
            rel_path = os.path.relpath(root, directory)
            if rel_path == '.':
                rel_path = ''
            
            # Filtra arquivos por extensão e remove temporários/conflito
            valid_files = []
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    if not self.name_analyzer.is_temp_file(file):
                        valid_files.append(file)
            
            if valid_files:
                files_by_path[rel_path] = valid_files
        
        return dict(files_by_path)
    
    def find_corresponding_files(self, merge_files: Dict[str, List[str]], 
                               expected_files: Dict[str, List[str]]) -> List[Dict]:
        """Encontra correspondências entre arquivos de dois diretórios"""
        correspondences = []
        merge_stats = {'exact_matches': 0, 'fuzzy_matches': 0, 'no_matches': 0, 'conflict_files': 0}
        
        # Para cada caminho no diretório de merge
        for merge_path, merge_file_list in merge_files.items():
            
            # Procura caminho correspondente no esperado
            expected_file_list = expected_files.get(merge_path, [])
            
            if not expected_file_list:
                # Tenta encontrar caminho similar
                for exp_path, exp_files in expected_files.items():
                    path_similarity = difflib.SequenceMatcher(None, merge_path, exp_path).ratio()
                    if path_similarity > 0.8:
                        expected_file_list = exp_files
                        break
            
            # Para cada arquivo no merge, procura correspondência
            for merge_file in merge_file_list:
                
                # Verifica se é arquivo de conflito
                if self.name_analyzer.is_conflict_file(merge_file):
                    merge_stats['conflict_files'] += 1
                    correspondences.append({
                        'type': 'conflict_file',
                        'scenario': f"{merge_path}/{merge_file}" if merge_path else merge_file,
                        'merge_file': merge_file,
                        'expected_file': None,
                        'match_score': 0.0,
                        'quality_issues': ['conflict_file']
                    })
                    continue
                
                # Procura correspondência exata primeiro
                if merge_file in expected_file_list:
                    merge_stats['exact_matches'] += 1
                    correspondences.append({
                        'type': 'exact_match',
                        'scenario': f"{merge_path}/{merge_file}" if merge_path else merge_file,
                        'merge_file': merge_file,
                        'expected_file': merge_file,
                        'match_score': 1.0,
                        'quality_issues': []
                    })
                else:
                    # Procura melhor correspondência fuzzy
                    best_match, score = self.name_analyzer.find_best_match(merge_file, expected_file_list)
                    
                    if best_match:
                        merge_stats['fuzzy_matches'] += 1
                        quality_issues = []
                        
                        if score < 0.9:
                            quality_issues.append('name_mismatch')
                        
                        correspondences.append({
                            'type': 'fuzzy_match',
                            'scenario': f"{merge_path}/{merge_file}" if merge_path else merge_file,
                            'merge_file': merge_file,
                            'expected_file': best_match,
                            'match_score': score,
                            'quality_issues': quality_issues
                        })
                    else:
                        merge_stats['no_matches'] += 1
                        correspondences.append({
                            'type': 'no_match',
                            'scenario': f"{merge_path}/{merge_file}" if merge_path else merge_file,
                            'merge_file': merge_file,
                            'expected_file': None,
                            'match_score': 0.0,
                            'quality_issues': ['missing_correspondence']
                        })
        
        # Verifica arquivos esperados que não têm correspondência
        for exp_path, exp_file_list in expected_files.items():
            merge_file_list = merge_files.get(exp_path, [])
            
            for exp_file in exp_file_list:
                # Verifica se esse arquivo esperado já foi encontrado
                found = any(c['expected_file'] == exp_file and 
                           c['scenario'].startswith(exp_path) for c in correspondences)
                
                if not found:
                    correspondences.append({
                        'type': 'missing_in_merge',
                        'scenario': f"{exp_path}/{exp_file}" if exp_path else exp_file,
                        'merge_file': None,
                        'expected_file': exp_file,
                        'match_score': 0.0,
                        'quality_issues': ['missing_in_merge']
                    })
        
        return correspondences, merge_stats


class MergeComparator:
    def __init__(self):
        self.merge_lines = []
        self.expected_lines = []
        self.normalized_merge_lines = []
        self.normalized_expected_lines = []
        
    def normalize_line(self, line: str) -> str:
        """Remove espaços em branco extras e normaliza a linha"""
        return ' '.join(line.strip().split())
    
    def load_files(self, merge_path: str, expected_path: str) -> bool:
        """Carrega e normaliza os arquivos"""
        try:
            with open(merge_path, 'r', encoding='utf-8') as f:
                self.merge_lines = f.readlines()
                
            with open(expected_path, 'r', encoding='utf-8') as f:
                self.expected_lines = f.readlines()
                
            # Normaliza as linhas removendo espaços extras
            self.normalized_merge_lines = [
                self.normalize_line(line) for line in self.merge_lines 
                if self.normalize_line(line)  # Remove linhas vazias
            ]
            
            self.normalized_expected_lines = [
                self.normalize_line(line) for line in self.expected_lines 
                if self.normalize_line(line)  # Remove linhas vazias
            ]
            
            return True
            
        except Exception as e:
            print(f"Erro ao carregar arquivos: {e}")
            return False
    
    def calculate_metrics(self) -> Dict[str, float]:
        """Calcula várias métricas de comparação"""
        metrics = {}
        
        # Converte para conjuntos para análise
        merge_set = set(self.normalized_merge_lines)
        expected_set = set(self.normalized_expected_lines)
        
        # Calcula intersecção e diferenças
        correct_lines = merge_set & expected_set  # Linhas corretas (TP)
        extra_lines = merge_set - expected_set    # Linhas extras no merge (FP)
        missing_lines = expected_set - merge_set  # Linhas faltando no merge (FN)
        
        # Métricas básicas
        total_expected = len(expected_set)
        total_merge = len(merge_set)
        true_positives = len(correct_lines)
        false_positives = len(extra_lines)
        false_negatives = len(missing_lines)
        
        # Precision: TP / (TP + FP)
        if (true_positives + false_positives) > 0:
            metrics['precision'] = true_positives / (true_positives + false_positives)
        else:
            metrics['precision'] = 0.0
            
        # Recall: TP / (TP + FN)
        if (true_positives + false_negatives) > 0:
            metrics['recall'] = true_positives / (true_positives + false_negatives)
        else:
            metrics['recall'] = 0.0
            
        # F1-Score: 2 * (precision * recall) / (precision + recall)
        if (metrics['precision'] + metrics['recall']) > 0:
            metrics['f1_score'] = 2 * (metrics['precision'] * metrics['recall']) / \
                                 (metrics['precision'] + metrics['recall'])
        else:
            metrics['f1_score'] = 0.0
            
        # Accuracy considerando ordem das linhas
        matches = 0
        for i in range(min(len(self.normalized_merge_lines), 
                          len(self.normalized_expected_lines))):
            if self.normalized_merge_lines[i] == self.normalized_expected_lines[i]:
                matches += 1
                
        max_lines = max(len(self.normalized_merge_lines), 
                       len(self.normalized_expected_lines))
        
        if max_lines > 0:
            metrics['line_order_accuracy'] = matches / max_lines
        else:
            metrics['line_order_accuracy'] = 0.0
            
        # Similaridade usando SequenceMatcher
        sm = difflib.SequenceMatcher(None, 
                                    self.normalized_merge_lines, 
                                    self.normalized_expected_lines)
        metrics['similarity_ratio'] = sm.ratio()
        
        # Métricas adicionais
        metrics['total_expected_lines'] = total_expected
        metrics['total_merge_lines'] = total_merge
        metrics['correct_lines'] = true_positives
        metrics['extra_lines'] = false_positives
        metrics['missing_lines'] = false_negatives
        
        # Taxa de erro
        metrics['error_rate'] = 1.0 - metrics['precision']
        
        return metrics
    
    def generate_diff_report(self, output_path: str = None):
        """Gera um relatório detalhado das diferenças"""
        diff = difflib.unified_diff(
            self.normalized_expected_lines,
            self.normalized_merge_lines,
            fromfile='expected',
            tofile='merge',
            lineterm=''
        )
        
        diff_content = '\n'.join(diff)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(diff_content)
        
        return diff_content


def compare_directories_recursive(merge_dir: str, expected_dir: str, output_dir: str = None, file_extensions: List[str] = None):
    """Compara todos os arquivos entre dois diretórios recursivamente"""
    
    print(f"\n{Colors.HEADER}=== COMPARAÇÃO RECURSIVA DE DIRETÓRIOS ==={Colors.ENDC}")
    print(f"{Colors.CYAN}Diretório de Merge: {merge_dir}{Colors.ENDC}")
    print(f"{Colors.CYAN}Diretório Esperado: {expected_dir}{Colors.ENDC}")
    
    # Inicializa scanner
    scanner = RecursiveFileScanner(file_extensions)
    
    # Escaneia diretórios
    print(f"\n{Colors.BLUE}Escaneando diretórios recursivamente...{Colors.ENDC}")
    merge_files = scanner.scan_directory(merge_dir)
    expected_files = scanner.scan_directory(expected_dir)
    
    # Estatísticas de arquivos encontrados
    total_merge_files = sum(len(files) for files in merge_files.values())
    total_expected_files = sum(len(files) for files in expected_files.values())
    
    print(f"{Colors.GREEN}✓ Arquivos encontrados no merge: {total_merge_files}{Colors.ENDC}")
    print(f"{Colors.GREEN}✓ Arquivos encontrados no esperado: {total_expected_files}{Colors.ENDC}")
    
    # Encontra correspondências
    print(f"\n{Colors.BLUE}Procurando correspondências entre arquivos...{Colors.ENDC}")
    correspondences, match_stats = scanner.find_corresponding_files(merge_files, expected_files)
    
    # Mostra estatísticas de matching
    print(f"\n{Colors.CYAN}Estatísticas de Correspondência:{Colors.ENDC}")
    print(f"  Correspondências exatas: {Colors.GREEN}{match_stats['exact_matches']}{Colors.ENDC}")
    print(f"  Correspondências aproximadas: {Colors.YELLOW}{match_stats['fuzzy_matches']}{Colors.ENDC}")
    print(f"  Sem correspondência: {Colors.RED}{match_stats['no_matches']}{Colors.ENDC}")
    print(f"  Arquivos de conflito detectados: {Colors.RED}{match_stats['conflict_files']}{Colors.ENDC}")
    
    # Filtra apenas correspondências que podem ser comparadas
    comparable_correspondences = [c for c in correspondences 
                                if c['merge_file'] and c['expected_file'] and 
                                c['type'] in ['exact_match', 'fuzzy_match']]
    
    if not comparable_correspondences:
        print(f"{Colors.RED}❌ Nenhum arquivo comparável encontrado!{Colors.ENDC}")
        return
    
    print(f"{Colors.GREEN}✓ {len(comparable_correspondences)} arquivos serão comparados{Colors.ENDC}")
    
    # Cria diretório de saída se especificado
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(output_dir, f"recursive_comparison_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
    
    # Resultados consolidados
    all_results = []
    total_metrics = {
        'total_files': len(comparable_correspondences),
        'perfect_matches': 0,
        'high_quality': 0,  # >= 90%
        'medium_quality': 0,  # >= 70%
        'low_quality': 0,  # < 70%
        'total_precision': 0.0,
        'total_recall': 0.0,
        'total_f1_score': 0.0,
        'total_similarity': 0.0,
        'name_quality_issues': 0,
        'structural_issues': 0
    }
    
    # Compara cada par de arquivos
    print(f"\n{Colors.BLUE}Iniciando comparações detalhadas...{Colors.ENDC}")
    for i, correspondence in enumerate(comparable_correspondences, 1):
        scenario = correspondence['scenario']
        merge_file = correspondence['merge_file']
        expected_file = correspondence['expected_file']
        match_score = correspondence['match_score']
        quality_issues = correspondence['quality_issues']
        
        print(f"\n[{i}/{len(comparable_correspondences)}] {scenario}")
        if match_score < 1.0:
            print(f"  {Colors.YELLOW}⚠ Match fuzzy: {merge_file} ↔ {expected_file} (score: {match_score:.3f}){Colors.ENDC}")
        
        # Constrói caminhos completos
        if '/' in scenario:
            path_part = os.path.dirname(scenario)
            merge_path = os.path.join(merge_dir, path_part, merge_file)
            expected_path = os.path.join(expected_dir, path_part, expected_file)
        else:
            merge_path = os.path.join(merge_dir, merge_file)
            expected_path = os.path.join(expected_dir, expected_file)
        
        # Compara conteúdo
        comparator = MergeComparator()
        if comparator.load_files(merge_path, expected_path):
            metrics = comparator.calculate_metrics()
            
            # Adiciona informações da correspondência
            metrics.update({
                'scenario': scenario,
                'merge_file': merge_file,
                'expected_file': expected_file,
                'match_score': match_score,
                'quality_issues': quality_issues,
                'match_type': correspondence['type']
            })
            
            # Calcula score de qualidade ajustado
            adjusted_f1 = metrics['f1_score'] * match_score
            metrics['adjusted_f1_score'] = adjusted_f1
            
            # Atualiza estatísticas
            if adjusted_f1 == 1.0:
                total_metrics['perfect_matches'] += 1
            elif adjusted_f1 >= 0.9:
                total_metrics['high_quality'] += 1
            elif adjusted_f1 >= 0.7:
                total_metrics['medium_quality'] += 1
            else:
                total_metrics['low_quality'] += 1
            
            if quality_issues:
                total_metrics['name_quality_issues'] += 1
            
            total_metrics['total_precision'] += metrics['precision']
            total_metrics['total_recall'] += metrics['recall']
            total_metrics['total_f1_score'] += adjusted_f1
            total_metrics['total_similarity'] += metrics['similarity_ratio']
            
            all_results.append(metrics)
            
            # Mostra resumo
            f1_color = Colors.GREEN if adjusted_f1 >= 0.9 else Colors.YELLOW if adjusted_f1 >= 0.7 else Colors.RED
            issues_text = f" | Issues: {', '.join(quality_issues)}" if quality_issues else ""
            print(f"  F1-Score: {f1_color}{adjusted_f1:.4f}{Colors.ENDC} | " +
                  f"Content F1: {metrics['f1_score']:.4f} | " +
                  f"Name Match: {match_score:.3f}{issues_text}")
            
            # Salva diff individual se diretório de saída especificado
            if output_dir:
                safe_scenario = scenario.replace('/', '_').replace('\\', '_')
                diff_file = os.path.join(report_dir, f"{safe_scenario}_diff.txt")
                comparator.generate_diff_report(diff_file)
        else:
            print(f"  {Colors.RED}❌ Erro ao carregar arquivos{Colors.ENDC}")
    
    # Calcula médias
    if total_metrics['total_files'] > 0:
        total_metrics['avg_precision'] = total_metrics['total_precision'] / total_metrics['total_files']
        total_metrics['avg_recall'] = total_metrics['total_recall'] / total_metrics['total_files']
        total_metrics['avg_f1_score'] = total_metrics['total_f1_score'] / total_metrics['total_files']
        total_metrics['avg_similarity'] = total_metrics['total_similarity'] / total_metrics['total_files']
    
    # Exibe relatório consolidado
    print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}RELATÓRIO CONSOLIDADO - COMPARAÇÃO RECURSIVA{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Resumo Geral:{Colors.ENDC}")
    print(f"  Total de arquivos analisados: {len(correspondences)}")
    print(f"  Arquivos comparáveis: {total_metrics['total_files']}")
    print(f"  Correspondências perfeitas (100%): {Colors.GREEN}{total_metrics['perfect_matches']}{Colors.ENDC}")
    print(f"  Alta qualidade (≥90%): {Colors.GREEN}{total_metrics['high_quality']}{Colors.ENDC}")
    print(f"  Média qualidade (≥70%): {Colors.YELLOW}{total_metrics['medium_quality']}{Colors.ENDC}")
    print(f"  Baixa qualidade (<70%): {Colors.RED}{total_metrics['low_quality']}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Problemas de Qualidade Detectados:{Colors.ENDC}")
    print(f"  Arquivos com problemas de nome: {Colors.YELLOW}{total_metrics['name_quality_issues']}{Colors.ENDC}")
    print(f"  Arquivos de conflito não resolvidos: {Colors.RED}{match_stats['conflict_files']}{Colors.ENDC}")
    print(f"  Arquivos sem correspondência: {Colors.RED}{match_stats['no_matches']}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Métricas Médias (Ajustadas):{Colors.ENDC}")
    avg_f1_color = Colors.GREEN if total_metrics['avg_f1_score'] >= 0.9 else Colors.YELLOW if total_metrics['avg_f1_score'] >= 0.7 else Colors.RED
    print(f"  F1-Score médio ajustado: {avg_f1_color}{total_metrics['avg_f1_score']:.4f} ({total_metrics['avg_f1_score']*100:.2f}%){Colors.ENDC}")
    print(f"  Precision média: {total_metrics['avg_precision']:.4f} ({total_metrics['avg_precision']*100:.2f}%)")
    print(f"  Recall médio: {total_metrics['avg_recall']:.4f} ({total_metrics['avg_recall']*100:.2f}%)")
    print(f"  Similaridade média: {total_metrics['avg_similarity']:.4f} ({total_metrics['avg_similarity']*100:.2f}%)")
    
    # Mostra problemas por categoria
    problematic_files = [r for r in all_results if r['quality_issues']]
    if problematic_files:
        print(f"\n{Colors.CYAN}Arquivos com Problemas de Qualidade:{Colors.ENDC}")
        for result in sorted(problematic_files, key=lambda x: x['adjusted_f1_score'])[:10]:
            issues_str = ', '.join(result['quality_issues'])
            f1_color = Colors.YELLOW if result['adjusted_f1_score'] >= 0.7 else Colors.RED
            print(f"  {result['scenario']}: {f1_color}F1={result['adjusted_f1_score']:.4f}{Colors.ENDC} | {issues_str}")
    
    # Mostra os piores casos
    print(f"\n{Colors.CYAN}Arquivos com menor qualidade (Top 10):{Colors.ENDC}")
    worst_results = sorted(all_results, key=lambda x: x['adjusted_f1_score'])[:10]
    for i, result in enumerate(worst_results, 1):
        f1_color = Colors.YELLOW if result['adjusted_f1_score'] >= 0.7 else Colors.RED
        match_info = f" (match: {result['match_score']:.3f})" if result['match_score'] < 1.0 else ""
        print(f"  {i}. {result['scenario']}: {f1_color}F1={result['adjusted_f1_score']:.4f}{Colors.ENDC}{match_info}")
    
    # Salva relatório completo
    if output_dir:
        # Adiciona informações de correspondência ao relatório
        enhanced_report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'directories': {
                'merge': merge_dir,
                'expected': expected_dir
            },
            'file_extensions': scanner.file_extensions,
            'correspondence_stats': match_stats,
            'all_correspondences': correspondences,
            'summary': total_metrics,
            'detailed_results': all_results
        }
        
        json_path = os.path.join(report_dir, 'full_recursive_report.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_report, f, indent=2)
        
        # Relatório de correspondências
        correspondence_path = os.path.join(report_dir, 'file_correspondences.txt')
        with open(correspondence_path, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE CORRESPONDÊNCIAS DE ARQUIVOS\n")
            f.write("="*50 + "\n\n")
            
            for corr in correspondences:
                f.write(f"Tipo: {corr['type']}\n")
                f.write(f"Cenário: {corr['scenario']}\n")
                f.write(f"Arquivo Merge: {corr['merge_file']}\n")
                f.write(f"Arquivo Esperado: {corr['expected_file']}\n")
                f.write(f"Score de Match: {corr['match_score']:.3f}\n")
                if corr['quality_issues']:
                    f.write(f"Problemas: {', '.join(corr['quality_issues'])}\n")
                f.write("-" * 30 + "\n")
        
        print(f"\n{Colors.GREEN}✓ Relatórios detalhados salvos em: {report_dir}{Colors.ENDC}")
    
    return all_results, total_metrics, correspondences


def select_directory(prompt: str, initial_dir: str = ".") -> str:
    """Permite ao usuário navegar e selecionar um diretório"""
    current_dir = os.path.abspath(initial_dir)
    
    while True:
        print(f"\n{Colors.HEADER}{prompt}{Colors.ENDC}")
        print(f"{Colors.CYAN}Diretório atual: {current_dir}{Colors.ENDC}")
        print("-" * 60)
        
        # Lista todos os diretórios
        dirs = []
        
        try:
            # Adiciona opção de voltar ao diretório pai
            parent_dir = os.path.dirname(current_dir)
            if parent_dir != current_dir:  # Não está na raiz
                dirs.append(("📁 ..", parent_dir))
            
            # Lista subdiretórios
            items = sorted(os.listdir(current_dir))
            for item in items:
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path):
                    # Conta quantos subdiretórios existem
                    try:
                        subdir_count = len([d for d in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, d))])
                        java_count = len([f for f in os.listdir(item_path) if f.endswith('.java')])
                        info = ""
                        if subdir_count > 0:
                            info += f"{subdir_count} pastas"
                        if java_count > 0:
                            info += f" {java_count} arquivos .java" if not info else f", {java_count} arquivos .java"
                        if info:
                            dirs.append((f"📁 {item} ({info})", item_path))
                        else:
                            dirs.append((f"📁 {item}", item_path))
                    except:
                        dirs.append((f"📁 {item}", item_path))
            
            # Exibe diretórios
            print(f"\n{Colors.BLUE}DIRETÓRIOS:{Colors.ENDC}")
            if dirs:
                for i, (name, path) in enumerate(dirs):
                    print(f"{Colors.YELLOW}{i + 1:3d}{Colors.ENDC}. {name}")
            else:
                print("    (nenhum diretório)")
            
            # Opções adicionais
            print(f"\n{Colors.CYAN}OUTRAS OPÇÕES:{Colors.ENDC}")
            print(f"{Colors.YELLOW}{len(dirs) + 1:3d}{Colors.ENDC}. ✅ Selecionar este diretório")
            print(f"{Colors.YELLOW}{len(dirs) + 2:3d}{Colors.ENDC}. 💾 Digitar caminho completo")
            print(f"{Colors.YELLOW}{len(dirs) + 3:3d}{Colors.ENDC}. 🏠 Ir para diretório home")
            print(f"{Colors.YELLOW}{len(dirs) + 4:3d}{Colors.ENDC}. 🔄 Atualizar listagem")
            
            # Obtém escolha do usuário
            choice = input(f"\n{Colors.BOLD}Escolha uma opção (número): {Colors.ENDC}").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(dirs):
                    _, dir_path = dirs[choice_num - 1]
                    current_dir = dir_path
                    
                elif choice_num == len(dirs) + 1:
                    # Selecionar diretório atual
                    confirm = input(f"\n{Colors.GREEN}Confirmar seleção do diretório '{os.path.basename(current_dir)}'? (s/n): {Colors.ENDC}").strip().lower()
                    if confirm == 's':
                        return current_dir
                        
                elif choice_num == len(dirs) + 2:
                    # Digitar caminho completo
                    path = input("Digite o caminho completo do diretório: ").strip()
                    if os.path.isdir(path):
                        current_dir = os.path.abspath(path)
                    else:
                        print(f"{Colors.RED}❌ Diretório não encontrado!{Colors.ENDC}")
                        
                elif choice_num == len(dirs) + 3:
                    # Ir para home
                    current_dir = os.path.expanduser("~")
                    
                elif choice_num == len(dirs) + 4:
                    # Atualizar - apenas continua o loop
                    continue
                    
                else:
                    print(f"{Colors.RED}❌ Opção inválida!{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Por favor, digite um número!{Colors.ENDC}")
                        
        except PermissionError:
            print(f"{Colors.RED}❌ Erro: Sem permissão para acessar este diretório!{Colors.ENDC}")
            current_dir = os.path.dirname(current_dir)
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao listar diretório: {e}{Colors.ENDC}")


def find_corresponding_files(merge_dir: str, expected_dir: str) -> List[Tuple[str, str, str]]:
    """Encontra arquivos correspondentes entre dois diretórios
    
    Returns:
        Lista de tuplas (cenário, arquivo_merge, arquivo_esperado)
    """
    correspondences = []
    
    # Lista todos os subdiretórios no diretório de merge
    merge_subdirs = sorted([d for d in os.listdir(merge_dir) 
                           if os.path.isdir(os.path.join(merge_dir, d))])
    
    # Para cada subdiretório de merge, procura o correspondente no esperado
    for subdir in merge_subdirs:
        merge_subdir_path = os.path.join(merge_dir, subdir)
        expected_subdir_path = os.path.join(expected_dir, subdir)
        
        if os.path.exists(expected_subdir_path):
            # Lista arquivos .java em ambos os diretórios
            merge_files = [f for f in os.listdir(merge_subdir_path) 
                          if f.endswith('.java')]
            expected_files = [f for f in os.listdir(expected_subdir_path) 
                             if f.endswith('.java')]
            
            # Para cada arquivo no merge, procura o correspondente
            for merge_file in merge_files:
                if merge_file in expected_files:
                    merge_path = os.path.join(merge_subdir_path, merge_file)
                    expected_path = os.path.join(expected_subdir_path, merge_file)
                    correspondences.append((f"{subdir}/{merge_file}", merge_path, expected_path))
                else:
                    print(f"{Colors.YELLOW}⚠ Arquivo '{merge_file}' não encontrado no diretório esperado '{subdir}'{Colors.ENDC}")
            
            # Verifica arquivos esperados que não estão no merge
            for expected_file in expected_files:
                if expected_file not in merge_files:
                    print(f"{Colors.YELLOW}⚠ Arquivo esperado '{expected_file}' não encontrado no merge '{subdir}'{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}⚠ Diretório esperado não encontrado: {subdir}{Colors.ENDC}")
    
    return correspondences


def compare_directories(merge_dir: str, expected_dir: str, output_dir: str = None):
    """Compara todos os arquivos entre dois diretórios e gera relatório consolidado"""
    
    print(f"\n{Colors.HEADER}=== COMPARAÇÃO DE DIRETÓRIOS ==={Colors.ENDC}")
    print(f"{Colors.CYAN}Diretório de Merge: {merge_dir}{Colors.ENDC}")
    print(f"{Colors.CYAN}Diretório Esperado: {expected_dir}{Colors.ENDC}")
    
    # Encontra arquivos correspondentes
    print(f"\n{Colors.BLUE}Procurando arquivos correspondentes...{Colors.ENDC}")
    correspondences = find_corresponding_files(merge_dir, expected_dir)
    
    if not correspondences:
        print(f"{Colors.RED}❌ Nenhum arquivo correspondente encontrado!{Colors.ENDC}")
        return
    
    print(f"{Colors.GREEN}✓ Encontrados {len(correspondences)} arquivos para comparar{Colors.ENDC}")
    
    # Resultados consolidados
    all_results = []
    total_metrics = {
        'total_files': len(correspondences),
        'perfect_matches': 0,
        'high_quality': 0,  # >= 90%
        'medium_quality': 0,  # >= 70%
        'low_quality': 0,  # < 70%
        'total_precision': 0.0,
        'total_recall': 0.0,
        'total_f1_score': 0.0,
        'total_similarity': 0.0
    }
    
    # Cria diretório de saída se especificado
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(output_dir, f"comparison_report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
    
    # Compara cada par de arquivos
    print(f"\n{Colors.BLUE}Iniciando comparações...{Colors.ENDC}")
    for i, (scenario, merge_path, expected_path) in enumerate(correspondences, 1):
        print(f"\n[{i}/{len(correspondences)}] Comparando: {scenario}")
        
        comparator = MergeComparator()
        if comparator.load_files(merge_path, expected_path):
            metrics = comparator.calculate_metrics()
            
            # Adiciona informações do arquivo
            metrics['scenario'] = scenario
            metrics['merge_file'] = merge_path
            metrics['expected_file'] = expected_path
            
            # Atualiza estatísticas
            if metrics['f1_score'] == 1.0:
                total_metrics['perfect_matches'] += 1
            elif metrics['f1_score'] >= 0.9:
                total_metrics['high_quality'] += 1
            elif metrics['f1_score'] >= 0.7:
                total_metrics['medium_quality'] += 1
            else:
                total_metrics['low_quality'] += 1
            
            total_metrics['total_precision'] += metrics['precision']
            total_metrics['total_recall'] += metrics['recall']
            total_metrics['total_f1_score'] += metrics['f1_score']
            total_metrics['total_similarity'] += metrics['similarity_ratio']
            
            all_results.append(metrics)
            
            # Mostra resumo
            f1_color = Colors.GREEN if metrics['f1_score'] >= 0.9 else Colors.YELLOW if metrics['f1_score'] >= 0.7 else Colors.RED
            print(f"  F1-Score: {f1_color}{metrics['f1_score']:.4f}{Colors.ENDC} | " +
                  f"Precision: {metrics['precision']:.4f} | " +
                  f"Recall: {metrics['recall']:.4f}")
            
            # Salva diff individual se diretório de saída especificado
            if output_dir:
                diff_file = os.path.join(report_dir, f"{scenario.replace('/', '_')}_diff.txt")
                comparator.generate_diff_report(diff_file)
        else:
            print(f"  {Colors.RED}❌ Erro ao carregar arquivos{Colors.ENDC}")
    
    # Calcula médias
    if total_metrics['total_files'] > 0:
        total_metrics['avg_precision'] = total_metrics['total_precision'] / total_metrics['total_files']
        total_metrics['avg_recall'] = total_metrics['total_recall'] / total_metrics['total_files']
        total_metrics['avg_f1_score'] = total_metrics['total_f1_score'] / total_metrics['total_files']
        total_metrics['avg_similarity'] = total_metrics['total_similarity'] / total_metrics['total_files']
    
    # Exibe relatório consolidado
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}RELATÓRIO CONSOLIDADO{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Resumo da Comparação:{Colors.ENDC}")
    print(f"  Total de arquivos comparados: {total_metrics['total_files']}")
    print(f"  Correspondências perfeitas (100%): {Colors.GREEN}{total_metrics['perfect_matches']}{Colors.ENDC}")
    print(f"  Alta qualidade (≥90%): {Colors.GREEN}{total_metrics['high_quality']}{Colors.ENDC}")
    print(f"  Média qualidade (≥70%): {Colors.YELLOW}{total_metrics['medium_quality']}{Colors.ENDC}")
    print(f"  Baixa qualidade (<70%): {Colors.RED}{total_metrics['low_quality']}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Métricas Médias:{Colors.ENDC}")
    avg_f1_color = Colors.GREEN if total_metrics['avg_f1_score'] >= 0.9 else Colors.YELLOW if total_metrics['avg_f1_score'] >= 0.7 else Colors.RED
    print(f"  F1-Score médio: {avg_f1_color}{total_metrics['avg_f1_score']:.4f} ({total_metrics['avg_f1_score']*100:.2f}%){Colors.ENDC}")
    print(f"  Precision média: {total_metrics['avg_precision']:.4f} ({total_metrics['avg_precision']*100:.2f}%)")
    print(f"  Recall médio: {total_metrics['avg_recall']:.4f} ({total_metrics['avg_recall']*100:.2f}%)")
    print(f"  Similaridade média: {total_metrics['avg_similarity']:.4f} ({total_metrics['avg_similarity']*100:.2f}%)")
    
    # Mostra os piores casos
    print(f"\n{Colors.CYAN}Arquivos com menor qualidade (Top 10):{Colors.ENDC}")
    worst_results = sorted(all_results, key=lambda x: x['f1_score'])[:10]
    for i, result in enumerate(worst_results, 1):
        f1_color = Colors.YELLOW if result['f1_score'] >= 0.7 else Colors.RED
        print(f"  {i}. {result['scenario']}: {f1_color}F1={result['f1_score']:.4f}{Colors.ENDC}")
    
    # Salva relatório completo
    if output_dir:
        # Relatório JSON
        full_report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'directories': {
                'merge': merge_dir,
                'expected': expected_dir
            },
            'summary': total_metrics,
            'detailed_results': all_results
        }
        
        json_path = os.path.join(report_dir, 'full_report.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2)
        
        # Relatório em texto
        text_path = os.path.join(report_dir, 'summary_report.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE COMPARAÇÃO DE MERGE\n")
            f.write(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Diretório Merge: {merge_dir}\n")
            f.write(f"Diretório Esperado: {expected_dir}\n")
            f.write("="*60 + "\n\n")
            
            f.write("RESUMO:\n")
            f.write(f"Total de arquivos: {total_metrics['total_files']}\n")
            f.write(f"Correspondências perfeitas: {total_metrics['perfect_matches']}\n")
            f.write(f"F1-Score médio: {total_metrics['avg_f1_score']:.4f}\n\n")
            
            f.write("DETALHES POR ARQUIVO:\n")
            for result in sorted(all_results, key=lambda x: x['scenario']):
                f.write(f"\n{result['scenario']}:\n")
                f.write(f"  F1-Score: {result['f1_score']:.4f}\n")
                f.write(f"  Precision: {result['precision']:.4f}\n")
                f.write(f"  Recall: {result['recall']:.4f}\n")
        
        print(f"\n{Colors.GREEN}✓ Relatórios salvos em: {report_dir}{Colors.ENDC}")
    
    return all_results, total_metrics


def main():
    parser = argparse.ArgumentParser(
        description='Compara arquivos de merge e calcula métricas de qualidade (Versão 3.0 - Recursiva)'
    )
    parser.add_argument('-m', '--merge', help='Caminho do diretório de merge')
    parser.add_argument('-e', '--expected', help='Caminho do diretório esperado')
    parser.add_argument('-o', '--output', help='Diretório de saída para os relatórios')
    parser.add_argument('-i', '--interactive', action='store_true', 
                       help='Modo interativo para seleção de diretórios')
    parser.add_argument('--no-color', action='store_true', 
                       help='Desabilita cores no terminal')
    parser.add_argument('--extensions', nargs='*', 
                       default=['.java', '.py', '.cpp', '.c', '.h', '.hpp', '.js', '.ts', '.xml', '.json'],
                       help='Extensões de arquivo para comparar')
    
    args = parser.parse_args()
    
    # Desabilita cores se solicitado
    if args.no_color:
        Colors.disable()
    
    print(f"{Colors.HEADER}=== COMPARADOR DE MERGE COM MÉTRICAS ==={Colors.ENDC}")
    print(f"{Colors.CYAN}Versão 3.0 - Comparação Recursiva com Análise de Nomes{Colors.ENDC}")
    
    # Pergunta o que o usuário deseja fazer
    print(f"\n{Colors.BOLD}O que você deseja fazer?{Colors.ENDC}")
    print(f"{Colors.YELLOW}1{Colors.ENDC}. Comparar diretórios recursivamente (RECOMENDADO)")
    print(f"{Colors.YELLOW}2{Colors.ENDC}. Comparar diretórios (modo compatibilidade)")
    print(f"{Colors.YELLOW}3{Colors.ENDC}. Comparar arquivos individuais")
    
    choice = input(f"\n{Colors.BOLD}Escolha uma opção (1, 2 ou 3): {Colors.ENDC}").strip()
    
    if choice == '1':
        # Comparação recursiva (NOVO)
        if args.interactive or (not args.merge or not args.expected):
            print("\n📌 MODO RECURSIVO: Escaneia todos os subdiretórios automaticamente")
            print("   ✓ Detecta arquivos de conflito não resolvidos")
            print("   ✓ Encontra correspondências mesmo com nomes diferentes")
            print("   ✓ Analisa qualidade baseada em nomes de arquivos")
            
            merge_dir = select_directory("Selecione o diretório de SAÍDA (será escaneado recursivamente):")
            expected_dir = select_directory("Selecione o diretório ESPERADO (será escaneado recursivamente):")
        else:
            merge_dir = args.merge
            expected_dir = args.expected
        
        # Verifica se os diretórios existem
        if not os.path.isdir(merge_dir):
            print(f"{Colors.RED}❌ Erro: Diretório de merge não existe: {merge_dir}{Colors.ENDC}")
            return 1
            
        if not os.path.isdir(expected_dir):
            print(f"{Colors.RED}❌ Erro: Diretório esperado não existe: {expected_dir}{Colors.ENDC}")
            return 1
        
        # Pergunta sobre diretório de saída
        output_dir = args.output
        if not output_dir:
            save_report = input(f"\n{Colors.BOLD}Deseja salvar os relatórios detalhados? (s/n): {Colors.ENDC}").strip().lower()
            if save_report == 's':
                output_dir = input("Digite o diretório de saída (deixe vazio para usar './reports'): ").strip()
                if not output_dir:
                    output_dir = './reports'
        
        # Executa comparação recursiva
        compare_directories_recursive(merge_dir, expected_dir, output_dir, args.extensions)
        
    elif choice == '2':
        # Comparação de diretórios (modo antigo para compatibilidade)
        if args.interactive or (not args.merge or not args.expected):
            print("\n📌 MODO ANTIGO: Compara arquivos diretamente nos diretórios selecionados")
            print("   - Não detecta conflitos automaticamente")
            print("   - Requer nomes de arquivos exatamente iguais")
            
            merge_dir = select_directory("Selecione o diretório de SAÍDA:")
            expected_dir = select_directory("Selecione o diretório ESPERADO:")
        else:
            merge_dir = args.merge
            expected_dir = args.expected
        
        # Verifica se os diretórios existem
        if not os.path.isdir(merge_dir):
            print(f"{Colors.RED}❌ Erro: Diretório de merge não existe: {merge_dir}{Colors.ENDC}")
            return 1
            
        if not os.path.isdir(expected_dir):
            print(f"{Colors.RED}❌ Erro: Diretório esperado não existe: {expected_dir}{Colors.ENDC}")
            return 1
        
        # Pergunta sobre diretório de saída
        output_dir = args.output
        if not output_dir:
            save_report = input(f"\n{Colors.BOLD}Deseja salvar os relatórios detalhados? (s/n): {Colors.ENDC}").strip().lower()
            if save_report == 's':
                output_dir = input("Digite o diretório de saída (deixe vazio para usar './reports'): ").strip()
                if not output_dir:
                    output_dir = './reports'
        
        # Executa comparação normal
        compare_directories(merge_dir, expected_dir, output_dir)
        
    elif choice == '3':
        # Comparação de arquivos individuais
        from pathlib import Path
        
        if args.interactive or (not args.merge or not args.expected):
            merge_path = select_file("Selecione o arquivo de MERGE:", file_filter='.java')
            expected_path = select_file("Selecione o arquivo ESPERADO:", file_filter='.java')
        else:
            merge_path = args.merge
            expected_path = args.expected
        
        # Cria o comparador
        comparator = MergeComparator()
        
        # Carrega os arquivos
        print(f"\nCarregando arquivos...")
        print(f"Merge: {merge_path}")
        print(f"Esperado: {expected_path}")
        
        if not comparator.load_files(merge_path, expected_path):
            print("Erro ao carregar arquivos!")
            return 1
        
        # Calcula métricas
        print("\nCalculando métricas...")
        metrics = comparator.calculate_metrics()
        
        # Exibe resultados
        print("\n" + "="*50)
        print(f"{Colors.HEADER}MÉTRICAS DE COMPARAÇÃO{Colors.ENDC}")
        print("="*50)
        
        print(f"\n{Colors.CYAN}Informações dos arquivos:{Colors.ENDC}")
        print(f"  Total de linhas (esperado): {metrics['total_expected_lines']}")
        print(f"  Total de linhas (merge): {metrics['total_merge_lines']}")
        print(f"  Linhas corretas: {Colors.GREEN}{metrics['correct_lines']}{Colors.ENDC}")
        print(f"  Linhas extras: {Colors.YELLOW}{metrics['extra_lines']}{Colors.ENDC}")
        print(f"  Linhas faltando: {Colors.RED}{metrics['missing_lines']}{Colors.ENDC}")
        
        print(f"\n{Colors.CYAN}Métricas de qualidade:{Colors.ENDC}")
        # Colorir métricas baseado no valor
        precision_color = Colors.GREEN if metrics['precision'] >= 0.9 else Colors.YELLOW if metrics['precision'] >= 0.7 else Colors.RED
        recall_color = Colors.GREEN if metrics['recall'] >= 0.9 else Colors.YELLOW if metrics['recall'] >= 0.7 else Colors.RED
        f1_color = Colors.GREEN if metrics['f1_score'] >= 0.9 else Colors.YELLOW if metrics['f1_score'] >= 0.7 else Colors.RED
        
        print(f"  Precision: {precision_color}{metrics['precision']:.4f} ({metrics['precision']*100:.2f}%){Colors.ENDC}")
        print(f"  Recall: {recall_color}{metrics['recall']:.4f} ({metrics['recall']*100:.2f}%){Colors.ENDC}")
        print(f"  F1-Score: {f1_color}{metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%){Colors.ENDC}")
        print(f"  Taxa de erro: {metrics['error_rate']:.4f} ({metrics['error_rate']*100:.2f}%)")
        
        print(f"\n{Colors.CYAN}Métricas de similaridade:{Colors.ENDC}")
        sim_color = Colors.GREEN if metrics['similarity_ratio'] >= 0.9 else Colors.YELLOW if metrics['similarity_ratio'] >= 0.7 else Colors.RED
        acc_color = Colors.GREEN if metrics['line_order_accuracy'] >= 0.9 else Colors.YELLOW if metrics['line_order_accuracy'] >= 0.7 else Colors.RED
        
        print(f"  Similaridade geral: {sim_color}{metrics['similarity_ratio']:.4f} ({metrics['similarity_ratio']*100:.2f}%){Colors.ENDC}")
        print(f"  Acurácia (ordem das linhas): {acc_color}{metrics['line_order_accuracy']:.4f} ({metrics['line_order_accuracy']*100:.2f}%){Colors.ENDC}")
    
    else:
        print(f"{Colors.RED}❌ Opção inválida!{Colors.ENDC}")
        return 1
    
    return 0


def select_file(prompt: str, initial_dir: str = ".", file_filter: str = None) -> str:
    """Permite ao usuário navegar por diretórios e selecionar um arquivo"""
    current_dir = os.path.abspath(initial_dir)
    
    while True:
        print(f"\n{Colors.HEADER}{prompt}{Colors.ENDC}")
        print(f"{Colors.CYAN}Diretório atual: {current_dir}{Colors.ENDC}")
        if file_filter:
            print(f"{Colors.YELLOW}Filtro ativo: *{file_filter}{Colors.ENDC}")
        print("-" * 60)
        
        # Lista todos os itens no diretório
        dirs = []
        files = []
        
        try:
            # Adiciona opção de voltar ao diretório pai
            parent_dir = os.path.dirname(current_dir)
            if parent_dir != current_dir:  # Não está na raiz
                dirs.append(("📁 ..", parent_dir))
            
            # Lista e separa diretórios e arquivos
            items = sorted(os.listdir(current_dir))
            for item in items:
                item_path = os.path.join(current_dir, item)
                if os.path.isdir(item_path):
                    dirs.append((f"📁 {item}", item_path))
                elif os.path.isfile(item_path):
                    # Aplica filtro se especificado
                    if file_filter and not item.endswith(file_filter):
                        continue
                        
                    # Mostra tamanho do arquivo
                    size = os.path.getsize(item_path)
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                    files.append((f"📄 {item} ({size_str})", item_path))
            
            # Exibe diretórios primeiro
            all_items = []
            print(f"\n{Colors.BLUE}DIRETÓRIOS:{Colors.ENDC}")
            if dirs:
                for i, (name, path) in enumerate(dirs):
                    print(f"{Colors.YELLOW}{i + 1:3d}{Colors.ENDC}. {name}")
                    all_items.append(('dir', path))
            else:
                print("    (nenhum diretório)")
            
            # Exibe arquivos
            print(f"\n{Colors.GREEN}ARQUIVOS:{Colors.ENDC}")
            if files:
                for i, (name, path) in enumerate(files, len(dirs) + 1):
                    print(f"{Colors.YELLOW}{i:3d}{Colors.ENDC}. {name}")
                    all_items.append(('file', path))
            else:
                print("    (nenhum arquivo)")
                if file_filter:
                    print(f"    {Colors.YELLOW}(nenhum arquivo {file_filter} encontrado){Colors.ENDC}")
            
            # Opções adicionais
            print(f"\n{Colors.CYAN}OUTRAS OPÇÕES:{Colors.ENDC}")
            print(f"{Colors.YELLOW}{len(all_items) + 1:3d}{Colors.ENDC}. 💾 Digitar caminho completo")
            print(f"{Colors.YELLOW}{len(all_items) + 2:3d}{Colors.ENDC}. 🏠 Ir para diretório home")
            print(f"{Colors.YELLOW}{len(all_items) + 3:3d}{Colors.ENDC}. 🔄 Atualizar listagem")
            print(f"{Colors.YELLOW}{len(all_items) + 4:3d}{Colors.ENDC}. 🔍 Alterar/remover filtro de arquivo")
            
            # Obtém escolha do usuário
            choice = input(f"\n{Colors.BOLD}Escolha uma opção (número): {Colors.ENDC}").strip()
            
            if choice.isdigit():
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(all_items):
                    item_type, item_path = all_items[choice_num - 1]
                    if item_type == 'dir':
                        current_dir = item_path
                    else:  # é um arquivo
                        confirm = input(f"\n{Colors.GREEN}Confirmar seleção do arquivo '{os.path.basename(item_path)}'? (s/n): {Colors.ENDC}").strip().lower()
                        if confirm == 's':
                            return item_path
                            
                elif choice_num == len(all_items) + 1:
                    # Digitar caminho completo
                    path = input("Digite o caminho completo do arquivo: ").strip()
                    if os.path.isfile(path):
                        return path
                    elif os.path.isdir(path):
                        current_dir = os.path.abspath(path)
                    else:
                        print(f"{Colors.RED}❌ Caminho não encontrado!{Colors.ENDC}")
                        
                elif choice_num == len(all_items) + 2:
                    # Ir para home
                    current_dir = os.path.expanduser("~")
                    
                elif choice_num == len(all_items) + 3:
                    # Atualizar - apenas continua o loop
                    continue
                    
                elif choice_num == len(all_items) + 4:
                    # Alterar filtro
                    print(f"\n{Colors.CYAN}Exemplos de filtros: .java, .py, .txt, .xml{Colors.ENDC}")
                    new_filter = input("Digite a extensão para filtrar (deixe vazio para remover filtro): ").strip()
                    file_filter = new_filter if new_filter else None
                    
                else:
                    print(f"{Colors.RED}❌ Opção inválida!{Colors.ENDC}")
            else:
                print(f"{Colors.RED}❌ Por favor, digite um número!{Colors.ENDC}")
                        
        except PermissionError:
            print(f"{Colors.RED}❌ Erro: Sem permissão para acessar este diretório!{Colors.ENDC}")
            current_dir = os.path.dirname(current_dir)
        except Exception as e:
            print(f"{Colors.RED}❌ Erro ao listar diretório: {e}{Colors.ENDC}")


if __name__ == "__main__":
    sys.exit(main())