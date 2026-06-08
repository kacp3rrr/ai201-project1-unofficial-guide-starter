"""Gradio web interface for The Unofficial Guide (M5).

A small web app: type a question about food near CUNY Hunter College, and the
system retrieves relevant student/customer reviews and answers grounded only in
those reviews, listing which documents it drew from.
"""

import gradio as gr
from query import EVAL_QUERIES, retrieve_and_generate

def handle_query(question: str):
    """Run the RAG pipeline for one question and format it for the UI."""
    question = (question or "").strip()
    if not question:
        return "Please enter a question.", ""

    result = retrieve_and_generate(question)
    answer = result["answer"]
    sources = result["sources"]

    sources_text = (
        "\n".join(f"• {s}" for s in sources)
        if sources
        else "(no sources — the reviews didn't cover this question)"
    )
    return answer, sources_text

with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "#The Unofficial Guide\n"
        "Ask about food options near **CUNY Hunter College**. Answers come "
        "only from collected student and customer reviews — if the reviews "
        "don't cover it, the guide will say so."
    )

    question = gr.Textbox(
        label="Your question",
        placeholder="e.g. Is the Chipotle near Hunter worth going to?",
        lines=2,
    )
    ask_btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from (sources)", lines=4)

    gr.Examples(examples=[[q] for q in EVAL_QUERIES], inputs=question)

    # Submit on button click and on pressing Enter in the textbox.
    ask_btn.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
