Hi. This is my syllabus proposal for the new Sinless Software Engineering class. My intention was to achieve the following goals:
1. A larger introduction to machine learning.
2. An unfairness detection module.
3. An unfairness mitigation module.

I am basing it off the original syllabus' markdown, so I will try to **highlight** my changes. No promises, though.

# Syllabus

CSC 591-066 (11983)     
CSC 791-066 (11984)     
Wed 3:00PM - 5:45PM   

## Overview

Lawyers and politicians cannot keep up with technical innovations,
**and the machine is evolving faster than man**.
**In this world full of, sinful technology,** it is up to us technologists
to **make sure the world sins less**. Even though we might
not be able to always avoid undesirable social effects of our
technology, we should at least try to write software that sins less.

This subject treats ethics as an AI-based optimization problem where
software makes choices that at least monitors, and at most improves,
the ethical impact of software. **This subject also treats AI as an
ethics problem, where the decisions we make choices that impact software,
and thus changes its ethical impact.** Topics covered will include ethics,
case studies in ethical software, **bias in data and how to detect it**,
data mining, **bias in data mining and how to mitigate it**,
method optimization (Pareto, multi-objective, Bayesian).

Projects will be determined by student background: skilled programmers
will build AI tools that make better ethical choice; other students
will do extensive case studies in ethics and software engineering.

### Topics

This is an _advanced graduate_ class. 
In this subject, students will be taught about ethical SE and AI.

Topics covered will include ethics,
case studies in ethical software, **bias in data and how to detect it**,
data mining, **bias in data mining and how to mitigate it**,
method optimization (Pareto, multi-objective, Bayesian), explenation,
abduction, non-parametric statistic, and
**transfer of knowledge (aka how to write a paper)**.

### Prerequisites

+ Any advanced programming subject.
+ **Preferrably some background knowledge in AI, data mining, or statistics.**

### Textbook

+  None. This whole topic area is so new.
+  **But be prepared to read a lot of papers.**

### Class Discord Group

It is each student's responsibility to join the class Discord group:

+ Students are strongly encouraged to contribute their 
  questions and answers to that shared resource.
+ Note that, for communication of a more private nature, 
  contact the lecturer on the email shown below.
  
**Note: Yes, please keep using Discord.**

All class communication from staff to students will be via this Discord group.

## Assessment

Grades come from:
- 7 case studies (1 marks each)
- 8 homeworks (3 marks each)
- 1 project draft (5 marks)
- 1 project presentation (15 marks)
- 1 end-of-term project report (35 marks)
- 1 small final report (commentary) (11 marks)

**Note: Removed midterm because I don't think its necesary.
Added evaluation for case studies. Also a project draft to have them do some prior research.**

### Case Studies (new)
- 1 page (max) reports about a case study in software fairness.
- Instructor will give you some initial questions, but you will need to add more.
- We will dedicate the first 20-30 min of class for discussion, be prepared!

### Homeworks

- Homework are scored "1" (for try and do it again) and "3" for "done!". Homework can be submitted
many times (until the mid-term). There are no late marks for homework.
- **But keeping up to date with homework will help you understand class concepts.**
- Homework are "build an AI".

### Project

- Project is "build it better", using the principles of this class.
- Project presentations must be presented on presentation day (last week of term).

Reports get late marks -1 per day late (weekend is 1 mark).

#### Draft (new)
- Around the mid of the term, you will submit a 2-page proposal of your project
- 1.5 pages is you summarizing the literature
- 0.5 pages is "I have these 2-3 ideas of where I want to go"
- Next class session we will discuss them and decide the path

**Note: Personally I like having some checkpoints, but I know its not your style.
Also I'm ashamed to say I need an incentive to read.**

### Exam
Exam is done individually. Everything else is done in  
<a href="https://docs.google.com/spreadsheets/d/1n0zHiZlVYkLAEg5Lj1CVaLSEaeNy8iYjw8IMWYWs4Tk/edit#gid=0">groups</a> (master students, groups of 2. phd students, groups of  1).

With the final grades, the following grade scale will be used: 

     A+ (97-100),  A (93-96),   A-(90-92)
     B+ (87-89),   B (83-86),   B-(80-82)
     C+ (77-79),   C (73-76),   C-(70-72)
     D+ (67-69),   D (63-66),   D-(60-62)
     F (below 60).

### Timetable

**All this is new. Also I'm more on the trend of using what we have.
Possibly sklearn. It looks like a machine learning class, but
people may not just have the ML background.**



|Week|Class Topic|Due that week|
|---|---|---|
|1|Ethics, AI, state of the art, the road ahead|-|
|2|Datasets, pandas, how to "see" your data|HW1: How 2 github, CS1|
|3|Very simple data visualization, how to detect bias in data|HW2: How to pandas, CS2|
|4|Gentle introduction to machine learning classification: the regression|HW3: How to plot, CS3|
|5|Some more machine learning, the model and the pipeline. Yes, we are using a library.|HW4: Make your own linear regression (or other very simple method), CS4|
|6|Metrics. Bias detection on models (with metrics). Maybe LIME but it may be too much. Bias mitigation with pre-processing.|HW5: Training a 2x2 rig of 2 pre-processors and 2 models, and compare results, CS5|
|7|Discretization lecture. Try compressing binary partition and Frugal trees in one class, it will be fun.|HW6: Take a dataset, a model, and try to see how biased it can get. Try again with a pre-processor., CS6|
|7|Optimization. Bias mitigation with optimization.|HW7: Program simple Frugal tree, CS7|
|8|Project draft discussion. Stats.py, they will need it.|Project draft|
|9|How to write a paper. The Fair by design class (basically update on SOTA on fairness)|HW8: Something so you HAVE to use stats.py, maybe using optimization|
|10|Free space. Maybe some discussion on where do we go from here. How to fairness on the industry.|-|
||And I think its like 1-2 dead weeks until project presentation.||


**Note: Keep the rest the same**
