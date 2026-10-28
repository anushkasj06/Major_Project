"""
Few-shot examples for better RAG responses on Indian college queries.
"""

FEW_SHOT_EXAMPLES = [
    {
        "question": "What are the fees for CSE at COEP?",
        "context": "COEP annual tuition fee for Computer Engineering is ₹95,000 as per 2024-25 fee structure approved by DTE Maharashtra.",
        "answer": "The annual tuition fee for Computer Science Engineering (CSE) at COEP (College of Engineering Pune) is **₹95,000** for the academic year 2024-25, as approved by DTE Maharashtra.\n\n*Source: COEP Fee Structure 2024-25*",
    },
    {
        "question": "What is VJTI Mumbai placement record?",
        "context": "VJTI 2024 Placement Report: 91% students placed. Average CTC: 9.2 LPA. Highest CTC: 48 LPA (Google). Top recruiters: Google, Microsoft, TCS, Infosys.",
        "answer": "VJTI Mumbai's 2024 placement statistics:\n- **Placement Rate:** 91%\n- **Average Package:** ₹9.2 LPA\n- **Highest Package:** ₹48 LPA (Google)\n- **Top Recruiters:** Google, Microsoft, TCS, Infosys\n\n*Source: VJTI Placement Report 2024*",
    },
    {
        "question": "I don't have information about this college",
        "context": "",
        "answer": "I don't have specific information about this in my knowledge base. I recommend:\n1. Visiting the official college website directly\n2. Contacting the admissions office\n3. Checking the DTE Maharashtra portal at dtemaharashtra.gov.in\n\nWould you like me to help with another college I have data for?",
    },
]


def build_few_shot_prompt(examples: list = None) -> str:
    """Build few-shot examples string for prompt prefix."""
    examples = examples or FEW_SHOT_EXAMPLES[:2]
    parts = ["Here are examples of ideal responses:\n"]
    for ex in examples:
        parts.append(f"Q: {ex['question']}")
        parts.append(f"A: {ex['answer']}\n")
    return "\n".join(parts)
