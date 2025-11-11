import sys
from core.graph_builder import SmartInfoAgent
from core.memory_store import MemoryStore


def main():
    print("\n🤖  Smart Info Agent")
    print("---------------------------------------------------")
    print("Type 'exit', 'quit', or 'history' anytime.\n")

    # Initialize agent and memory
    memory = MemoryStore()
    agent = SmartInfoAgent()

    # Chat loop
    while True:
        try:
            user_input = input("User: ").strip()
            if not user_input:
                continue

            # Handle exit or history commands
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye! Thanks for using Smart Info Agent.")
                break
            elif user_input.lower() in ["history", "logs"]:
                print("\n📜 Conversation History:\n")
                print(memory.get_history())
                print("\n")
                continue
            elif user_input.lower() in ["clear", "reset"]:
                memory.clear()
                print("🧹 Memory cleared!\n")
                continue

            # Run the tool-based agent
            response = agent.run(user_input)

            # Display assistant’s reply
            print(f"Agent: {response}\n")

        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
