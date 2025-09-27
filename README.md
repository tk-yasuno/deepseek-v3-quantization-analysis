# DeepSeek V3 Quantization Analysis

A comprehensive quantization comparison framework for **DeepSeek V3 (6.7B)** on 16GB GPU environments, supporting **FP16, Q8_0, and Q4_0** quantization levels.

## 🎯 Research Results Summary

Based on our comprehensive testing on RTX 4060 Ti 16GB:

| Quantization | Inference Speed | GPU Memory | Best Use Case |
|--------------|-----------------|------------|---------------|
| **FP16** | 4.8 tok/s | 6,101MB | Research, maximum quality |
| **Q8_0** | 2.1 tok/s | 9,219MB | Production, balanced quality |
| **Q4_0** | 2.9 tok/s | 6,101MB | Daily development, speed focus |

### 🔍 Key Findings
- **Q4_0 vs Q8_0**: 39.9% speed improvement, 33.8% memory reduction
- **FP16 surprise**: Most memory-efficient for quality (only 6,101MB)
- **Q8_0 memory usage**: Highest at 9,219MB despite being 8-bit

## 🧩 Hardware Requirements
- **GPU**: 16GB VRAM (RTX 4060 Ti, RTX 4080, A4000, eGPU)
- **CPU**: Ryzen 7 / Intel i7+
- **RAM**: 16GB+ recommended
- **Storage**: SSD recommended

## 📥 Model Setup

### All Quantization Levels
```powershell
# FP16 (Full Precision) - Research Quality
ollama pull deepseek-coder:6.7b-instruct

# Q8_0 (8-bit) - Production Balance
ollama pull deepseek-coder:6.7b-instruct-q8_0

# Q4_0 (4-bit) - Daily Development
ollama pull deepseek-coder:6.7b-instruct-q4_0
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

# 4. Download models (choose based on your needs)
ollama pull deepseek-coder:6.7b-instruct      # FP16
ollama pull deepseek-coder:6.7b-instruct-q8_0 # Q8_0  
ollama pull deepseek-coder:6.7b-instruct-q4_0 # Q4_0
```

## 📊 Running Comparisons

### Full 3-Level Quantization Comparison
```powershell
# Run comprehensive comparison (FP16, Q8_0, Q4_0)
python scripts/quantization_comparison.py

# Generate professional report and charts
python scripts/generate_github_report.py
```

### Single Model Quick Test
```powershell
# Test specific quantization level
python scripts/deepseek_quick_test.py
```

## 📁 Project Structure

```
takato-llm-comparison/
├── README.md                           # This file
├── QUICKSTART.md                       # 5-minute setup guide
├── requirements.txt                    # Python dependencies
├── scripts/                           # Analysis scripts
│   ├── quantization_comparison.py     # Main 3-level comparison
│   ├── generate_github_report.py      # Professional reporting
│   ├── deepseek_quick_test.py         # Quick single tests
│   └── deepseek_evaluation.py         # Legacy single model
├── templates/                         # Test prompts
│   ├── prompt_template.txt           
│   └── test_prompts.json             
├── results/                          # Generated results
│   ├── RESULTS.md                    # Professional analysis report
│   ├── performance_charts.png        # Visual comparisons
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

### Quantization Trade-offs (Our Research)

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

All results are automatically formatted for research publication:
- **Professional Report**: `results/RESULTS.md`
- **Performance Charts**: `results/performance_charts.png` 
- **Raw Data**: `results/quantization_comparison_log.csv`

Ready for GitHub, academic papers, or technical blogs!

## 📞 Support

For setup issues, check:
- Latest GPU drivers
- CUDA Toolkit 11.8+
- Python 3.8+
- Sufficient disk space (models: 3.8GB-7.2GB each)

---

*Research conducted on RTX 4060 Ti 16GB | Windows 11 | Ollama inference engine*