from merge_metrics_analyzer import MergeMetricsAnalyzer

analyzer = MergeMetricsAnalyzer()
analyzer.load_json('IntelliMerge_detailed_result.json', 'IntelliMerge')
analyzer.print_all_tables()