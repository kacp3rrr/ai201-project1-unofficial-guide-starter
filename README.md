# The Unofficial Guide — Project 1

## Domain

This system covers student-relevant food options in the immediate vicinity of CUNY Hunter College. Platforms like Yelp aggregate generalized public reviews, but don't take into account the context of what matters to a student of the college - factors like proximity, price, and speed of service, among other things.
<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit | Thread on Food Recommendations near Hunter College |https://www.reddit.com/r/HunterCollege/comments/1j9nlfh/food_places_by_hunter/ |
| 2 | Reddit | Another Thread on Food Recommendations| https://www.reddit.com/r/HunterCollege/comments/1fu67yc/food_spots/|
| 3 | Reddit | Food Recommendation Thread with Focus on Affordability| https://www.reddit.com/r/HunterCollege/comments/1ovsxsd/good_affordable_food_rec/|
| 4 |Yelp|Terry and Yaki Foodcart Reviews | https://www.yelp.com/biz/terry-and-yaki-new-york?osq=Terry+and+Yaki|
| 5 |Yelp|Hunter College Cafeteria Reviews |https://www.yelp.com/biz/hunter-college-cafeteria-new-york |
| 6 |Yelp |Hunter Delicatessen Reviews | https://www.yelp.com/biz/hunter-delicatessen-new-york|
| 7 |Yelp |Chipotle near Hunter Reviews | https://www.yelp.com/biz/chipotle-mexican-grill-new-york-85|
| 8 | Yelp|Tacombi near Hunter Reviews |https://www.yelp.com/biz/tacombi-upper-east-side-new-york-2 |
| 9 |Yelp |Gourmet Bagel near Hunter Reviews | https://www.yelp.com/biz/gourmet-bagel-new-york|
| 10 |Yelp |Korean Express near Hunter Reviews |https://www.yelp.com/biz/korean-express-new-york |

---

## Chunking Strategy
<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 400 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** 

It is a large enough chunk size to accomodate most reviews and reddit comments/threads, with some overlap room given to handle entries that cross chunk boundaries. Yelp reviews are self-contained opinions that can for the most part be chunked pretty consistently with a 400 character chunk size. While Reddit comment threads are not entirely self-contained, each individual comment on average is short enough in length that each chunk from the reddit threads will have a few comments, and the overlap will help group threads that are split apart.

Most of the preprocessing done was stripping a lot of the boilerplate text from Yelp/Reddit that snuck into the copy-and-paste (e.g., the post date, the username of the poster, junk alt text from images accidentally highlighted)

**Final chunk count:** 373

**Sample chunks:**
```txt

CHUNK 1: [tacombi.txt #46  len=400]
all, I think it was pretty good and would come back again!

Stopped here with a group of 8 family members after the marathon. Service. Awesome. Food Awesome. Margaritas bang bang spot on great. Tacos were seasoned well and delicious. Guacamole and chips. Excellent. Street corn. Awesome. Pork burritos. Flavorful and nicely prepared.

Loved it. A great vibe and very reasonable.

kay tacos but extrem

----------------------------------------------------------------------------------------------
CHUNK 2: [chipotle.txt #57  len=399]
face when she brought up the fact that all these things ended up in her burrito. Rude.

3. Guacamole was brown. Mine was brown, my fiancee's was brown, everyone's was brown! I paid extra to have gross stringy guacamole sit in my burrito. Definitely not up to regular Chipotle standards.

4. I saw a lady refilling the forks: She grabbed a big handful from under the counter, dropped a bunch on the f

----------------------------------------------------------------------------------------------
CHUNK 3: [chipotle.txt #12  len=400]
uilding my bowl before telling me they would have to re-charge me for my entire bowl. Horrible attitudes. I'm never coming back here again.

Chipotle Mexican Grill

We would like the opportunity to follow up on this as soon as possible. Please contact us directly: https://www.chipotle.com/contact-us#report-an-experience
-Fia

If I could give zero stars, I would! I placed an online order while in s

----------------------------------------------------------------------------------------------
CHUNK 4: [hunter_deli.txt #6  len=399]
come by and I am sure you will find something you like.

This isn't 5 star dining and there are only a couple tables. Probably best for takeout. Not sure if there is wifi either so not ideal if you need to get work done.

Great NYC deli! We love all their sandwiches. Especially the pastrami and roast beef. Delicious!

The ratings are too low for the deli it is- this is a good basic neighborhood d

----------------------------------------------------------------------------------------------
CHUNK 5: [hunter_cafe.txt #15  len=399]
itely run over there instead. You know when its bad when you're absolutely hungry, but the food still tastes nasty.

rude service. My friend asked for some milk to put in her coffee, and the manager (who we were both directed to) told us that "we don't do that here. They will probably tell you to take your coffee back where you bought it..." that just, left a bad taste in my mouth by that kind of
```

