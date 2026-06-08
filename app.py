import gradio as gr
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load rule documents, chunk them, and store in ChromaDB.

    If the vector store is already populated, ingestion is skipped.
    To re-ingest (e.g. after changing your chunking strategy), delete the
    ./chroma_db folder and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting documents...")
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc["text"], doc["title"], doc["source"], doc["url"])
        all_chunks.extend(chunks)

    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks produced. Make sure chunk_document() is implemented in ingest.py.\n"
            "    UCSDSocialBot will start, but won't be able to answer questions yet.\n"
        )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    return generate_response(message, retrieved)


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="UCSDSocialBot") as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1.25rem 0 0.5rem;">
            <h1 style="font-size:2rem; font-weight:700; color:#312e81; margin:0;">
                🤖 UCSDSocialBot
            </h1>
            <p style="color:#6b7280; font-size:1rem; margin:0.4rem 0 0;">
                Ask anything about UCSD Social Life - answer straight from forums and student-run sources.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=440,
                    placeholder=(
                        "<div style='text-align:center; color:#9ca3af; margin-top:3rem;'>"
                        "Ask a UCSD social life question to get started — no arguing required 🎯"
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "Why does UCSD have the "UC Socially Dead" reputation?"',
                    container=False,
                    scale=7,
                ),
                examples=[
                    "Where can I find parties at UCSD, on and off campus?",
                    "Why does UCSD have the 'UC Socially Dead' reputation?",
                    "When does fraternity and sorority recruitment happen at UCSD?",
                    "What happens at a Bear Garden event?",
                    "What are the big annual festivals and events at UCSD?",
                    "How do students recommend making friends at UCSD?",
                    "What free spots on campus are good for socializing?",
                    "How does UCSD's college system work and how does it affect social life?",
                    "What is living in the residence halls like at UCSD?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=180):
            gr.HTML("""
                <div style="background:#f5f3ff; border:1px solid #ddd6fe;
                            border-radius:10px; padding:1rem; margin-top:0.5rem;">
                    <p style="font-size:0.8rem; font-weight:700; color:#4c1d95;
                               margin:0 0 0.5rem; letter-spacing:0.05em;">
                        📚 LOADED SOURCES
                    </p>
                    <ul style="font-size:0.85rem; color:#5b21b6; list-style:none;
                                padding:0; margin:0; line-height:1.8;">
                        <li style="color:#1e1b4b;">📝 Freshmen Survival Guide</li>
                        <li style="color:#1e1b4b;">👽 Reddit (r/UCSD)</li>
                        <li style="color:#1e1b4b;">📰 UCSD Guardian</li>
                        <li style="color:#1e1b4b;">🗞️ The Triton</li>
                        <li style="color:#1e1b4b;">❓ Quora</li>
                        <li style="color:#1e1b4b;">🎓 CollegeVine</li>
                        <li style="color:#1e1b4b;">💬 Plexuss</li>
                        <li style="color:#1e1b4b;">▶️ YouTube</li>
                    </ul>
                    <hr style="border:none; border-top:1px solid #ddd6fe; margin:0.75rem 0;">
                    <p style="font-size:0.75rem; color:#7c3aed; margin:0; line-height:1.5;">
                        Answers are grounded in the loaded sources only. If a topic
                        isn't covered, UCSDSocialBot will say so.
                    </p>
                </div>
            """)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  RulesBot — starting up")
    print("="*50 + "\n")
    run_ingestion()
    demo.launch()
