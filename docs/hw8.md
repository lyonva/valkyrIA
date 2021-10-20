# Homework 8 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

# Summary
- My lit. review is currently at 16 papers: https://docs.google.com/spreadsheets/d/e/2PACX-1vTX0mcx_65Mjo6x_waXegNQ5xTOrt3cZD36bFVSWvX06J-PeMIOheSL2QENsvTPHYX2-1rcuR6_TLSn/pubhtml
  - Results suggest effective pre-processing is better at mitigation of bias
  - Hyper-parameter optimization also works, but is more costly
  - I think we more or less know what has been done in fairness, but I'll still keep going with the lit. review until I hit 25/30.
- Plans for action:
  1. Benchmark: compare bias of models using and not using both pre-processing and hyper-parameter optimization. Use everything in literature.
  2. Beat: Find a way to make hyper-parameter tuning beat pre-processing.
  3. Tune everything: Hyper-parameter tune the pre-processing + model.
  4. More: Models, datasets, tuners, etc.

# Partial results of literature review

## Categories
Out of the total 16 papers:
- 31% (5) are theory papers
- 25% (4) are on detection
- 44% (7) are in mitigation
- 0% are on explenation, although you can argue detection has some intersection here

So a great portion focuses on mitigation of fairness for future errors. Are mitigation and detection mutually exclusive? I see them being used separately.

## Topics
Out of the total 16 papers:
- 100% (16) are on fairness (duh)
- 63% (10) contain experimental studies
- 69% (11) are on AI/ML
  - The others are more broad, but they apply as well
- 44% (7) are on data pre-processing
- 13% (2) are on hyper-parameter tuning
  - Both are contained in the 44% data pre-processing

It appears fairness favors more pre-processing approaches than hyper-parameter optimization. Results also aim that way, so far.

## Remarkable studies (w.r.t our goals)

- Fairbalance: A preprint that dethrones parameter optimization and says pre-processing is king of fairness.
- Chakraborty et al. (2019) show that (multi-objective) hyper-parameter tuning was more effective than pre-processing.
- Fairprep: A comprehensive framework for fairness that has HPO, pre-processing, and much more.

## Open Challenges

- We know the impact of pre-processing and tuning. But what about the combination?
- Some pre-processors have configurations. How about we tune them + the model?
- Some studies have limited range of ML models. Should we expand?
- We are just in time to just evaluate everything done up to now as well.