---

## Embedding Model
**Model used:**
sentence-transformers (all-miniLM-l6-v2) - good balance of speed, simplicity, and suitability for short opinion-based text. Runs locally with no API key or rate limits, so it is entirely appropriate for the corpus size and usecase in this project

**Production tradeoff reflection:**
Context length would be a consideration, as most Yelp reviews and compacted reddit threads exceed the token limit of weaker models, meaning that upgrading to a model with a bigger token limit would be the primary solution to one of the core bottlenecks of this guide. Latency would also have to be consideration especially if we made the rational choice to scale the number of documents used to form chunks, in the hopes of a more informed answer from the model
<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->
---

## Retrieval Test Results
```txt
======================================================================
QUERY 1: What do students say about the Hunter College cafeteria?
======================================================================

[1] hunter_cafe.txt #19  distance=0.283
always been nice and helpful. It's decent, for what it is.

Oh my goodness, memories of the hunter college cafeteria fill my head as I write this review. Some good times as a wide eyed transfer student fresh out of bmcc eating their soups, salads, burrito bowls, sushi and the occasional sandwich and thinking those were the greatest foods and times I've ever had. I mean, look at all this variety,

[2] hunter_cafe.txt #16  distance=0.364
ust, left a bad taste in my mouth by that kind of answer. When she said "they" she obviously meant "I" since she manages the place. very rude and would not want to go back even though it just re-opened today... at the end of the semester.

It's a cafeteria. With limited selection. At least it is very clean and has some vegetarian options (even veggie sushi). The seating area is HORRIBLE with music

[3] terry_yaki.txt #13  distance=0.366
you're craving something to eat around Hunter College. The guys working at the cart are nice as well.

Good food and some of the tastiest steak bowls I've ever eaten, the chipotle mayo and teriyaki sauce makes this place so iconic that even if it's almost 7 miles from me Id still come.

Great portions for a respectable price. Generous with sauces and substitutions while maintaining great pricing.

[4] hunter_cafe.txt #6  distance=0.368
ul. The service is obnoxious and unaccommodating. I wonder why Hunter college can't get a better deal, quality and price wise, with the massive buying power they posses?! You've got to wonder....!
Do yourself a favor and stay clear of this menacing establishment.

word of advice walk with food or if you have time run out and get a chicken over rice for $5 or something because spending money here i

[5] hunter_cafe.txt #3  distance=0.384
nk about something worse than that.
Yeup this is Hunter College's food.
Probably one of the worst cafeteria in all of US.
Plus.. it's expensive af. At least make it cheap for students..? A meal is at least $8.
The fries are so stale my jaw hurts chewing.
The burgers come with old gross bun and patty.. THATS IT.

Why would u do this to me
I come to u in between class and u have... funfetti with whi

======================================================================
QUERY 2: Is the Chipotle near Hunter worth going to?
======================================================================

[1] hunter_cafe.txt #23  distance=0.341
have it. You're better off eating at the roadside grill cart right in front of hunters main entrance by the west building. You get good food for a fair price. Also chipotle is on third Avenue by 67th street. Go along lex, third Avenue, second Avenue, first Avenue or where ever to pay less for meals that are of better quality and more wallet friendly.

[2] chipotle.txt #39  distance=0.408
are never too long and even if it is, it's quick moving so don't be discouraged.

I usually get steak here now because the one time I got chicken and found it to be burned and could only taste the charred parts. I had taken it to go so was unable to get another one.

Now why this place has 2 stars, is beyond me! I love Chipotle and everytime I come here my experience only gets better. I love the s

[3] chipotle.txt #29  distance=0.458
was a Christmas party. The ONLY reason I go to this specific chipotle is because its by my job and there's nothing else but no more. I get its a minimum wage job and it's whatever but at least try. This spot is just terrible.

Walked in 30 mins after opening.
No white rice. Can't make proper change at the register and soda Machine not working.

Grabbed lunch at Chipotle located at 1153 Third Aven

[4] chipotle.txt #16  distance=0.460
ebsite, someone will be in touch with you directly: https://www.chipotle.com/contact-us
-Sheldon
Euler Vasquez

Literally the worse chipotle location I've eaten on, small rations and although services was fast. It wasn't good as they just want you out of their face. Not recommended go to literally any other chipotle around it'll be better.

Chipotle Mexican Grill

Will you please contact us at htt

[5] terry_yaki.txt #13  distance=0.481
you're craving something to eat around Hunter College. The guys working at the cart are nice as well.

Good food and some of the tastiest steak bowls I've ever eaten, the chipotle mayo and teriyaki sauce makes this place so iconic that even if it's almost 7 miles from me Id still come.

Great portions for a respectable price. Generous with sauces and substitutions while maintaining great pricing.

======================================================================
QUERY 3: Where can I eat near Hunter if I'm on a budget?
======================================================================

[1] reddit_thread_1.txt #0  distance=0.240
Food places by Hunter
General
Why is everything so expensive by Hunter. I get we are in Manhattan and by Central Park but damn😢. I thought the café would be a little more affordable but it’s not. The food is decent but I can’t afford to buy food during my long days and I have enough time to meal prep the whole week. My money is limited unfortunately :/

Any cheap food recommendations that don’t in

[2] reddit_thread_1.txt #1  distance=0.282
y :/

Any cheap food recommendations that don’t include walking to far is greatly appreciated

I feel you. Your Hunter student card gets you 10% off at the Hunter Deli on 70th and Lex. Also at the Dunkin’ down the street the other way. Otherwise…nothing cheap is around there on the UES. I utilize that fruit stand a lot to eat some fruit to hold me over until I get back to my neighborhood

The frui

[3] reddit_thread_2.txt #0  distance=0.307
Go to HunterCollege
r/HunterCollege

Food Spots?
Questions

Hi, I’m a transfer at Hunter and I trying to find the best food spots. I tried the 3rd floor cafe but it’s horrible and the food trucks outside are fine but I want to know what else it has? And is it in close proximity to Hunter where I don’t have to walk blocks just to reach the locations? I’m open to any type of food :)

I go to korean

[4] reddit_thread_2.txt #1  distance=0.348
? I’m open to any type of food :)

I go to korean express a lot

Where is that?

Lunch Deal isn’t bad

Where is that?

5ish blocks downtown on the east side of lexington

Korean Express, UP thai, Thep Thai, The Pho Lexington, Mikado, Jerk House Caribbean, Teranga, Koba, Tina’ Cuban, Patsy’s Pizzeria

Where and how far are all those locations from Hunter?

You should search them up. It’s pretty clo

[5] reddit_thread_1.txt #3  distance=0.360
s and in that area that’s where the microwaves are

I just went to the cafe for the first time this semester the other day. Over $3 for that little ass slice of pizza is highway robbery wtf. Atleast last semester the slices used to be way bigger.

I have no recs for cheap food near hunter unfortunately. I usually buy food on my way home and starve throughout the day💀

Most students starve througho


```

