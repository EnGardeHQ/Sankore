from typing import Dict, Any, List
from pydantic import BaseModel
import openai
import os
import json

class CopyAnalysisResult(BaseModel):
    score: float
    hooks: List[str]
    ctas: List[str]
    improvements: List[str]
    winning_patterns: List[str]

class CopyAnalyzerService:
    def __init__(self):
        try:
            self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))
        except Exception as e:
            print(f"OpenAI Init Error: {e}")
            self.client = None

    async def analyze_copy(self, ad_text: str, objective: str) -> CopyAnalysisResult:
        """
        Analyze ad copy using an LLM to score effectiveness and extract patterns.
        """
        # Check if client is available before attempting to use it
        if self.client is None:
            print("Warning: OpenAI client not available, returning mock data")
            return CopyAnalysisResult(
                score=75.0,
                hooks=["Detected Hook (Mock Mode)"],
                ctas=["Detected CTA (Mock Mode)"],
                improvements=["Add more urgency", "Include social proof"],
                winning_patterns=["Benefit-First", "Problem-Solution"]
            )

        prompt = f"""
        Analyze the following ad copy for a {objective} campaign.

        Ad Copy:
        "{ad_text}"

        Return a JSON object with:
        - score (0-100 float)
        - hooks (list of strong opening lines found)
        - ctas (list of call to actions found)
        - improvements (list of specific suggestions)
        - winning_patterns (list of abstract patterns found, e.g. "Scarcity", "Social Proof")
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a world-class Direct Response Copywriter."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            data = json.loads(content)

            return CopyAnalysisResult(
                score=data.get("score", 0.0),
                hooks=data.get("hooks", []),
                ctas=data.get("ctas", []),
                improvements=data.get("improvements", []),
                winning_patterns=data.get("winning_patterns", [])
            )
        except Exception as e:
            # Fallback for dev/mock if no key or error
            print(f"Warning: OpenAI API call failed, returning mock data. Error: {e}")
            return CopyAnalysisResult(
                score=75.0,
                hooks=["Detected Hook (Mock Mode)"],
                ctas=["Detected CTA (Mock Mode)"],
                improvements=["Add more urgency", "Include social proof"],
                winning_patterns=["Benefit-First", "Problem-Solution"]
            )
