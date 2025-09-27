# LLM Model Comparison Analysis

A comprehensive comparison framework for **DeepSeek V3**, **Qwen2.5**, and quantization analysis on 16GB GPU environments.

## 🎯 Latest Research Results Summary

### 🏆 Multi-Model Performance Comparison (September 2025)

Based on our comprehensive testing on RTX 4060 Ti 16GB:

| Model | Quantization | Speed (tok/s) | GPU Memory | Quality Score | Best Use Case |
|-------|--------------|---------------|------------|---------------|---------------|
| **🥇 Qwen2.5-7B** | Default | **22.7** | 14,074MB | **0.55/1.0** | **Overall Best Performance** |
| **🥈 DeepSeek Q4_0** | Q4_0 | 13.0 | **6,099MB** | 0.47/1.0 | **Memory Efficient** |
| DeepSeek Q8_0 | Q8_0 | 7.9 | 9,217MB | 0.51/1.0 | Balanced Quality |

### 🔍 Major Discoveries
- **🚀 Qwen2.5-7B dominates**: 75% faster than DeepSeek Q4_0, 187% faster than Q8_0
- **💎 Quality leadership**: Qwen2.5 achieves highest response quality (0.55/1.0)  
- **⚖️ Memory efficiency**: DeepSeek Q4_0 uses 57% less VRAM than Qwen2.5
- **🎯 Best overall value**: Qwen2.5 offers 1.25 quality-speed balance vs 0.61 for DeepSeek

### 📊 DeepSeek Quantization Results

| Quantization | Inference Speed | GPU Memory | Best Use Case |
|--------------|-----------------|------------|---------------|
| **FP16** | 4.8 tok/s | 6,101MB | Research, maximum quality |
| **Q8_0** | 2.1 tok/s | 9,219MB | Production, balanced quality |
| **Q4_0** | 2.9 tok/s | 6,101MB | Daily development, speed focus |

### 🔍 Quantization Key Findings
- **Q4_0 vs Q8_0**: 39.9% speed improvement, 33.8% memory reduction
- **FP16 surprise**: Most memory-efficient for quality (only 6,101MB)
- **Q8_0 memory usage**: Highest at 9,219MB despite being 8-bit

## 🧩 Hardware Requirements
- **GPU**: 16GB VRAM (RTX 4060 Ti, RTX 4080, A4000, eGPU)
- **CPU**: Ryzen 7 / Intel i7+
- **RAM**: 16GB+ recommended
- **Storage**: SSD recommended

## 📥 Model Setup

### Multi-Model Comparison Suite
```powershell
# Qwen2.5-7B - Overall Best Performance
ollama pull qwen2.5:7b

# DeepSeek Coder - All Quantization Levels  
ollama pull deepseek-coder:6.7b-instruct      # FP16 (Full Precision)
ollama pull deepseek-coder:6.7b-instruct-q8_0 # Q8_0 (8-bit) 
ollama pull deepseek-coder:6.7b-instruct-q4_0 # Q4_0 (4-bit)
```

### Recommended Model Selection by Use Case
```powershell
# Maximum Performance (22.7 tok/s)
ollama pull qwen2.5:7b

# Memory Efficient Development (6GB VRAM)  
ollama pull deepseek-coder:6.7b-instruct-q4_0

# Research & Quality (6GB VRAM, highest accuracy)
ollama pull deepseek-coder:6.7b-instruct
```

## 🛠️ Quick Setup

```powershell
# 1. Clone repository
git clone <repository-url>
cd takato-llm-comparison

# 2. Python environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Install Ollama (if needed)
winget install Ollama.Ollama

# 4. Download models (recommended combination)
ollama pull qwen2.5:7b                         # Best overall performance
ollama pull deepseek-coder:6.7b-instruct-q4_0  # Memory efficient
ollama pull deepseek-coder:6.7b-instruct        # Research quality
```

## 📊 Running Comparisons

### Multi-Model Comprehensive Comparison
```powershell
# Qwen2.5 vs DeepSeek comprehensive analysis  
python scripts/qwen25_vs_deepseek_comparison.py

# Original DeepSeek quantization analysis
python scripts/quantization_comparison.py

# Generate professional reports and charts
python scripts/generate_github_report.py
```

### Single Model Quick Test
```powershell
# Test specific model
python scripts/deepseek_quick_test.py
```

## 📁 Project Structure

