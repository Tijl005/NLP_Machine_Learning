from typing import Tuple, Optional, Union

from crewai import Agent, Task, Crew, Process, LLM
from tools.wiki_tool import search_tool as wikipedia_search_tool
from tools.serpapi_tool import search_online
# [NIEUW] Importeer de vector tool (zorg dat je tools/vector_tool.py hebt aangemaakt)
from tools.vector_tool import search_history_vector


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


def build_agents(llm: LLM) -> Tuple[Agent, Agent, Agent]:
    """
    Create the TutorAgent, ResearchAgent, and QuizAgent.
    """
    research_agent = Agent(
        name="ResearchAgent",
        role="WW2 Researcher",
        goal=(
            "Efficiently find accurate information about World War II using available tools. "
            "Prioritize local history notes (vector DB) before searching online."
        ),
        backstory=(
            "You are a careful historian specializing in World War II. "
            "You first check your local knowledge base (vector tool) for specific notes. "
            "If the information is missing there, you use Wikipedia or global search. "
            "You are efficient and verify information across sources when possible."
        ),
        # [NIEUW] Voeg search_history_vector toe aan de lijst.
        # De agent kan nu kiezen: lokale notities, Wikipedia of Google.
        tools=[search_history_vector, wikipedia_search_tool, search_online],
        llm=llm,
        verbose=True,
        max_iter=3,  # Limit iterations to reduce API calls
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
        max_iter=2,  # Limit iterations for efficiency
    )

    quiz_agent = Agent(
        name="QuizAgent",
        role="Quiz Master",
        goal=(
            "Create engaging and educational quizzes about World War II topics "
            "based on factual information provided by the researcher."
        ),
        backstory=(
            "You are an experienced educator who creates challenging yet fair multiple-choice questions. "
            "You ensure questions test understanding, not just memorization, and provide clear, "
            "unambiguous answer options with one clearly correct answer."
        ),
        llm=llm,
        verbose=True,
        max_iter=2,  # Limit iterations for efficiency
    )

    return tutor_agent, research_agent, quiz_agent


def answer_question(
    question: str,
    tutor_agent: Agent,
    research_agent: Agent,
    quiz_agent: Agent,
    history: Optional[str] = None,
    mode: str = "Regular answer",
) -> str:
    """
    Run an efficient crew to answer a single user question.

    - ResearchAgent uses tools efficiently (Vector DB + Wikipedia + Online)
    - TutorAgent or QuizAgent produces the final output based on mode

    history: a short text representation of the recent conversation.
    mode: one of ["Regular answer", "Summary", "Explanation", "Quiz"].
    """

    # Optional conversation context prefix
    context_part = ""
    if history:
        context_part = f"Conversation so far:\n{history}\n\n"

    # ---- Research task (optimized) ----
    research_task = Task(
        description=(
            context_part +
            "Research the question efficiently: "
            f"'{question}'. "
            "First check the 'search_history_vector' tool for local notes. "
            "If insufficient, use Wikipedia or online search. "
            "Summarize findings in 5-6 concise bullet points (max 20 words each)."
        ),
        expected_output=(
            "A concise bullet-point summary (5-6 points) with the most relevant facts."
        ),
        agent=research_agent,
    )

    # ---- Choose the right agent based on mode ----
    if mode == "Quiz":
        # Use dedicated QuizAgent
        output_task = Task(
            description=(
                context_part +
                "Using the researcher's summary, create an educational quiz about the topic. "
                "Generate 5 multiple-choice questions with 4 options each (A, B, C, D). "
                "Ensure questions are clear and test understanding. "
                f"Topic: '{question}'. "
                "Format: List questions 1-5, then provide answers separately at the end."
            ),
            expected_output=(
                "5 multiple-choice questions with 4 options each, followed by correct answers."
            ),
            agent=quiz_agent,
        )
        agents_list = [research_agent, quiz_agent]
    else:
        # Use TutorAgent for other modes
        if mode == "Summary":
            tutor_goal = (
                "Using the researcher's summary, provide a concise summary. "
                "Highlight 4-5 key points in bullet format."
            )
        elif mode == "Explanation":
            tutor_goal = (
                "Using the researcher's summary, explain the topic clearly for beginners. "
                "Use simple language and define difficult terms."
            )
        else:  # "Regular answer"
            tutor_goal = (
                "Using the researcher's summary, answer the question directly and clearly. "
                "Keep it concise but informative."
            )

        output_task = Task(
            description=(
                context_part +
                tutor_goal +
                f" Question: '{question}'. "
            ),
            expected_output=(
                "Clear, concise response matching the selected mode."
            ),
            agent=tutor_agent,
        )
        agents_list = [research_agent, tutor_agent]

    crew = Crew(
        agents=agents_list,
        tasks=[research_task, output_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=10,  # Limit requests per minute
        memory=True, # [NIEUW] Activeer Long Term Memory / Short Term Memory
    )

    result = crew.kickoff()
    return str(result)