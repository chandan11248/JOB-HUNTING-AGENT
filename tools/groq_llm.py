"""Groq LLM integration using LangChain - Synchronous version."""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import Config


class GroqLLM:
    """Wrapper for Groq LLM with resume/cover letter generation."""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model_name=Config.GROQ_MODEL,
            temperature=0.7
        )
    
    def customize_resume(self, base_resume: str, job_description: str) -> str:
        """Customize a resume for a specific job.
        
        Args:
            base_resume: The user's base resume text
            job_description: The job posting details
            
        Returns:
            Customized resume text
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume writer. Your task is to customize 
the given resume to better match the job description while maintaining truthfulness.

Guidelines:
- Highlight relevant skills and experiences that match the job requirements
- Reorder sections to emphasize most relevant qualifications first
- Use keywords from the job description naturally
- Keep the resume concise (1-2 pages)
- Maintain professional formatting
- DO NOT fabricate experience or skills"""),
            ("human", """Base Resume:
{resume}

Job Description:
{job_description}

Please provide the customized resume:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "resume": base_resume,
            "job_description": job_description
        })
        
        return response.content
    
    def generate_cover_letter(
        self, 
        resume: str, 
        job_description: str,
        company_name: str
    ) -> str:
        """Generate a cover letter for a job application.
        
        Args:
            resume: The user's resume/skills
            job_description: The job posting details
            company_name: Name of the company
            
        Returns:
            Generated cover letter
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cover letter writer. Create a compelling, 
personalized cover letter that connects the candidate's experience with the job requirements.

Guidelines:
- Start with an attention-grabbing opening
- Show genuine interest in the company
- Highlight 2-3 key qualifications that match the role
- Include specific achievements with metrics when possible
- Keep it to 3-4 paragraphs
- End with a clear call to action
- Professional but personable tone"""),
            ("human", """Candidate's Resume:
{resume}

Job Description:
{job_description}

Company Name: {company_name}

Please write the cover letter:""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            "resume": resume,
            "job_description": job_description,
            "company_name": company_name
        })
        
        return response.content
    def chat(self, messages: list, context: str) -> str:
        """Have a conversation with the user about their career and jobs.
        
        Args:
            messages: List of conversation messages
            context: Context about user's resume and found jobs
            
        Returns:
            LLM response
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a helpful career advisor bot. Use the following context 
(resume and jobs found) to provide advice and suggestions to the user.
Answer the user's questions helpfully and professionally.

CONTEXT:
{context}"""),
            *[(m.type, m.content) if hasattr(m, 'type') else ("human", str(m)) for m in messages]
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