**Query 1:**
Chunks 1,2,4, and 5 are sourced directly from the Hunter Cafe Yelp review, and are relevant to the question about student opinion of the cafeteria - including thoughts on food quality, pricing, and service. Chunk 3 surfaces because it is semantically close in terms of recommending a nearby alternative, but not directly related to the cafeteria. The retrieval correctly prioritized the right source document for almost all of the results

**Query 2:**
Chunk 1 from the Hunter Cafe Yelp review is relevant as it directly references the chipotle as an alternative. Chunks 2-4 are sourced from the Chipotle review as expected and are specific reviews about food quality and service. Chunk 5 from the Terry and Yaki surfaces as it references the word Chipotle, but otherwise isn't relevant. Chunks 1-4 are directly relevant to the query, and Chunk 5 is just a minor false positive that otherwise doesn't dilute much from the chunk sample

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

```py
SYSTEM_PROMPT = (
    "You are The Unofficial Guide, answering questions about food options near "
    "CUNY Hunter College using ONLY the student and customer reviews provided "
    "as context.\n\n"
    "Rules:\n"
    "1. Answer using ONLY the information in the provided context. Never use "
    "outside or prior knowledge.\n"
    "2. If the context does not contain enough information to answer the "
    f"question, reply with exactly this sentence and nothing else: "
    f'"{REFUSAL_MESSAGE}"\n'
    "3. Be concise. Reflect the sentiment of the reviews, and note disagreement "
    "between reviewers when it exists.\n"
    "4. Do not invent prices, names, or details that are not in the context."
)
```

