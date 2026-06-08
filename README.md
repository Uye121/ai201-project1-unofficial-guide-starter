# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

UCSD Social Life

Official guides usually contain administrative items, academic policies, and safety protocols. Unofficial guides are run by students that shows what social life is actually like on the ground from the perspective of current students or alumni.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Google Doc | A freshmen survival guide created and updated by UCSD students and alumni. It contains a section on the socializing aspect of UCSD (Partying and Events). | https://docs.google.com/document/u/2/d/1Ne92VhDUGj-fnjg7e-Brc5d1ESInk9GASr2sIHWLbHA/mobilebasic# |
| 2 | Reddit | Redditors talked about UCSD's muted social life especially compared to party schools. | https://www.reddit.com/r/UCSD/comments/1hoe5p4/social_life_at_ucsd/?rdt=58712 |
| 3 | UCSD Guardian | Despite the UC Socially Dead reputation, many students and administrators found social life through the new transit system, college communities, sports, and student initiatives. | https://ucsdguardian.org/2022/04/03/the-uc-socially-dead-stigma/ |
| 4 | Youtube | A former student talked about social life at UCSD. | https://www.youtube.com/watch?app=desktop&v=fCBZmONxAhk |
| 5 | Reddit | Redditors discuss UCSD social life and whether the UC socially dead meme is true. | https://www.reddit.com/r/UCSD/comments/thcbhl/ucsd_social_life/ |
| 6 | Reddit | There are various social events at UCSD such as Bear Garden, meet the beach, and more. | https://www.reddit.com/r/UCSD/comments/wyk39g/when_you_guys_think_of_socializing_events_at_ucsd/ |
| 7 | Quora | Quora users talked about their life at UCSD including things to do and social aspect. | https://www.quora.com/What-is-student-life-like-at-UCSD |
| 8 | Triton News | Different places and activity groups where UCSD students can socialize and make friends. | https://triton.news/2023/11/six-ways-to-make-friends-on-campus-and-counter-the-uc-socially-dead-narrative/ |
| 9 | collegeVine | CollegeVine expert gave an overview of UCSD and dismissed UCSD's "socially dead" label. | https://www.collegevine.com/faq/92983/university-of-california-san-diego-what-s-campus-life-like |
| 10 | plexuss | Q&A response of what life is like on campus. | https://plexuss.com/f3/university-of-california-san-diego-campus-life-residence-halls |

---

## Chunking Strategy - Recursive Chunking

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 256

**Overlap:** 64

**Why these choices fit your documents:** My data is forum-heavy, where individual comments are short independent opinions. A blind fixed-size chunk would slice across different comments, merging unrelated (and possibly opposing) voices into one chunk. Instead, I pre-segmented each sourcce with "---" markers between logical units (one comment, one topic, etc.). The recursive splitter first spits on the delimiters. If a segment exceeds 256 tokens, then it fall back to a fixed-size window. This preserves the integrity of commenter's perspective.

**Final chunk count:** 97

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2

**Production tradeoff reflection:** The documents retrieved are manually extracted and organized, so it would not work in a production setting at scale. For forum sources like Reddit and Quora, the API return the data in a structure way separated by comment so there is no need for custom web scrappers or data wrangling. For blogs, videos, or other web sources, a custom web scrapper is needed to clean the data.

If this is deployed for real users and cost is not a constraint, I would upgrade to all-mpnet-base-v2 or text-embedding-3-small (OpenAI). The key tradeoffs to weigh are:

_Accuracy on domain-specific text_ – UCSD social life discussions use campus slang ("Geisel," "Sixth College," "Price Center"). all-MiniLM-L6-v2 sometimes misses semantic nuance in conversational text. A larger model like mpnet improves recall for queries like "How do commuters make friends?"

_Context length_ – The max token for all-MiniLM-L6-v2 is 256 tokens, which works nicely for all of the documents that are preprocessed. For sources that are longer (> 256 tokens) and cannot be split into smaller logical units, a larger model like text-embedding-3-small would be necessary.

_Latency vs. quality_ – all-MiniLM-L6-v2 runs at ~10ms/query locally. mpnet takes ~30–50ms. For real users, 50ms is still imperceptible, so the accuracy gain likely justifies the latency tradeoff.

_Multilingual support_ – Not relevant for this English-only corpus. Since students are attending UCSD, they should be proficient in English.

