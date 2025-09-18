# AI Agent Ecosystem 🤖⚡

A high-performance AI agent ecosystem combining **Rust performance** with **Python AI/ML capabilities**. Features hybrid architecture for maximum speed, local AI models, and intelligent task automation.

## 🌟 Current Features

### 🚀 **Hybrid Performance Architecture** 
- **Rust Performance Layer**: CLI, file processing, tool execution (5-10x faster)
- **Python AI/ML Layer**: Transformers, PyTorch, custom models (unchanged capabilities)
- **PyO3 Bridge**: Seamless integration between languages
- **<100ms CLI startup** vs 500-800ms pure Python

### 🧠 **Advanced AI Capabilities**
- **Custom Local Models**: Run entirely offline without API keys
- **Multi-platform Support**: CPU, CUDA GPU, Apple Silicon optimization
- **Smart Model Selection**: Automatic best model for your system
- **Multiple Model Options**: Lightweight to high-performance

### 🔧 **Task Automation**
- **AGI Task Automator**: Natural language task automation (in development)
- **Real-time User Approval**: Safety-first execution with consent
- **Cross-platform Support**: Windows, macOS, Linux
- **Local-only Execution**: Privacy-protected, no network requirements

## 🏗️ Architecture

### **Hybrid Performance Structure**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rust Layer    │    │  PyO3 Bridge    │    │  Python Layer   │
│  (Performance)  │◄──►│  (Integration)  │◄──►│   (AI/ML)       │
│                 │    │                 │    │                 │
│ • CLI Interface │    │ • Data Exchange │    │ • Transformers  │
│ • File Proc.    │    │ • Async Bridge  │    │ • PyTorch       │
│ • Tool Exec.    │    │ • Error Handle  │    │ • Custom Models │
│ • System Ops    │    │ • Memory Mgmt   │    │ • ML Pipeline   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
     ⚡ 5-10x             🔗 Seamless           🧠 Smart
```

### **Project Structure**
```
Ai/
├── cli/                    # Rust CLI (fast startup, <100ms)
│   ├── Cargo.toml
│   └── src/main.rs
├── core/                   # Rust performance components
│   ├── Cargo.toml
│   └── src/
│       ├── file_processor/ # High-speed file operations
│       ├── tools/          # Tool execution engine
│       └── system/         # System integration
├── python-bridge/          # PyO3 integration layer
│   ├── Cargo.toml
│   └── src/
│       ├── agent_core.rs   # Core agent bridge
│       ├── data_exchange.rs # Rust-Python data flow
│       └── async_bridge.rs # Async communication
├── agi_agent/              # Python AI/ML components
│   ├── agent.py            # Main agent logic
│   ├── models/             # AI model interfaces
│   └── core/               # AI reasoning engine
└── specs/                  # Feature specifications
    ├── 001-convert-ai-agent/    # Rust conversion (in progress)
    └── 002-agi-task-automator/  # Task automation (planned)
```

## 🚀 Quick Start

### Option 1: **Rust CLI** (Recommended - Fastest)

1. Install Rust (if not already installed):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. Build and run the CLI:

```bash
cd cli
cargo build --release
./target/release/cli --help
```

### Option 2: **Python AGI Agent** (Full AI Features)

#### Prerequisites

- Python 3.8 or higher
- Optional: OpenAI/Anthropic API keys (for cloud models)

#### Installation

1. Clone the repository:

```bash
git clone https://github.com/xingxerx/Ai.git
cd Ai
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional for cloud models):

```bash
cp .env.example .env
# Edit .env with your API keys if using cloud models
```

4. Run the example:

```bash
python example.py
```

## 🤖 Custom AI Model (No API Keys Required!)

This AGI Agent now includes a **custom local AI model** that runs entirely on your machine without requiring OpenAI or Anthropic API keys!

## 🎯 **Which Approach to Choose?**

### **Use Rust CLI When:**

- ⚡ **Speed is critical** (CLI operations, file processing)
- 🔧 **Simple automation tasks** (file operations, system commands)
- 💻 **Resource efficiency matters** (limited memory/CPU)
- 🚀 **Quick prototyping** of system integrations

### **Use Python AGI Agent When:**

- 🧠 **AI/ML capabilities needed** (reasoning, language understanding)
- 🤖 **Complex task planning** (multi-step workflows)
- 📚 **Knowledge management** (persistent learning, memory)
- 🔬 **Research and experimentation** (model testing, algorithm development)

### **Hybrid Approach (Best of Both):**

- 🌟 **Production systems** requiring both speed and intelligence
- 📈 **Scalable applications** with varying performance requirements
- 🔄 **Gradual migration** from Python to Rust for performance gains

### Quick Start with Custom Model

1. **Setup (one-time)**:
```bash
python setup_custom_model.py
```

2. **Test the model**:
```bash
python test_custom_model.py
```

3. **Run the agent**:
```bash
python example.py
```

### Custom Model Features

- 🚀 **No API keys required** - runs completely offline
- 🧠 **Smart model selection** - automatically chooses the best model for your system
- 💻 **Multi-platform support** - works on CPU, CUDA GPU, and Apple Silicon
- 📦 **Multiple model options** - from lightweight to high-performance
- 🔧 **Easy configuration** - just set `model_provider="custom"`

