import os
from dotenv import load_dotenv

from agents import build_llm, build_agents, answer_question


def main():
    load_dotenv()

    groq_key = os.getenv("OPENAI_API_KEY")
    if not groq_key:
        print("[ERROR] OPENAI_API_KEY is not set. Please create a .env file based on .env.example.")
        return

    print("Initializing LLM and agents (CrewAI + Groq)...")
    llm = build_llm()
    tutor_agent, research_agent = build_agents(llm)

    print("\nHistory Tutor (World War II)")
    print("Type your question, or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\n[Thinking... please wait]\n")
        try:
            answer = answer_question(user_input, tutor_agent, research_agent)
        except Exception as e:
            print(f"[ERROR] Something went wrong: {e}")
            continue

        print(f"Assistant:\n{answer}\n")


if __name__ == "__main__":
    main()
