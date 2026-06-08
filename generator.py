from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

# Chunks whose cosine distance is above this are treated as irrelevant and
# dropped before building the context. In-domain matches land around 0.2–0.4;
# unrelated queries land around 0.9+ (see retrieval testing), so ~0.6 cleanly
# separates the two. Tune after running your eval questions.
RELEVANCE_THRESHOLD = 0.6


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer about UCSD social life from retrieved chunks.

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "title"    : the source document title
      - "source"   : the platform/source name (e.g. "Reddit — r/UCSD")
      - "url"      : the original URL
      - "distance" : cosine distance (lower = more similar)

    The answer is grounded ONLY in the retrieved context. Because these sources
    are student opinions and forum posts (not authoritative rules), the model is
    asked to attribute claims to where they came from and to reflect disagreement
    rather than present any single opinion as fact.

    Returns a plain string.
    """
    # Drop weak matches so off-topic questions don't get answered from
    # loosely-related chunks.
    relevant = [c for c in retrieved_chunks if c["distance"] <= RELEVANCE_THRESHOLD]

    if not relevant:
        return (
            "I couldn't find anything about that in the loaded UCSD social life "
            "sources. Try rephrasing, or ask about something like campus parties, "
            "events, clubs, Greek life, the college system, or residence halls."
        )

    context_block = "\n\n".join(
        f"[Source {i + 1} — {chunk['source']}: \"{chunk['title']}\"]\n{chunk['text']}"
        for i, chunk in enumerate(relevant)
    )

    system_prompt = (
        "You are UCSDSocialBot, an assistant that answers questions about social "
        "life at UC San Diego using an unofficial collection of student and alumni "
        "sources (Reddit, Quora, student guides, campus news, YouTube, etc.).\n\n"
        "Rules you must follow:\n"
        "- Answer using ONLY the excerpts provided in the context below. Do NOT use "
        "outside knowledge, even if you think you know the answer.\n"
        "- These are student opinions and personal experiences, not official policy. "
        "Attribute claims to their source (e.g. \"Students on Reddit say...\", "
        "\"According to the UCSD Guardian...\").\n"
        "- When sources disagree, present the range of views rather than picking one.\n"
        "- If the context does not contain enough information to answer, say so "
        "honestly: \"That isn't covered in the sources I have.\" Do not guess.\n"
        "- Be concise, specific, and conversational.\n"
        "- **IMPORTANT - ORGANIZATION RULE:** Organize your answer by source. "
        "Start with the most relevant source, discuss what it says, then move to "
        "the next source. Do not bounce back and forth between sources.\n"
        "- Use clear transitions: 'According to [Source], ...' then 'From [Another Source], ...'"
    )

    user_prompt = (
        f"Context (retrieved excerpts from UCSD social life sources):\n{context_block}\n\n"
        f"Question: {query}"
    )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content