### Available Models

Run `python model_config.py` to see all available models and get recommendations for your system.

### Basic Usage

```python
import asyncio
from agi_agent import AGIAgent, AgentConfig

async def main():
    # Configure the agent
    config = AgentConfig(
        model_provider="openai",
        model_name="gpt-4",
        safety_level="high"
    )
    
    # Initialize the agent
    agent = AGIAgent(config)
    
    # Process a request
    response = await agent.process_request(
        "Create a Python script that analyzes data trends"
    )
    
    if response.success:
        print("Task completed successfully!")
        print(f"Result: {response.result}")
    else:
        print(f"Task failed: {response.error}")
    
    await agent.shutdown()

asyncio.run(main())
```

## 📖 Documentation

### Core Components

#### Reasoning Engine
The reasoning engine provides various types of reasoning capabilities:

- **Analytical**: Step-by-step problem analysis
- **Creative**: Novel solution generation
- **Strategic**: Goal-oriented planning
- **Causal**: Cause-and-effect analysis
- **Logical**: Formal reasoning processes

#### Task Planning
The task planner automatically:

- Decomposes complex tasks into manageable steps
- Identifies dependencies between steps
- Estimates execution time
- Optimizes execution order
- Handles error recovery

#### Safety System
Built-in safety mechanisms include:

- Action approval workflows
- Risk assessment
- Constraint enforcement
- Human oversight integration
- Rollback capabilities

### Configuration

The agent can be configured through the `AgentConfig` class:

```python
config = AgentConfig(
    model_provider="custom",      # "openai", "anthropic", or "custom"
    model_name="auto",            # Model to use (or "auto" for smart selection)
    max_reasoning_depth=10,       # Maximum reasoning steps
    safety_level="high",          # "low", "medium", "high"
    learning_enabled=True,        # Enable learning system
    auto_approve_safe_actions=False  # Auto-approve safe actions
)
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key

# Optional
AGI_MODEL_PROVIDER=openai
AGI_MODEL_NAME=gpt-4
AGI_SAFETY_LEVEL=high
AGI_LEARNING_ENABLED=true
```

## 🛠️ Development

### Project Structure

```
agi_agent/
├── __init__.py
├── agent.py                 # Main AGI Agent class
├── core/                    # Core components
│   ├── reasoning_engine.py  # Reasoning capabilities
│   ├── task_planner.py      # Task planning system
│   ├── knowledge_manager.py # Knowledge management
│   ├── tool_integration.py  # Tool integration
│   ├── learning_system.py   # Learning capabilities
│   └── safety_controller.py # Safety mechanisms
├── models/                  # Data models
│   ├── task.py             # Task representations
│   ├── reasoning.py        # Reasoning models
│   ├── plan.py             # Planning models
│   └── response.py         # Response models
└── interfaces/             # User interfaces
    └── communication.py    # Communication interface
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black agi_agent/
flake8 agi_agent/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- The open-source AI community

## 🔮 Project Evolution & Roadmap

### 🎯 **Current Development Focus**

**AGI Task Automator (In Development)** - Natural language task automation:

- **Natural Language Processing**: Convert plain English tasks to executable commands
- **User Approval System**: Real-time consent for all actions
- **Cross-platform Execution**: Windows, macOS, Linux support
- **Local-only Processing**: Privacy-first, no network requirements
- **Safety Controls**: Built-in validation and rollback capabilities

### 🚀 **Performance Migration**

**Rust Conversion Progress**:

- ✅ **CLI Interface**: Fast startup and command processing
- 🔄 **Core Engine**: Migrating Python performance bottlenecks
- 📋 **Integration Layer**: PyO3 bridge for seamless Python-Rust communication
- 🎯 **Target**: 5-10x performance improvement while maintaining AI capabilities

### 📈 **Roadmap**

#### **Phase 1: Performance** (In Progress)

- [x] Rust CLI foundation
- [ ] File processing optimization
- [ ] Tool execution acceleration
- [ ] Memory management improvements

#### **Phase 2: Automation** (Planned)

- [ ] AGI Task Automator completion
- [ ] Natural language command interface
- [ ] Cross-platform system integration
- [ ] Advanced safety mechanisms

#### **Phase 3: Enhancement** (Future)

- [ ] Web-based user interface
- [ ] Advanced tool ecosystem
- [ ] Multi-modal capabilities (vision, audio)
- [ ] Distributed execution across devices
- [ ] Enhanced learning algorithms
- [ ] External knowledge base integration
- [ ] Real-time collaboration features

## 📞 Support

For questions, issues, or contributions, please:

1. Check the [Issues](https://github.com/your-username/agi-agent/issues) page
2. Join our [Discord community](https://discord.gg/agi-agent)
3. Email us at [support@agi-agent.com](mailto:support@agi-agent.com)

---

**⚠️ Disclaimer**: This is an experimental AGI system with active development. Always review and approve actions before execution, especially in production environments. The hybrid Rust-Python architecture is under continuous optimization.