This system prompt immediately enforces the use of ONLY the information supplied by the ChromaDB collection, restricting outside knowledge (given that llama-3.3 is a general-purpose LLM like ChatGPT), and instructed it to return a message stating that it is unable to answer the question if it could not find relevant enough chunks to satisfy the query. I chose to use the tail end of the prompt to enforce some stylistic structure, namely that it is concise and sentimentally accurate, especially in cases where user feedback may vary.

**How source attribution is surfaced in the response:**

The return format of `query.py`'s `retrieve_and_generate()` function:

```py
{
     "answer":  str,          # model answer, or the refusal sentence
     "sources": list[str],    # distinct source files the context came from
     "hits":    list[dict],   # the raw retrieved chunks (text/source/dist)
}
```

Thus, any successful chunk retrieval on a given query will cite all of the sources alongside the chunks found most relevant for the response

---

**Query Interface:**

The interface consists of three fields
- Input: text box where user types their question
- Answer: text box displaying the mode's grounded response
- Retrieved from: a text box citing the source documents that the answer was drawn from

The user types a question and either presses Enter or click the ask button. The system retrieves the top-5 relevant chunks from ChromaDB, passes it to the LLM with the system prompt, and displays the answer and sources

---

**Examples Responses:**

```txt
1. How is service at gourmet bagel

RESPONSE: Service quality at Gourmet Bagel is generally considered good, with many reviewers describing the staff as "nice", "friendly", and "very nice". However, one reviewer had a negative experience with two women at the register, describing them as "extremely rude". The majority of reviewers found the service to be fast and efficient, with a well-organized ordering and pickup process.

Retrieved from (sources):
• gourmet_bagel.txt

-------------------------------
2. Is chipotle a good option for hunter students?

RESPONSE: Reviews are mixed, but most students disagree with the positive assessment. Several students strongly advise against eating at the Chipotle near Hunter College, calling it "the most disgusting Chipotle" and "the absolute worst." One reviewer mentions that despite being a fan of Chipotle, this location is an exception. However, one reviewer, Andrew, approves of this location. Overall, the majority of reviews suggest that Chipotle may not be a good option for Hunter students due to its poor quality.

Retrieved from (sources):
• reddit_thread_3.txt
• chipotle.txt
• hunter_cafe.txt
• reddit_thread_1.txt

-------------------------------
(Out of scope refusal example)
3. Who is playing in the 2026 nba finals?

RESPONSE: I don't have enough information on that.

Retrieved from (sources):
(no sources — the reviews didn't cover this question)

```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the Hunter College cafeteria?| It is convenient in location, but limited in options, and overpriced relative to what you get|Students have mixed but mostly negative opinions about the Hunter College cafeteria. Some mention a decent variety of food, but others criticize it for a limited selection |Good - Cited the cafeteria Yelp, but unnecessarily cited the Yelp of Terry and Yaki, only because it was cited as an alternative | Great |
| 2 |Is the Chipotle near Hunter worth going to? | It's a relatively affordable option but has questionable food quality|Reviews about the Chipotle are mostly negative, but it seems to be due to the specific franchise and not Chipotle food quality/price in general| Good - Cited the Chipotle review, but also unnecessarily cited two other unrelated Yelp Reviews |Great |
| 3 |Where can I eat near Hunter if I'm on a budget? |Chipotle, McDonalds, Hunter Halal Cart. Varying answers, but mostly leans towards these three |Cites the Hunter Deli, which offers student discounts, as a great choice among others. However, the consensus is that affordable food options are limited |Great - Cited two of the three Reddit threads, where affordability for students was of greater focus than Yelp reviews | Great - Only weak in that it is not too specific or considering of all options mentioned, but overall a good consensus |
| 4 |What do people say about the Halal carts near Hunter |They are a frequented food source, but have mixed, slightly negative-leaning opinion about them |These options are dirty and overpriced, and are not recommended due to the lack of sanity |Great - Cited the Reddit threads where these issues appear more frequently, as well as a Yelp review for one of these carts |Decent - Gives a decent overview of sentiment but misses the decent percentage of positive opinions about the Halal Carts |
| 5 |How is service quality at Gourmet Bagel |Reviews on Yelp cite generally good service quality and accomodating staff, albeit with a few bad experiences sprinkled in | Generally considered good, nice staff and fast service. A few negative experiences that had to do with food quality and some service mishaps|Excellent - Cites the Yelp for Gourmet Bagel alone, which is one of the only places it was mentioned besides being vaguely namedropped in Reddit threads |Excellent - Pretty much reflects the expected answer based on Yelp reviews |

