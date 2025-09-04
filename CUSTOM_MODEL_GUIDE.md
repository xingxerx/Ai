# Custom AI Model Guide

🤖 **No API Keys Required!** This AGI Agent now includes a custom local AI model that runs entirely on your machine.

## Quick Start

### 1. See the Demo (No Installation Required)
```bash
python demo_custom_model.py
```

### 2. Install Dependencies
```bash
pip install torch transformers accelerate sentencepiece
```

### 3. Run Setup
```bash
python setup_custom_model.py
```

### 4. Test the Model
```bash
python test_custom_model.py
```

### 5. Run the AGI Agent
```bash
python example.py
```

## Features

✅ **No API Keys Required** - Runs completely offline  
✅ **Privacy First** - Your data never leaves your machine  
✅ **Smart Model Selection** - Automatically chooses the best model for your system  
✅ **Multi-Platform** - Works on Windows, Mac, Linux  
✅ **Hardware Adaptive** - Supports CPU, NVIDIA GPU, Apple Silicon  
✅ **Multiple Models** - From lightweight (82MB) to powerful (1.5GB+)  
✅ **Easy Configuration** - Just set `model_provider="custom"`  

## Available Models

| Model | Size | Memory | Best For |
|-------|------|--------|----------|
| `distilgpt2` | 82MB | Low | Testing, Development |
| `microsoft/DialoGPT-small` | 117MB | Low | Fast Chat |
| `microsoft/DialoGPT-medium` | 345MB | Medium | Conversation |
| `gpt2` | 548MB | Medium | General Purpose |
| `microsoft/DialoGPT-large` | 774MB | High | Better Quality |
| `gpt2-medium` | 1.5GB | High | Advanced Reasoning |

## System Requirements

### Minimum
- Python 3.8+
- 4GB RAM
- 2GB free disk space

### Recommended
- Python 3.9+
- 8GB+ RAM
- NVIDIA GPU with 4GB+ VRAM (optional)
- 5GB+ free disk space

## Configuration

### Basic Configuration
```python
from agi_agent import AGIAgent, AgentConfig

config = AgentConfig(
    model_provider="custom",  # Use custom local model
    model_name="auto",        # Auto-select best model
    max_reasoning_depth=10,
    safety_level="high",
    learning_enabled=True
)

agent = AGIAgent(config)
```

### Advanced Configuration
```python
config = AgentConfig(
    model_provider="custom",
    model_name="microsoft/DialoGPT-medium",  # Specific model
    max_reasoning_depth=15,
    safety_level="medium"
)
```

## Model Selection Guide

### For Development/Testing
```python
model_name="distilgpt2"  # Fastest, smallest
```

### For General Use
```python
model_name="auto"  # Smart selection
```

### For Better Quality
```python
model_name="microsoft/DialoGPT-large"  # Larger, better responses
```

### For Specific Hardware
```python
# CPU only
model_name="distilgpt2"

# GPU with 4GB+ VRAM
model_name="microsoft/DialoGPT-large"

# GPU with 8GB+ VRAM
model_name="gpt2-medium"
```

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'torch'"**
```bash
pip install torch transformers accelerate
```

**2. "CUDA out of memory"**
- Use a smaller model: `model_name="distilgpt2"`
- Or force CPU: `device="cpu"`

**3. "Model download is slow"**
- First download takes time (models are cached)
- Use smaller model for testing: `model_name="distilgpt2"`

**4. "Response quality is poor"**
- Try a larger model: `model_name="microsoft/DialoGPT-large"`
- Adjust temperature: `temperature=0.8`

### Performance Tips

1. **Use GPU if available** - Much faster than CPU
2. **Start with small models** - Test with `distilgpt2` first
3. **Cache models locally** - First run downloads, subsequent runs are fast
4. **Adjust generation parameters** - Lower `max_length` for faster responses

## Architecture

```
Custom AI Model Stack:
┌─────────────────────────────────────┐
│ AGI Agent (example.py)              │
├─────────────────────────────────────┤
│ Reasoning Engine                    │
├─────────────────────────────────────┤
│ Custom Model Provider               │
├─────────────────────────────────────┤
│ Hugging Face Transformers          │
├─────────────────────────────────────┤
│ PyTorch                             │
├─────────────────────────────────────┤
│ Hardware (CPU/GPU/Apple Silicon)    │
└─────────────────────────────────────┘
```

## Comparison with External APIs

| Feature | Custom Model | OpenAI API | Anthropic API |
|---------|--------------|------------|---------------|
| **Cost** | Free | Pay per token | Pay per token |
| **Privacy** | Complete | Data sent to API | Data sent to API |
| **Internet** | Not required* | Required | Required |
| **Speed** | Fast (local) | Network dependent | Network dependent |
| **Customization** | Full control | Limited | Limited |
| **Setup** | One-time install | API key needed | API key needed |

*Internet only required for initial model download

## Next Steps

1. **Run the demo**: `python demo_custom_model.py`
2. **Install dependencies**: `pip install torch transformers accelerate`
3. **Setup the model**: `python setup_custom_model.py`
4. **Test it out**: `python test_custom_model.py`
5. **Use with AGI Agent**: `python example.py`

## Support

- Check system requirements with: `python setup_custom_model.py`
- View available models: `python model_config.py`
- Test installation: `python test_custom_model.py`
- See demo: `python demo_custom_model.py`

---

🎉 **Enjoy your private, local AI model!** No API keys, no limits, no data sharing.
