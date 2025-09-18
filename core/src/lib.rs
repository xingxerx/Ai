// AI Agent Core Library
// High-performance components for file processing, tool execution, and system integration

pub mod file_processor;
pub mod tools;
pub mod system;

// Re-export main functionality
pub use file_processor::*;
pub use tools::*;
pub use system::*;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_core_library_loads() {
        // Basic test to ensure library compiles
        assert!(true);
    }
}