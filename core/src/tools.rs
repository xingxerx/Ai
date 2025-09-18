// Tool execution module
// High-performance tool and process execution

pub mod executor;
pub mod process;

// Re-export public APIs
pub use executor::ToolExecutor;
pub use process::ProcessManager;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_tools_module_loads() {
        assert!(true);
    }
}