# src/research_crew/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class CompetitiveResearchCrew:
    """Crew for startup competitor research and analysis"""

    # -----------------------------
    # AGENTS
    # -----------------------------
    @agent
    def researcher_agent(self) -> Agent:
        """Agent that performs competitor research using Serper"""
        return Agent(
            config=self.agents_config['researcher_agent'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def analyst_agent(self) -> Agent:
        """Agent that performs competitor analysis"""
        return Agent(
            config=self.agents_config['analyst_agent'],
            verbose=True
        )

    # -----------------------------
    # TASKS
    # -----------------------------
    @task
    def competitor_research_task(self) -> Task:
        """Search competitor info"""
        return Task(
            config=self.tasks_config['competitor_research_task']
        )

    @task
    def competitor_analysis_task(self) -> Task:
        """Analyze competitors & create report"""
        return Task(
            config=self.tasks_config['competitor_analysis_task'],
            output_file='output/report.md'
        )

    # -----------------------------
    # CREW
    # -----------------------------
    @crew
    def crew(self) -> Crew:
        """Define entire crew workflow"""
        return Crew(
            agents=self.agents,   # auto-loaded from @agent methods
            tasks=self.tasks,     # auto-loaded from @task methods
            process=Process.sequential,
            verbose=True,
        )
