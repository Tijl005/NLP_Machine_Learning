from crewai import Agent, Task, Crew, Process, LLM
from tools.wiki_tool import search_tool as wikipedia_search_tool
from typing import Tuple, Optional

def build_llm() -> LLM:
    """
    Create an OpenAI-backed LLM for all agents.

    Make sure OPENAI_API_KEY is set in your .env file.
    """
    llm = LLM(
        model="openai/gpt-4o-mini",  # or another OpenAI model, e.g. "openai/gpt-4.1-mini"
        temperature=0.3,
    )
    return llm


def build_agents(llm: LLM) -> Tuple[Agent, Agent]:
    """
    Create the TutorAgent and ResearchAgent.
    """
    research_agent = Agent(
        name="ResearchAgent",
        role="WW2 Researcher",
        goal=(
            "Look up accurate information about World War II, its causes, key events, "
            "major powers, and consequences, and summarize the key facts for another agent."
        ),
        backstory=(
            "You are a careful historian specializing in World War II. "
            "You search trusted course notes (via tools) and produce concise, factual summaries."
        ),
        tools=[wikipedia_search_tool],  # <-- currently only local
        llm=llm,
        verbose=True,
    )
    tutor_agent = Agent(
        name="TutorAgent",
        role="History Tutor",
        goal=(
            "Explain World War II topics to students in simple, clear language, "
            "using the researcher's summaries as factual grounding."
        ),
        backstory=(
            "You are a patient teacher helping students understand 20th-century history. "
            "You turn research notes into easy-to-understand explanations, examples, and analogies."
        ),
        llm=llm,
        verbose=True,
    )

    return tutor_agent, research_agent


def answer_question(
    question: str,
    tutor_agent: Agent,
    research_agent: Agent,
    history: Optional[str] = None,
    mode: str = "Regular answer",
) -> str:
    """
    Run a two-task crew to answer a single user question.

    - ResearchAgent uses the history tool and summarizes key facts.
    - TutorAgent uses those facts to produce either:
      - a regular answer
      - a summary
      - an explanation
      - a quiz

    history: a short text representation of the recent conversation.
    mode: one of ["Regular answer", "Summary", "Explanation", "Quiz"].
    """

    # Optional conversation context prefix
    context_part = ""
    if history:
        context_part = f"Conversation so far:\n{history}\n\n"

    # ---- Research task ----
    research_task = Task(
        description=(
            context_part +
            "Use the available tools to research the student's question: "
            f"'{question}'. Focus on accurate World War II facts, key events, causes, and consequences. "
            "Summarize your findings in bullet points. Maximum 8 bullets, each under 25 words."
        ),
        expected_output=(
            "A concise bullet-point summary of the most important factual information "
            "relevant to the question."
        ),
        agent=research_agent,
    )

    # ---- Tutor behavior depends on mode ----
    if mode == "Summary":
        tutor_goal = (
            "Using the researcher's summary, provide a short summary of the topic. "
            "Highlight only the most important points. Aim for 5–7 concise bullet points."
        )
    elif mode == "Explanation":
        tutor_goal = (
            "Using the researcher's summary, explain the topic step by step as if to a beginner. "
            "Use simple language, give context, and define any difficult terms."
        )
    elif mode == "Quiz":
        tutor_goal = (
            "Using the researcher's summary, create a quiz about the topic. "
            "Generate 5 multiple-choice questions with 4 options each (A, B, C, D). "
            "After listing the questions, provide the correct answers in a separate section."
        )
    else:  # "Regular answer"
        tutor_goal = (
            "Using the researcher's summary, answer the student's question clearly and directly. "
            "Give a short explanation with enough detail to understand the key idea."
        )

    tutor_task = Task(
        description=(
            context_part +
            tutor_goal +
            f" The student's question was: '{question}'. "
            "If there is uncertainty or missing information, state that honestly."
        ),
        expected_output=(
            "An output matching the selected mode (regular answer, summary, explanation, or quiz)."
        ),
        agent=tutor_agent,
    )

    crew = Crew(
        agents=[research_agent, tutor_agent],
        tasks=[research_task, tutor_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
