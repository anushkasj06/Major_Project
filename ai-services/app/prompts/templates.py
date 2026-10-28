"""
Arambh — Prompt templates for RAG responses.
"""

SYSTEM_PROMPT = """You are Arambh, an expert AI assistant specializing in Indian engineering and polytechnic college admissions.

Your job is to help students with accurate, grounded information about:
- College fees, placements, cutoffs, scholarships
- Hostel facilities, branches, rankings
- Admission criteria, seat availability
- Government notices and policies

STRICT RULES:
1. ONLY answer based on the provided context. DO NOT hallucinate.
2. If the context does not contain enough information, say: "I don't have enough information about this. Please check the official college website."
3. Always cite your sources by mentioning the college name and document type.
4. Be concise, clear, and helpful.
5. Respond in the same language as the user's query ({language}).
6. If multiple colleges match, compare them clearly.
"""

RAG_PROMPT_TEMPLATE = """Based on the following information from official college sources, answer the student's question.

CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

STUDENT QUESTION: {query}

Instructions:
- Answer ONLY based on the context above
- If context is insufficient, clearly state that
- Cite which college/document the info comes from
- Format numbers and fees clearly (₹ for Indian Rupees)
- If comparing colleges, use a structured format

ANSWER:"""

QUERY_UNDERSTANDING_PROMPT = """Analyze this student query about college admissions and extract structured information.

Query: {query}

Respond in JSON format:
{{
  "intent": "one of: fees|placement|cutoff|scholarship|hostel|branches|ranking|admission|seats|general",
  "entities": {{
    "college_name": "extracted college name or null",
    "branch": "extracted branch like CSE, ME, Civil or null",
    "year": "extracted year or null",
    "category": "extracted category like OBC, SC, ST or null",
    "location": "city/district or null"
  }},
  "requires_comparison": false,
  "language": "en|hi|mr",
  "cleaned_query": "normalized English version of the query"
}}"""

RECOMMENDATION_PROMPT = """Based on the student's requirements, recommend suitable engineering colleges.

Student Requirements:
- Budget: {budget}
- Location Preference: {location}
- Preferred Branches: {branches}
- Rank/Score: {rank}
- Other Requirements: {other}

Available Colleges Context:
{context}

Provide top 3-5 recommendations with:
1. College name and location
2. Why it matches their requirements
3. Key strengths
4. Estimated fees
5. Placement highlights

Format as a clear, numbered list."""

TRANSLATION_PROMPT = """Translate the following text to {target_language}.
Keep technical terms (college names, branch names, fees) in their original form.

Text: {text}

Translation:"""
