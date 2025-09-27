# DeepSeek V3 Quantization Comparison Results

**Generated**: 2025-09-27 20:47:31

## 🎯 Executive Summary

### Key Findings
- **FP16**: 4.8 tok/s average, 6101MB GPU usage
- **Q4_0**: 2.9 tok/s average, 6101MB GPU usage
- **Q8_0**: 2.1 tok/s average, 9219MB GPU usage
- **Q4_0 vs Q8_0**: 39.9% speed improvement, 33.8% memory reduction
- **Q4_0 vs FP16**: -40.0% speed change, 0.0% memory reduction

## 📊 Detailed Performance Data

### Category-wise Comparison

| Category | FP16 Speed | FP16 GPU | Q4_0 Speed | Q4_0 GPU | Q8_0 Speed | Q8_0 GPU |
|----------|------------|-----------|------------|-----------|------------|-----------|
| コード生成 | 6.0 tok/s | 6101MB | 5.4 tok/s | 6101MB | 3.5 tok/s | 9219MB |
| 問題解決 | 1.0 tok/s | 6101MB | 0.7 tok/s | 6101MB | 0.5 tok/s | 9219MB |
| 技術解説 | 1.5 tok/s | 6101MB | 1.3 tok/s | 6101MB | 0.7 tok/s | 9219MB |
| 数学・論理 | 10.9 tok/s | 6101MB | 4.2 tok/s | 6101MB | 3.5 tok/s | 9219MB |

### Performance Comparison Chart

![Performance Comparison](performance_charts.png)

## 💡 Practical Recommendations

### FP16 (Full Precision) Recommended Use Cases
- ✅ Maximum quality requirements
- ✅ Research & academic work
- ✅ Production-critical applications
- ✅ When GPU memory is abundant (>12GB)

### Q8_0 Recommended Use Cases
- ✅ High-quality code generation & review
- ✅ Technical documentation writing
- ✅ Balance between quality and efficiency
- ✅ Medium GPU memory systems (8-12GB)

### Q4_0 Recommended Use Cases
- ✅ Daily development & learning assistance
- ✅ Fast iterative tasks
- ✅ Multi-application concurrent usage
- ✅ Lower GPU memory systems (6-8GB)

## 📈 Data Quality & Statistics

- **Total Tests**: 20
- **Successful Tests**: 20
- **Success Rate**: 100.0%
- **Test Categories**: 4 types

## 📄 Raw Data

- [CSV Numerical Data](quantization_comparison_log.csv)
- [Detailed Evaluation Report](quantization_evaluation.md)

## 🛠️ Experiment Environment

- **GPU**: NVIDIA GeForce RTX 4060 Ti 16GB
- **OS**: Windows 11
- **Inference Engine**: Ollama
- **Quantization Levels**: FP16, Q4_0, Q8_0
- **Model Format**: GGUF
- **Measurement Method**: Single execution per test, nvidia-smi monitoring

