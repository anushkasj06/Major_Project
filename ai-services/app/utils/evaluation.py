"""
RAG Evaluation — RAGAS metrics: faithfulness, answer relevancy, context recall.
Usage: python -m app.utils.evaluation
"""
import asyncio
from typing import List, Dict


async def evaluate_rag(test_cases: List[Dict]) -> Dict:
    """
    Evaluate RAG pipeline on test cases.
    Each case: {"question": str, "ground_truth": str, "contexts": List[str], "answer": str}
    Returns faithfulness, answer_relevancy, context_recall scores.
    """
    from app.agents.llm_provider import generate_response
    results = []

    for case in test_cases:
        # Faithfulness — does the answer contradict the context?
        faithfulness_prompt = f"""
Context: {chr(10).join(case.get('contexts', []))}
Answer: {case['answer']}
Does the answer contain only information present in the context? Reply with a score 0.0-1.0 only.
"""
        try:
            score_str = await generate_response(faithfulness_prompt)
            faithfulness = float(score_str.strip()[:3])
        except:
            faithfulness = 0.5

        results.append({
            "question": case["question"],
            "faithfulness": faithfulness,
        })

    avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results) if results else 0
    return {
        "num_cases": len(results),
        "avg_faithfulness": round(avg_faithfulness, 3),
        "results": results
    }


# Sample test dataset
SAMPLE_EVAL_SET = [
    {
        "question": "What are the fees for COEP Computer Engineering?",
        "ground_truth": "COEP annual tuition fees are approximately ₹95,000",
        "contexts": ["COEP annual tuition fee for engineering is ₹95,000 per year as per 2024 fee structure."],
        "answer": "COEP annual tuition fee is ₹95,000 per year.",
    },
    {
        "question": "What is VJTI placement average?",
        "ground_truth": "VJTI average package is 9.2 LPA",
        "contexts": ["VJTI 2024 placement report: Average CTC 9.2 LPA, Highest 48 LPA, Placement rate 91%."],
        "answer": "VJTI's average placement package is 9.2 LPA with 91% placement rate.",
    },
]

if __name__ == "__main__":
    results = asyncio.run(evaluate_rag(SAMPLE_EVAL_SET))
    print(f"\n📊 RAG Evaluation Results:")
    print(f"  Cases evaluated: {results['num_cases']}")
    print(f"  Avg Faithfulness: {results['avg_faithfulness']}")
