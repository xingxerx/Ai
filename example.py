"""
Example usage of the AGI Agent.
"""

import asyncio
import os

# Make dotenv optional to avoid ModuleNotFoundError if not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    def load_dotenv():
        return False

from agi_agent import AGIAgent, AgentConfig


async def main():
    """Main example function."""
    print("🤖 AGI Agent Example")
    print("=" * 50)
    
    # Configure the agent
    config = AgentConfig(
        model_provider="openai",  # or "anthropic"
        model_name="gpt-4",
        max_reasoning_depth=10,
        safety_level="high",
        learning_enabled=True,
        auto_approve_safe_actions=False
    )
    
    # Initialize the agent
    print("Initializing AGI Agent...")
    agent = AGIAgent(config)
    
    # Example tasks to demonstrate capabilities
    example_tasks = [
        "Create a simple Python script that calculates the Fibonacci sequence",
        "Analyze the pros and cons of renewable energy sources",
        "Design a creative solution for reducing plastic waste in oceans",
        "Explain quantum computing in simple terms",
        "Invent a new type of musical instrument"
    ]
    
    print(f"\nAgent Status: {agent.get_status()}")
    print("\nExample Tasks Available:")
    for i, task in enumerate(example_tasks, 1):
        print(f"{i}. {task}")
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("Interactive Mode - Enter your task or 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🧠 Enter your task: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            if user_input.isdigit():
                task_num = int(user_input)
                if 1 <= task_num <= len(example_tasks):
                    user_input = example_tasks[task_num - 1]
                    print(f"Selected: {user_input}")
                else:
                    print("Invalid task number")
                    continue
            
            print(f"\n🔄 Processing: {user_input}")
            print("-" * 30)
            
            # Process the request
            response = await agent.process_request(user_input)
            
            # Display results
            if response.success:
                print("✅ Task completed successfully!")
                print(f"📋 Task ID: {response.task_id}")
                
                if response.result:
                    print("\n📊 Results:")
                    if isinstance(response.result, dict):
                        for key, value in response.result.items():
                            if key == "results" and isinstance(value, list):
                                print(f"  {key}: {len(value)} steps completed")
                            else:
                                print(f"  {key}: {value}")
                    else:
                        print(f"  {response.result}")
                
                if response.metadata:
                    print("\n📈 Metadata:")
                    for key, value in response.metadata.items():
                        print(f"  {key}: {value}")
            
            else:
                print("❌ Task failed!")
                if response.error:
                    print(f"Error: {response.error}")
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Shutdown
    print("\n🔄 Shutting down agent...")
    await agent.shutdown()
    print("👋 Goodbye!")


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No API keys found in environment variables.")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY to use the agent.")
        print("\nFor testing purposes, the agent will still initialize but may not work properly.")
    
    asyncio.run(main())