**Retrieval quality:** Relevant
**Response accuracy:** Mostly accurate, can struggle when there is sentiment imbalance

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

What is the most popular food place among Hunter students

**What the system returned:**

```txt
Korean Express is mentioned by a student as a place they go to "a lot", but there isn't enough information to definitively say it's the most popular among all Hunter students. Other places like the 3rd floor cafe and food trucks are also mentioned, but with negative or neutral reviews.
```

Gives a cited example of a specific student experience, but fails to give a meaningful assessment of the population consensus

**Root cause (tied to a specific pipeline stage):**

This is a limitation at the generation stage, but the root cause is moreso the documents. The generation stage refuses to confidently give any ranking, due to the fact that no retrieved chunk on its own contains aggregate popularity data. The document pool consists entirely of individual first-person opinions, so even a perfect retrieval cannot confidently supply a population-level consensus

**What you would change to fix it:**

Fixing this issue would require supplying different document types that give better aggregate data (e.g., student surveys, pool results, curated lists from multiple sources, etc). You could also rephrase or redirect prompts hinting at this type of question to aim in the direction of more answerable phrasings that focus on more narrowed queries, rather than cross-document popularity rankings

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

Helped me get on board with the overall structure of the RAG pipeline from top to bottom. Also made it easier to structure the actual codebase and functions that I would end up with. It also made it much easier to prompt Claude with precise requirements, making the overall developing experience more streamlined compared to if I had a more vague structure in mind

**One way your implementation diverged from the spec, and why:**

Didn't really follow the hard line split between milestones 3-5. I initially planned to have each milestone seperated into its own files and structures, but some parts of milestones merged with others, and I sometimes ended up accidentally planning/developing ahead for future milestones. It ended up making the split not as clear, but I believe the ingestion and query phases are still split cleanly enough where I'm satisfied with the end result.

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

- *What I gave the AI:* I gave Claude my planning.md documents section, chunking strategy section, and pipeline diagram, and asked it to produce ingest.py, which would handle document loading from the directory, chunking, and embedding into ChromaDB
- *What it produced:* A complete ingest.py that sanitized the text and the chunks, and a general structure that made it easy to show chunks all chunks and return their counts
- *What I changed or overrode:* I mainly overrode the sanitation process, given that I kept adding/finding ways to sanitize the copy-and-pasted documents based on the chunk outputs. This mainly consisted of making regex patterns, and also being wary of certain edge cases. Some noise still persisted, but I cleansed it down to a point where I got satisfactory results

**Instance 2**

- *What I gave the AI:* I gave Claude my retrieval approach section from planning.md, the chunk metadata structure from ingest.py, and asked it to generate query.py with a retrieval function returning the top-5 chunks with the relevant source metadata and distance scores, as well as grounded generation for prompt response using llama-3.3-70b-versatile
- *What it produced:* A complete query.py with retrieve_and_generate() function returning answer, sources, and raw hits
- *What I changed or overrode:* I tweaked the initial system prompt as the one initially given didn't enforce as much structure. I had to play around with different system prompts before ending up with the one i was most satisfied with
