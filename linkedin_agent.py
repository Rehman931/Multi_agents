from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import TypedDict,Annotated
import operator
from pypdf import PdfReader
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)

llm1 = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite',
    temperature=0.3
)

class PipelineData(TypedDict):
    file_path:str
    input_type:str
    input_text: str
    headline: str
    about: str
    skills: Annotated[list[str], operator.add]
    keywords: Annotated[list[str], operator.add]
    experience: dict
    headline_review: str
    about_review: str
    branding_review: str
    networking_review: str
    ats_score: int
    final_score: int


class ExtractedProfileSchema(BaseModel):
    headline: str = Field(description="A short, catchy professional headline or job title.")
    about: str = Field(description="A comprehensive professional summary or bio.")
    skills: list[str] = Field(description="A list of technical and soft skills identified in the text.")
    keywords: list[str] = Field(description="Industry-specific keywords, tools, or domain terms.")
    experience: dict = Field(description="A structured mapping or dictionary containing work history details like role, company, and duration.")

def Routing_func(State:PipelineData):
    """Stage1:Route flow as file then loader and if text then Analysis"""
    print("Executing Router tool\n")

    return State["input_type"]
    
def fileloader_tool(state: PipelineData):
    """Load PDF text into the graph state."""
    print("Executing loader tool")

    loader = PdfReader(state["file_path"])
    file_text=""
    for page in loader.pages:
        file_text += page.extract_text()

    return {
        "input_text": file_text
    }