```
takato-llm-comparison/
├── README.md                           # This file  
├── QUICKSTART.md                       # 5-minute setup guide
├── requirements.txt                    # Python dependencies
├── scripts/                           # Analysis scripts
│   ├── qwen25_vs_deepseek_comparison.py # NEW: Multi-model comparison
│   ├── quantization_comparison.py     # DeepSeek 3-level comparison
│   ├── int4_quantization_comparison.py # INT4 quantization analysis
│   ├── generate_github_report.py      # Professional reporting  
│   ├── deepseek_quick_test.py         # Quick single tests
│   └── deepseek_evaluation.py         # Legacy single model
├── templates/                         # Test prompts
│   ├── prompt_template.txt           
│   └── test_prompts.json             
├── results/                          # Generated results
│   ├── qwen25_vs_deepseek_*.csv      # NEW: Multi-model results
│   ├── qwen25_vs_deepseek_*.json     # NEW: Detailed comparison data
│   ├── qwen25_vs_deepseek_*.png      # NEW: Performance charts
│   ├── RESULTS.md                    # DeepSeek quantization analysis
│   ├── performance_charts.png        # DeepSeek visual comparisons
│   ├── quantization_comparison_log.csv # Raw performance data
│   └── quantization_evaluation.md    # Detailed evaluation
└── config/                           # Configuration
    └── q4_km_settings.conf           
```

## 🔧 GPU Optimization

### Ollama GPU Settings
```powershell
# Optimize for 16GB GPU
$env:OLLAMA_GPU_LAYERS = "35"
$env:OLLAMA_NUM_PARALLEL = "1"
ollama serve
```

## 📈 Performance Analysis Results

### 🎯 Multi-Model Comparison Highlights

**🏆 Overall Winner: Qwen2.5-7B**
- **Speed Champion**: 22.7 tok/s (75% faster than DeepSeek Q4_0)
- **Quality Leader**: 0.55/1.0 response quality score
- **Best Balance**: 1.25 quality-speed ratio
- **Use Case**: Maximum performance applications

**💎 Memory Efficiency Champion: DeepSeek Q4_0** 
- **VRAM Efficient**: Only 6,099MB (57% less than Qwen2.5)
- **Decent Speed**: 13.0 tok/s (still competitive)
- **Good Quality**: 0.47/1.0 quality score
- **Use Case**: Memory-constrained environments

**📊 Performance Rankings by Category:**

| Metric | 1st Place | 2nd Place | 3rd Place |
|--------|-----------|-----------|-----------|
| **Speed** | Qwen2.5 (22.7 tok/s) | DeepSeek Q4_0 (13.0) | DeepSeek Q8_0 (7.9) |
| **Quality** | Qwen2.5 (0.55) | DeepSeek Q8_0 (0.51) | DeepSeek Q4_0 (0.47) |
| **Memory Efficiency** | DeepSeek Q4_0 (2.1 tok/s/GB) | Qwen2.5 (1.6) | DeepSeek Q8_0 (0.9) |
| **Overall Balance** | Qwen2.5 (1.25) | DeepSeek Q4_0 (0.61) | DeepSeek Q8_0 (0.40) |

### 🔍 DeepSeek Quantization Trade-offs (Legacy Analysis)

**🚀 FP16 (Full Precision)**
- **Best for**: Research, academic work, maximum quality
- **Performance**: 4.8 tok/s average
- **Memory**: 6,101MB (surprisingly efficient!)
- **Quality**: Highest accuracy, best for complex reasoning

**⚖️ Q8_0 (8-bit Quantization)** 
- **Best for**: Production environments, balanced quality
- **Performance**: 2.1 tok/s average 
- **Memory**: 9,219MB (highest consumption)
- **Quality**: High accuracy with memory trade-off

**⚡ Q4_0 (4-bit Quantization)**
- **Best for**: Daily development, rapid iteration
- **Performance**: 2.9 tok/s average
- **Memory**: 6,101MB (efficient)
- **Quality**: Good for most development tasks

### Category Performance Breakdown
| Task Type | FP16 Speed | Q4_0 Speed | Q8_0 Speed |
|-----------|------------|------------|------------|
| Code Generation | 6.0 tok/s | 5.4 tok/s | 3.5 tok/s |
| Math & Logic | 10.9 tok/s | 4.2 tok/s | 3.5 tok/s |
| Technical Explanation | 1.5 tok/s | 1.3 tok/s | 0.7 tok/s |
| Problem Solving | 1.0 tok/s | 0.7 tok/s | 0.5 tok/s |

## 🚀 Results & Publication

### Latest Multi-Model Analysis (September 2025)
- **Comprehensive Report**: `results/qwen25_vs_deepseek_comparison_*.csv`
- **Performance Charts**: `results/qwen25_vs_deepseek_charts_*.png`
- **Detailed Data**: `results/qwen25_vs_deepseek_detailed_*.json`

### Original DeepSeek Quantization Analysis
- **Professional Report**: `results/RESULTS.md`
- **Performance Charts**: `results/performance_charts.png` 
- **Raw Data**: `results/quantization_comparison_log.csv`

### Research Publications Ready
All results are automatically formatted for:
- **GitHub repositories**: Markdown tables and charts
- **Academic papers**: CSV data and statistical analysis
- **Technical blogs**: Professional visualizations
- **Industry reports**: Executive summaries

---

*Latest research conducted September 2025 on RTX 4060 Ti 16GB | Windows 11 | Ollama inference engine*  
*Qwen2.5-7B vs DeepSeek V3 comprehensive comparison completed*