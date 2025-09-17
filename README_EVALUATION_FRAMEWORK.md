# Scientific Merge Tool Evaluation Framework

Uma ferramenta robusta e cientificamente rigorosa para avaliar e comparar ferramentas de merge em desenvolvimento de software. Este framework segue as melhores práticas de engenharia de software empírica e fornece análises estatisticamente válidas para pesquisa acadêmica.

## 🎯 Objetivo

Este framework foi desenvolvido para proporcionar uma avaliação abrangente e cientificamente rigorosa de ferramentas de merge, incluindo:

- **Análise Quantitativa:** Métricas precisas de desempenho (precisão, recall, F1-score)
- **Validação Estatística:** Testes de significância e medidas de tamanho de efeito
- **Classificação de Qualidade:** Sistema estruturado de classificação de resultados
- **Relatórios Científicos:** Documentação adequada para publicação acadêmica

## 📋 Características Principais

### ✅ Métricas Científicas
- **Precisão:** Proporção de linhas corretamente mergeadas
- **Recall:** Cobertura do conteúdo esperado
- **F1-Score:** Média harmônica entre precisão e recall
- **Acurácia:** Correção linha-por-linha considerando ordem
- **Integridade Estrutural:** Análise de correção sintática
- **Classificação de Qualidade:** Sistema de 6 níveis (Perfect → Failed)

### ✅ Rigor Estatístico
- **Testes de Significância:** Mann-Whitney U, Wilcoxon, Kruskal-Wallis
- **Tamanho de Efeito:** Cliff's Delta e Cohen's d
- **Intervalos de Confiança:** 95% CI com bootstrap
- **Correção para Múltiplas Comparações:** Bonferroni
- **Detecção de Outliers:** Identificação automática de valores atípicos

### ✅ Análise de Erros
- **Classificação Sistemática:** Tipos de erros estruturados
- **Análise de Falhas:** Padrões de falha por ferramenta
- **Detecção de Conflitos:** Identificação de marcadores não resolvidos
- **Validação Sintática:** Verificação de correção estrutural

### ✅ Relatórios Profissionais
- **Formato Científico:** Relatórios em Markdown para publicação
- **Tabelas Estatísticas:** Resultados formatados profissionalmente
- **Análise Comparativa:** Comparação detalhada entre ferramentas
- **Reprodutibilidade:** Informações completas para replicação

## 🏗️ Estrutura do Projeto

```
projeto/
├── merge_evaluation_tool.py          # Framework principal de avaliação
├── run_evaluation.py                 # Script de execução simplificado
├── scientific_report_generator.py    # Gerador de relatórios científicos
├── evaluation_config.py              # Configurações e parâmetros
├── output/                           # Resultados das ferramentas de merge
│   ├── IntelliMerge/
│   │   ├── scenarios/               # Outputs da ferramenta
│   │   └── expected/                # Resultados esperados
│   ├── JDime/
│   └── FSTMerge/
└── scientific_evaluation_results/    # Resultados da avaliação
    ├── tools_comparison.json
    ├── IntelliMerge/
    ├── JDime/
    └── FSTMerge/
```

## 🚀 Como Usar

### 1. Preparação do Ambiente

```bash
# Clonar o repositório
git clone <repository-url>
cd Pesquisa-cientifica

# Instalar dependências Python
pip install pandas numpy scipy tabulate

# Verificar estrutura de diretórios
python run_evaluation.py --check-only
```

### 2. Execução da Avaliação

#### Avaliação Automática (Recomendado)
```bash
# Detecta automaticamente todas as ferramentas disponíveis
python run_evaluation.py

# Com saída detalhada
python run_evaluation.py --verbose
```

#### Avaliação de Ferramentas Específicas
```bash
# Avaliar apenas IntelliMerge e JDime
python run_evaluation.py --tools IntelliMerge JDime

# Especificar diretório de saída
python run_evaluation.py --output-dir meus_resultados
```

