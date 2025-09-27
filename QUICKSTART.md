# 🚀 Quick Start: 5-Minute DeepSeek V3 Quantization Analysis

Fastest setup guide for 16GB GPU quantization performance comparison.

## ✅ Prerequisites Check (2 minutes)

```powershell
# 1. GPU verification
nvidia-smi  # Should show 16GB VRAM

# 2. Python version check
python --version  # Requires 3.8+

# 3. Ollama check (auto-install if missing)
ollama --version
```

## ⚡ Automatic Setup (3 minutes)

### Windows (Recommended)
```powershell
# Navigate to project directory
cd c:\Users\yasun\LLM\takato-llm-comparison

# Run automated setup
.\setup.bat
```

### Manual Setup
```powershell
# 1. Python environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 2. Install Ollama
winget install Ollama.Ollama

# 3. Download quantization models (choose based on your needs)
ollama pull deepseek-coder:6.7b-instruct      # FP16 - Research quality
ollama pull deepseek-coder:6.7b-instruct-q8_0 # Q8_0 - Production balance  
ollama pull deepseek-coder:6.7b-instruct-q4_0 # Q4_0 - Daily development
```

## 🧪 Instant Quantization Testing

### 1. Quick Single Model Test
```powershell
# Test FP16 (Full Precision)
ollama run deepseek-coder:6.7b-instruct "Write a Python quicksort function"

# Test Q8_0 (8-bit)
ollama run deepseek-coder:6.7b-instruct-q8_0 "Write a Python quicksort function"

# Test Q4_0 (4-bit)  
ollama run deepseek-coder:6.7b-instruct-q4_0 "Write a Python quicksort function"
```

### 2. Full 3-Level Comparison (10 minutes)
```powershell
# Run comprehensive quantization analysis
python scripts\quantization_comparison.py

# Generate professional report with charts
python scripts\generate_github_report.py

# View results
type results\RESULTS.md
start results\performance_charts.png
```

## 📊 Understanding Results (Based on Our Research)

### Performance Summary
```
Quantization | Speed    | Memory   | Best Use Case
-------------|----------|----------|----------------
FP16         | 4.8 tok/s| 6,101MB  | Research/Academic
Q8_0         | 2.1 tok/s| 9,219MB  | Production Quality
Q4_0         | 2.9 tok/s| 6,101MB  | Daily Development
```

### CSV Output Format
```csv
model,quantization,prompt_id,category,latency_ms,tokens_per_second,gpu_memory_used_mb,success
deepseek-fp16,FP16,quant_001,コード生成,15321.3,6.0,6101,True
deepseek-q8,Q8_0,quant_001,コード生成,21908.3,3.7,9219,True
deepseek-q4,Q4_0,quant_001,コード生成,10808.0,4.9,6101,True
```

### Key Insights from Our Testing

**🔍 Surprising Findings:**
- **FP16 is memory-efficient**: Only 6,101MB (same as Q4_0!)
- **Q8_0 uses most memory**: 9,219MB despite being "8-bit"
- **Q4_0 balanced performance**: Good speed with minimal memory

**⚡ Speed Champions by Task:**
- **Math & Logic**: FP16 dominates (10.9 tok/s)
- **Code Generation**: FP16 leads (6.0 tok/s), Q4_0 close (5.4 tok/s)
- **General Tasks**: Q4_0 offers best speed/memory ratio

## 🔧 Troubleshooting

### GPU Not Detected
```powershell
# Check NVIDIA GPU
nvidia-smi

# Verify CUDA installation
nvcc --version

# Set Ollama GPU optimization
$env:OLLAMA_GPU_LAYERS = "35"
$env:OLLAMA_NUM_PARALLEL = "1"
```

### Memory Issues
```powershell
# If running out of VRAM, try single model:
ollama pull deepseek-coder:6.7b-instruct-q4_0  # Only Q4_0 (3.8GB)

# Monitor GPU usage during inference
nvidia-smi -l 1
```

### Model Download Problems
```powershell
# Check disk space (models are large)
dir C:\ | findstr "free"

# Retry download with verification
ollama pull deepseek-coder:6.7b-instruct --insecure
```

## 📈 Professional Results Output

After running the comparison, you'll get:

1. **RESULTS.md**: Publication-ready analysis report
2. **performance_charts.png**: Professional performance visualizations  
3. **quantization_comparison_log.csv**: Raw data for further analysis

Perfect for:
- 📝 Technical blog posts
- 🎓 Academic research
- 💼 Corporate AI strategy decisions
- 🚀 GitHub portfolio projects

## 🎯 Next Steps

1. **Run full comparison**: `python scripts\quantization_comparison.py`
2. **Analyze results**: Review `results\RESULTS.md`
3. **Customize tests**: Edit `templates\test_prompts.json`
4. **Share findings**: Results are ready for publication!

---

*Optimized for RTX 4060 Ti 16GB | Tested on Windows 11 | Based on real performance data*
