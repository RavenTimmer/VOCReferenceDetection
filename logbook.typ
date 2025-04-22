/*
 * Defines
 */

#show smallcaps: set text(font: "Latin Modern Roman Caps")
#set par(justify: true)

/*
 * Header
 */
#align(center, text(17pt)[
  *--- Research Project Log ---*
])

#align(center, text(13pt)[
  Raven Timmer - 13974920\
])

#line(length: 100%)

= 16/04/2025

== Initialized the repository.
Standard initialization

== Started testing by using entity Recognition.
I have started testing the entity recognition. Firstly I will try this using the pretrained huggingface model described in the #link("https://aclanthology.org/2021.latechclfl-1.3.pdf")[paper: Batavia asked for advice. Pretrained language models for Named Entity Recognition in historical texts.]

The results seem to be good. I will show the recognised entities in the following text:

#align(center, text(8pt)[
  "Erasmus werd in J apan, waar het bij aankomst slecht terecht was gekomen, vastgehouden; ten gevolge van het uitblijven van de nodige herstellingen werd het geheel onbruikbaar; het werd in 1634 voor sloping verkocht. 282 Specx, Vlack, Van Diemen en Van der Burch II, 7 maart 1631 ’t Schip den Gouden Leeuw  is onbequaem bevonden omme met retouren naer ’t vaderlandt over te gaen, jaa is inwendich soo vergaen, dat, onaengesyen de handt daer extra-ordinaris aengehouden is, niet langer in ’t vaerwater sal connen continueren. Schiedam is op de Cust ende wert oudt, sulx dat Uw Edn bij ’t vorige als uuyt"
])

Gives the (post-processed) entities:
#align(center, text(8pt)[
\[{'entity': 'PER', 'text': 'Erasmus', 'score': np.float32(0.52735126)},\ {'entity': 'LOC', 'text': 'Japan', 'score': np.float32(0.9614511)},\ {'entity': 'SHP', 'text': 'Specx', 'score': np.float32(0.67104995)},\ {'entity': 'SHP', 'text': 'Vlack', 'score': np.float32(0.641053)},\ {'entity': 'PER', 'text': 'VanDiemen', 'score': np.float32(0.9959038)},\ {'entity': 'PER', 'text': 'VanderBurchden', 'score': np.float32(0.7346338)},\ {'entity': 'SHP', 'text': 'GoudenLeeuw', 'score': np.float32(0.9601866)},\ {'entity': 'LOC', 'text': 'Cust', 'score': np.float32(0.90481424)}\]
])

#line(length: 100%)

= 21/04/2025

Extracted all dates from the original National Archives xml file (voc\_inventory.xml) and exported them to inventory\_dates.txt.

Dates that are considered ranges are saved as a tuple containing the start and end year. Anything that is not a year is discarded, meaning that 1720 May 10 $arrow.double$ 1720.

Any references to centuries are regexed to a fitting year, so: 18e eeuw $arrow.double$ 1700

The data seems to be complete but is to be finetuned based on how it will be used later.

#line(length: 100%)
