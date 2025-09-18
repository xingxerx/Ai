// AI Agent Python Bridge
// PyO3 bindings for seamless Rust-Python integration

use pyo3::prelude::*;

pub mod agent_core;
pub mod data_exchange;
pub mod async_bridge;
pub mod error_handling;

// Python module definition
#[pymodule]
fn ai_agent_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    
    // Add submodules when implemented
    // m.add_class::<agent_core::AgentCore>()?;
    // m.add_class::<data_exchange::DataExchange>()?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_python_bridge_loads() {
        // Basic test to ensure library compiles
        assert!(true);
    }
}