_Deployment environment_ – Without cost constraints, I'd also consider a reranking step (e.g., cross-encoder/ms-marco-MiniLM-L-6-v2) after initial retrieval to reorder top-k chunks by relevance. This adds latency but significantly improves answer quality for Q&A.

Bottom line: Cost-no-object production system = text-embedding-3-small + cross-encoder reranker + k=10 (reranked to top-5). But for a local pipeline, all-MiniLM-L6-v2 with k=5 is a practical, fast, and sufficient baseline.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The instruction explicitly tells the models not to use outside knowledge even if it thinks it know the answer. Before constructing the prompt, the chunks are filtered by relevance where any answer with cosine distance over 0.6 are dropped. Those are answers that are off-topic or weakly related chunks. If the model cannot find anything relevant, it falls back by telling the user it cannot find anything.

**How source attribution is surfaced in the response:** The system prompt mandates the attribution pattern: "Students on Reddit say..." or "According to UCSD Guardian..." There is also a rule to force a source-by-source structure as the LLM would answer with the same sources at different lines, interweaving the sources.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | When does fraternity and sorority recruitment happen at UCSD, and how do they differ? | Sorority formal recruitment is week 1 of fall quarter (some informal recruitment in winter/spring, but not all). Fraternity rush is week 2 of both fall and spring quarter (a few do informal rush in winter; most don't). | Based on the YouTube video "UCSD SURVIVAL GUIDE" by byte of michael, sorority formal recruitment occurs during week one of fall quarter and is described as extremely formal, while fraternity rush takes place during week two of both fall and spring quarters with more flexibility. Some sororities may offer informal recruitment in winter and spring, and some fraternities may have informal rush in winter quarter. Students interested in fraternities can choose fall quarter for immediate involvement or spring quarter to experience college life first. No other sources provided additional information about recruitment process differences. | Relevant | Accurate |
| 2 | Where do students find parties at UCSD, both on and off campus? | On campus, parties are found at International House (I-House) in ERC and the Village (transfer housing); both are exclusive, so you need to know the hosts. Off campus, parties are found at fraternities/sororities/social orgs, since UCSD has no frat row; some students also live and party in Pacific Beach. | According to the UCSD Freshmen Survival Guide, most on-campus parties are small kickbacks, with large parties occurring at SDSU or off-campus Greek houses since UCSD lacks a fraternity row. The UCSD Guardian adds that students can find parties outside Greek life through bonfires at local beaches, college-specific events, and organizations via the Center for Student Involvement. Reddit users note that UCSD is not a "frat party lifestyle" school, but social opportunities exist through clubs and smaller gatherings with a healthier drinking culture. CollegeVine confirms that while UCSD isn't a party school, proactive students can find social opportunities through events like the Sun God Festival. Overall, students can access parties and social events through organizations, clubs, university-hosted events, and informal kickbacks across campus. | Relevant | Accurate |
| 3 | What happens at a Bear Garden event? | An outdoor mini-carnival at Matthews Quad, held once or twice a quarter on a Friday afternoon. Everything is free: food from 2–3 vendors, free beer / hard apple cider for those 21+, and carnival games you play for prizes. Lines get long. | The Reddit source describes Bear Garden events as "pretty fun" with free food from 2-3 vendors, two free drinks (beer or hard apple cider) for those over 21, and carnival games offering tickets and prizes, though it notes that lines can get long. The UCSD Freshmen Survival Guide provides additional context, specifying that Bear Garden is an outdoor mini-carnival held at Matthews Quad once or twice per quarter on Friday afternoons, confirming the free beer for those 21+ and free food, games, and prizes for all attendees. | Relevant | Accurate |
| 4 | Why does UCSD have the "UC Socially Dead" reputation? | Relaxed, wealthy La Jolla location with no college town; constant comparison to nearby party school SDSU; no football team (less school-spirit anchor); ~50 frats/sororities but no frat row; a STEM-heavy, academically driven student body; a commuter-heavy campus (only ~39% of students housed on campus); and a college system that can isolate students within their own college. | The UCSD Guardian describes the "UC Socially Dead" reputation as a complex myth, noting that the school's STEM-heavy focus attracts academically-driven students who may prioritize studies over socializing. YouTube creator byte of michael disagrees that UCSD is socially dead, arguing that students need to make an effort to be social, though people do become less social when midterms begin. Reddit and Quora users offer mixed perspectives: one Reddit user insists UCSD is genuinely socially dead and that individual effort alone isn't enough, while a Quora user describes the school as chill and laid-back but lacking strong social energy due to highly intelligent, study-focused students. Overall, the sources point to a combination of factors—STEM culture, academic priorities, and the need for personal initiative—contributing to the reputation. | Relevant | Accurate |
| 5 | According to students, what is the most recommended way to build a social life at UCSD? | The overwhelming consensus is to join clubs, orgs, and club sports and to take personal initiative ("put yourself out there"). UCSD is social if you seek it out. Specific free on-campus social hubs include Tritons Roll Out (roller skating), Groundwork Books, Company 157 (theater), The Che Café (music venue), MOM's Café (open-mic), and The Loft at Price Center. | Across multiple sources, the most consistent recommendation for building a social life at UCSD is to be proactive and take initiative. YouTube creator byte of michael advises going out of your way to be social, starting with meeting people in the dorms. Reddit and The Triton both recommend joining clubs, sports teams, organizations, or student co-ops as affordable, accessible ways to meet people without needing transportation. CollegeVine echoes this by emphasizing proactivity and highlighting university resources and events like the Sun God Festival. The UCSD Guardian notes that while students may not prioritize socializing due to academic focus, this doesn't mean they are anti-social, though it offers no specific recommendations. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Are sorority recruitment and fraternity rush equally formal?

**What the system returned:** According to the Youtube video "UCSD SURVIVAL GUIDE" by byte of michael, sorority formal recruitment is extremely formal and takes place during week one of fall quarter, while some sororities may also have informal recruitment in the winter and spring. On the other hand, fraternity rush, also known as "rush," is a formal process that takes place over one week, with official rush happening during week two of both fall and spring quarters. 

From the UCSD Guardian article "The 'UC Socially Dead' Stigma", there isn't a direct comparison between the formality of sorority recruitment and fraternity rush. However, it does mention that UCSD's Greek life scene is unique due to the lack of a "frat row" on campus.

The Google Doc "UCSD Freshmen Survival Guide" by Nick Lin doesn't explicitly compare the formality of sorority recruitment and fraternity rush. It does mention that joining a frat can involve parties, drama, and poor decisions, and that unless you're good friends with someone in a frat or a woman, you have close to zero chance of getting into parties.

The other sources, including the second part of the Google Doc "UCSD Freshmen Survival Guide" by Nick Lin and the Reddit comment, don't provide information about the formality of sorority recruitment and fraternity rush. 

Overall, based on the available information, it seems that both sorority recruitment and fraternity rush have formal components, but the specifics and levels of formality may differ.

**Root cause (tied to a specific pipeline stage):** The retrieval stage is successful, but the generation stage failed to perform comparative reasoning. Youtube source stated that sorority recruitment is extremely formal, while fraternity rush is flexible but allow flexibility. The right answer should be that they are not equally formal.

The other sources did not compare the formality of both, but the model still bring those sources up adding zero value.

**What you would change to fix it:** I can add another filter to drop chunks that doesn't contain keywords relevant to the specific question or lower the cosine distance. In the prompt, I can also increase the comparative reasoning.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** It helped me go through everything step by step in an organized fashion.

**One way your implementation diverged from the spec, and why:** I did dive into the code a little bit during part of the planning phase because I am used to writing a bit to externalize my thought process as code.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I give Claude my Chunking strategy and the chunking code from the lab and ask it to implement chunk_document() and any helper functions to help with it. I am expecting it to chunks of object, where each contains the document's metadata, the text, and chunk id. I will print the output and see if it matches the expected shape.
- *What it produced:* A modified version of the lab code that is tailored to my usecase (UCSD Social Life) and specific to my planning.
- *What I changed or overrode:* I updated the docstring to be more specific.

**Instance 2**

- *What I gave the AI:* I give Claude my Retrieval approach and the lab retrieval functions and ask it to implement embed_and_store() and retrieve(). I expect it to store the chunks in chromadb, and it can retrieve the top k chunks that is most related to the query. I will print the number of chunks and their distance.
- *What it produced:* A modified version of the lab retrieval code tailored to my usecase.
- *What I changed or overrode:* I added additional metadata (url and source) so that the model can have more information to work with.
