/*
 * Defines
 */

#show smallcaps: set text(font: "Latin Modern Roman Caps")
#set par(justify: true)

/*
 * Header
 */
#align(center, text(17pt)[
  *--- Talking Points ---*
])

#align(center, text(13pt)[
  Raven Timmer - 13974920\
])

#line(length: 100%)

= Quick overview of the week:
The week was spent on the following tasks:
1. Cleaning up the combined code in #smallcaps("similarity_test.py") (Missed the demo last week)
2. Researching different transformer models, and preprocessing the data
  - Different models ranging from MultiLingual to Dutch to Tailored for the VOC corpus
  - Cleaning up the input data by removing interpunctions, etc.
  - Cleaning up the input data by removing _stopwords_
3. Creating a test dataset
  - The dataset is a set of possible matches which have been hand-marked for their validity.
  - All data is extracted via the Knaw API
  - Around 1000 lines at the moment (Might be expanded)
  - Each query is capped at 200 responses
  - Why: To give quantitative data on the models which otherwise would be "impossible" to get
4. Testing the models
  - I will show the results (for now)

= Show last weeks code
Run #smallcaps("similarity_test.py") with inputs:
- de Gouden Leeuw  is onbequaem bevonden omme met retouren naer ’t vaderlandt over te gaen, jaa is inwendich soo vergaen, dat, onaengesyen de handt daer extra-ordinaris aengehouden is, niet langer in ’t vaerwater sal connen continueren.
- 1633

= Different transformer models
  - _paraphrase-multilingual-MiniLM-L12-v2_: Trained on 50+ languages
  - _all-MiniLM-L6-v2_: English only (But fast)
  - _distiluse-base-multilingual-cased-v2_: Trained on 15+ languages
  - _LaBSE_: Trained on 109 languages
  - _NetherlandsForensicInstitute/robbert-2022-dutch-sentence-transformers_: Modern Dutch
    - Unclear if this is a good model for the VOC data but used in paper

= Cleaning up the input data
  - Removing everything except letters
  - Removing stopwords
    - Candidates were chosen based on the most used words in the test inputs, and with some characteristic words removed from the list.
    - Might want to look into a list that GLOBALISE already compiled.

= Creating a test dataset
  - Show the datasets
  - Suprisingly hard to get a high quality event to test on
    - Either to broad or to specific
  - For now I have used the following events:
    - Gouden Leeuw
    - Johannes Thedens
    - Bantam
    - Don Felipe
    - Patna

= Testing the models

How does this give a quantative result?
- I use Mean Reciprocal Rank (#smallcaps("mrr")) and Mean Average Precision (#smallcaps("map"))) to get a score for the models.

*MRR* is the average of the reciprocal ranks of the first relevant item in the result list.

Since we only use one "list" of results, this is the same as the rank of the first relevant item in the list divided by the number of items in the list.
  - first post = $1$
  - second post = $1/2$
  - third post = $1/3$

*MAP* is the mean of the average precision scores for each query.

Again we only use one "list" of results but this time it takes multiple relevant items into account.

If you get a result like: [true, false, true, false, true] then the average precision is $0.7556$.
  - first post = $1$
  - second post = $0$
  - third post = $2/3$
  - fourth post = $0$
  - fifth post = $3/5$

$ (1 + 2/3 + 3/5)/3 = 2.2667/3 = 0.7556 $

*Problem*: Not yet sure if this is biased towards files with more relevant items.

It does however seem to show a trend relative to other models that use the same data.