def extractor_tool(State: PipelineData):
    """Stage3: Extracting info from text to later analysis"""
    print("Executing extractor tool\n")
    
    # Get the raw text from the state (populated by the loader or direct input)
    source_text = State.get("input_text", "")
    
    # 2. Bind the structured output schema to the Gemini model
    structured_llm = llm.with_structured_output(ExtractedProfileSchema)
    
    # 3. Craft a clean, direct extraction prompt
    system_prompt = (
        "You are an expert data extraction assistant. Your task is to extract professional details "
        "from the provided text and map them strictly to the required output schema without modifying and skill,keywords and experience in there field"
        "the intrinsic meaning or format of the structural data."
    )
    
    user_prompt = f"Please analyze and extract the profile information from the following text:\n\n{source_text}"
    
    # 4. Invoke the model to get a parsed Pydantic object
    try:
        extraction_result = structured_llm.invoke([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        # 5. Return the extracted data to update the LangGraph state
        return {
            "headline": extraction_result.headline,
            "about": extraction_result.about,
            "skills": extraction_result.skills,
            "keywords": extraction_result.keywords,
            "experience": extraction_result.experience
        }
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        # Return empty safe defaults for the state updates if parsing hits an edge case
        return {
            "headline": "",
            "about": "",
            "skills": [],
            "keywords": [],
            "experience": {}
        }

from pydantic import BaseModel, Field

# --- Helper function to build uniform context ---
def _get_profile_context(State: PipelineData) -> str:
    return f"""
    Headline: {State.get('headline', 'N/A')}
    About Summary: {State.get('about', 'N/A')}
    Skills: {', '.join(State.get('skills', []))}
    Keywords: {', '.join(State.get('keywords', []))}
    Experience Data: {State.get('experience', {})}
    """

# ==========================================
# 1. HEADLINE REVIEW TOOL
# ==========================================
def headline_review_tool(State: PipelineData):
    """Analyzes only the professional headline."""
    print("Executing Headline Review Tool")
    
    # Simple schema for a single primitive output
    class SingleReview(BaseModel):
        review: str = Field(description="Constructive critique of the professional headline.")

    structured_llm = llm.with_structured_output(SingleReview)
    
    system = "You are an expert copywriter. Critique the user's professional headline for punchiness, impact, and clarity."
    user = f"Review this profile's headline details:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"headline_review": res.review}

# ==========================================
# 2. ABOUT REVIEW TOOL
# ==========================================
def about_review_tool(State: PipelineData):
    """Analyzes only the about/summary section."""
    print("Executing About Review Tool")
    
    class SingleReview(BaseModel):
        review: str = Field(description="Critique of the professional summary/about section.")

    structured_llm = llm.with_structured_output(SingleReview)
    
    system = "You are a branding coach. Critique the 'About' summary section for narrative flow, engagement, and value proposition."
    user = f"Review this profile's summary details:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"about_review": res.review}

# ==========================================
# 3. BRANDING REVIEW TOOL
# ==========================================
def branding_review_tool(State: PipelineData):
    """Analyzes overall market positioning and personal brand."""
    print("Executing Branding Review Tool")
    
    class SingleReview(BaseModel):
        review: str = Field(description="Evaluation of overall personal branding.")

    structured_llm = llm1.with_structured_output(SingleReview)
    
    system = "You are an executive recruiter. Critique the overall visual and textual personal brand identity and industry positioning."
    user = f"Review this profile's layout details:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"branding_review": res.review}

# ==========================================
# 4. NETWORKING REVIEW TOOL
# ==========================================
def networking_review_tool(State: PipelineData):
    """Analyzes optimization for networking and social outreach."""
    print("Executing Networking Review Tool")
    
    class SingleReview(BaseModel):
        review: str = Field(description="Strategic feedback on networking optimization.")

    structured_llm = llm1.with_structured_output(SingleReview)
    
    system = "You are a professional networking strategist. Evaluate how approachable and optimized this profile data is for community growth and cold outreach."
    user = f"Review this profile data:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"networking_review": res.review}

# ==========================================
# 5. ATS SCORE TOOL
# ==========================================
def ats_score_tool(State: PipelineData):
    """Calculates an objective parser optimization score (0-100)."""
    print("Executing ATS Score Tool")
    
    class SingleScore(BaseModel):
        score: int = Field(description="An optimization score from 0 to 100 based strictly on keyword density and clear structure.")

    structured_llm = llm1.with_structured_output(SingleScore)
    
    system = "You are an Application Tracking System (ATS) parsing simulator. Score this profile configuration strictly out of 100 based on core industry keywords and technical skills present."
    user = f"Analyze these metrics:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"ats_score": res.score}

# ==========================================
# 6. FINAL SCORE TOOL
# ==========================================
def final_score_tool(State: PipelineData):
    """Calculates an overall comprehensive profile score (0-100)."""
    print("Executing Final Score Tool")
    
    class SingleScore(BaseModel):
        score: int = Field(description="An overall profile quality score from 0 to 100.")

    structured_llm = llm1.with_structured_output(SingleScore)
    
    system = "You are a senior talent acquisition director. Look at the overall package of skills, narrative, and experience, and assign a definitive quality score out of 100."
    user = f"Grade this profile setup:\n{_get_profile_context(State)}"
    
    res = structured_llm.invoke([("system", system), ("user", user)])
    return {"final_score": res.score}

builder = StateGraph(PipelineData)
builder.add_node("loader", fileloader_tool)
builder.add_node("extractor", extractor_tool)
builder.add_node("headline", headline_review_tool)
builder.add_node("about", about_review_tool)
builder.add_node("branding", branding_review_tool)
builder.add_node("networking", networking_review_tool)
builder.add_node("ats", ats_score_tool)
builder.add_node("final", final_score_tool)

builder.add_conditional_edges(
    START,
    Routing_func,
    {
        "file":"loader",
        "text":"extractor"
    }
)


builder.add_edge(
    "loader",
    "extractor"
)
builder.add_edge(
    "extractor",
    "headline"
)
builder.add_edge(
    "extractor",
    "about"
)
builder.add_edge(
    "extractor",
    "branding"
)
builder.add_edge(
    "extractor",
    "networking"
)
builder.add_edge(
    "extractor",
    "ats"
)
builder.add_edge(
    "extractor",
    "final"
)


builder.add_edge(
    "headline",
    END
)
builder.add_edge(
    "about",
    END
)
builder.add_edge(
    "branding",
    END
)
builder.add_edge(
    "networking",
    END
)
builder.add_edge(
    "ats",
    END
)
builder.add_edge(
    "final",
    END
)

graph = builder.compile()