#### Execução Direta do Framework
```bash
# Comando completo
python merge_evaluation_tool.py \
    --tools IntelliMerge JDime FSTMerge \
    --scenarios-base output \
    --expected-base output \
    --output-dir scientific_evaluation_results \
    --extensions .java \
    --verbose
```

### 3. Geração de Relatórios Científicos

```bash
# Gerar relatório científico completo
python scientific_report_generator.py \
    --results-dir scientific_evaluation_results \
    --output-file relatorio_cientifico.md

# Apenas visualizar resumo dos resultados existentes
python run_evaluation.py --summary-only
```

## 📊 Estrutura dos Resultados

### Métricas por Cenário (`scenario_metrics.csv`)
```csv
scenario_id,tool_name,file_name,precision,recall,f1_score,accuracy,
total_lines_expected,total_lines_actual,lines_correctly_merged,
syntactic_correctness,structural_integrity,quality_class,...
```

### Relatório de Avaliação (`evaluation_report.json`)
```json
{
  "tool_name": "IntelliMerge",
  "total_scenarios": 41,
  "overall_f1_score": 0.8523,
  "overall_precision": 0.8441,
  "overall_recall": 0.8607,
  "success_rate": 0.8293,
  "perfect_merges": 15,
  "failed_merges": 3,
  "statistical_summary": {...},
  "scenario_metrics": [...]
}
```

### Comparação entre Ferramentas (`tools_comparison.json`)
```json
{
  "performance_ranking": [
    {"rank": 1, "tool_name": "JDime", "overall_f1_score": 0.8523},
    {"rank": 2, "tool_name": "IntelliMerge", "overall_f1_score": 0.7854}
  ],
  "statistical_significance": {...},
  "quality_distribution": {...}
}
```

## 📈 Interpretação dos Resultados

### Classificação de Qualidade
- **Perfect (1.0):** Correspondência exata com o resultado esperado
- **Excellent (≥0.95):** Qualidade excelente, desvios mínimos
- **Good (≥0.85):** Boa qualidade, pequenos ajustes necessários
- **Acceptable (≥0.70):** Qualidade aceitável, alguns problemas
- **Poor (≥0.50):** Qualidade baixa, muitos problemas
- **Failed (<0.50):** Falha significativa no merge

### Métricas de Desempenho
- **F1-Score:** Métrica principal, balanço entre precisão e recall
- **Success Rate:** Porcentagem de merges com F1 ≥ 0.70
- **Reliability Score:** Consistência dos resultados
- **Consistency Score:** Baixa variabilidade entre cenários

### Significância Estatística
- **p-value < 0.05:** Diferença estatisticamente significativa
- **Effect Size:** Magnitude prática da diferença
  - Small (δ < 0.147), Medium (0.147 ≤ δ < 0.33), Large (δ ≥ 0.33)

## 🔬 Metodologia Científica

### Abordagem Experimental
- **Tipo de Estudo:** Comparação empírica quantitativa
- **Variáveis Independentes:** Ferramentas de merge
- **Variáveis Dependentes:** Métricas de qualidade do merge
- **Controles:** Cenários padronizados, configurações padrão
- **Validação:** Ground truth estabelecido por especialistas

### Rigor Estatístico
- **Testes Não-Paramétricos:** Apropriados para distribuições não-normais
- **Correção Bonferroni:** Controle de erro tipo I em múltiplas comparações
- **Bootstrap:** Intervalos de confiança robustos
- **Tamanho de Amostra:** Justificado por análise de poder

### Ameaças à Validade
- **Validade de Construto:** Múltiplas métricas, validação cruzada
- **Validade Interna:** Ambiente controlado, configurações padronizadas
- **Validade Externa:** Cenários diversificados, representativos
- **Validade de Conclusão:** Métodos estatísticos apropriados

## 🛠️ Configuração Avançada

### Personalização de Métricas
Edite `evaluation_config.py` para ajustar:
- Thresholds de qualidade
- Pesos das métricas
- Parâmetros estatísticos
- Configurações específicas por ferramenta

### Extensão para Novas Linguagens
O framework suporta extensão para outras linguagens:
1. Adicione extensões em `SUPPORTED_EXTENSIONS`
2. Implemente análise estrutural específica
3. Ajuste padrões de normalização

### Adição de Novas Ferramentas
Para avaliar novas ferramentas:
1. Crie diretórios `output/NovaTool/scenarios/` e `expected/`
2. Execute as ferramentas nos cenários base
3. Execute a avaliação normalmente

## 📝 Exemplos de Uso

### Exemplo 1: Avaliação Completa
```bash
# Verificar estrutura
python run_evaluation.py --check-only

# Executar avaliação completa
python run_evaluation.py --verbose

# Gerar relatório científico
python scientific_report_generator.py
```

### Exemplo 2: Comparação Específica
```bash
# Comparar apenas duas ferramentas
python run_evaluation.py --tools IntelliMerge JDime --verbose

# Analisar apenas resultados existentes
python run_evaluation.py --summary-only
```

### Exemplo 3: Personalização
```bash
# Diretório personalizado
python run_evaluation.py --output-dir estudo_caso_2025

# Relatório personalizado
python scientific_report_generator.py \
    --results-dir estudo_caso_2025 \
    --output-file relatorio_final.md
```

## 🔧 Resolução de Problemas

### Problemas Comuns

1. **"No merge tools with complete data found!"**
   - Verifique se existem diretórios `output/[Tool]/scenarios/` e `expected/`
   - Certifique-se de que contêm arquivos de cenários

2. **"Evaluation failed with return code X"**
   - Execute com `--verbose` para mais detalhes
   - Verifique permissões de arquivo e espaço em disco

3. **"Results directory not found"**
   - Execute a avaliação antes de gerar relatórios
   - Verifique o caminho do diretório de resultados

### Logs e Depuração
- Logs detalhados em `merge_evaluation.log`
- Use `--verbose` para saída detalhada
- Verifique `scientific_evaluation_results/` para resultados intermediários

## 📊 Saída de Exemplo

```
📊 PERFORMANCE RANKING:
----------------------------------------
1. JDime
   F1-Score: 0.8523 | Success Rate: 0.8293 | Reliability: 0.7854
2. IntelliMerge  
   F1-Score: 0.7854 | Success Rate: 0.7317 | Reliability: 0.7231
3. FSTMerge
   F1-Score: 0.6892 | Success Rate: 0.6341 | Reliability: 0.6108

🎯 QUALITY DISTRIBUTION:
----------------------------------------
JDime:
  Perfect: 36.59% | Excellent: 4.88%
  Good: 17.07% | Acceptable: 21.95%
  Poor: 12.20% | Failed: 7.32%
```

## 📚 Publicação e Citação

Este framework foi desenvolvido seguindo padrões de pesquisa acadêmica em engenharia de software empírica. Os relatórios gerados incluem:

- Metodologia detalhada
- Análise estatística rigorosa
- Discussão de ameaças à validade
- Informações de reprodutibilidade
- Formato adequado para publicação

### Estrutura do Relatório Científico
1. Abstract e Introdução
2. Metodologia e Setup Experimental
3. Resultados e Análise Estatística
4. Discussão e Implicações Práticas
5. Ameaças à Validade
6. Conclusão e Trabalhos Futuros
7. Apêndices com Dados Completos

## 🤝 Contribuições

Para contribuir com melhorias:
1. Fork do repositório
2. Implemente melhorias seguindo padrões científicos
3. Adicione testes apropriados
4. Submeta pull request com documentação

## 📄 Licença

Este projeto é desenvolvido para fins acadêmicos e de pesquisa. Cite apropriadamente quando usado em publicações científicas.

---

**Desenvolvido para pesquisa científica em engenharia de software empírica**  
*Versão 1.0.0 - Framework de Avaliação Científica de Ferramentas de Merge*
