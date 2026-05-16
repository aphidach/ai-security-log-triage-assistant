---
title: "Fine-tuning small language models for industrial retrieval-augmented generation: Efficiency, factuality, and hallucination analysis"
source: "https://www.sciencedirect.com/science/article/pii/S0920548926000371?utm_source=chatgpt.com"
author:
  - "[[together with an 8B mid-sized baseline model]]"
  - "[[using real-world industrial customer service and internal regulation logs in retrieval-augmented generation (RAG) applications. The evaluated models include DeepSeek-R1-Distill-Qwen-1.5B]]"
  - "[[Llama-3.2–3B-F1-Instruct]]"
  - "[[Llama-Breeze2–3B-Instruct]]"
  - "[[Gemma-3–4B-IT]]"
  - "[[Qwen3–4B]]"
  - "[[and Llama-3-Taiwan-8B-Instruct. Faithfulness]]"
  - "[[response relevance]]"
  - "[[factual correctness]]"
  - "[[and F1 score are adopted to assess generation quality and efficiency. The impact of training data scale is investigated]]"
published:
created: 2026-05-16
description: "This study examines the fine-tuning performance of five small language models (SLMs) ranging from 1.5B to 4B parameters, together with an 8B mid-sized…"
tags:
  - "clippings"
---
## Published by: Elsevier

### Published by

[![Elsevier](https://www.sciencedirect.com/eu-west-1/prod/3bda52079cf433ecd5c50fdf87cde311ea7a6dc4/image/elsevier-non-solus.svg)](https://www.sciencedirect.com/journal/computer-standards-and-interfaces "Go to Computer Standards & Interfaces on ScienceDirect")

,

[View **PDF**](https://www.sciencedirect.com/science/article/pii/S0920548926000371/pdfft?md5=29c72abacf215e378b560de1c28d5c3b&pid=1-s2.0-S0920548926000371-main.pdf)

[10.1016/j.csi.2026.104163](https://doi.org/10.1016/j.csi.2026.104163)

## Highlights

## Keywords

Small language model (SLM)

;

Fine-tuning

;

Retrieval-augmented generation

;

Hallucination evaluation

;

Hallucination taxonomy

- [Previous article in this issue](https://www.sciencedirect.com/science/article/pii/S0920548926000383)
- [Next article in this issue](https://www.sciencedirect.com/science/article/pii/S0920548926000395)

## 1\. Introduction

The rise of large language models (LLMs) has changed the nature of natural language processing (NLP): they can achieve state-of-the-art performance on knowledge intensive reasoning tasks and for open domain conversational systems. Even with these advances, however, their parametric knowledge is a static field that is difficult to interpret and susceptible to factual hallucination \[,\]. Recent work incorporates a generative model with an external read-only non-parametric memory for better generative factuality and interpretability \[,\], which is referred to as Retrieval-Augmented Generation (RAG) models, filling the mentioned gaps. However, deployment in practice introduces new challenges regarding how to balance model size, latency and cost trade-offs; protecting data ethics and locality; domain specific robustness requirements for safety critical applications \[,\]. These concerns have influenced the trend toward Small Language Models (SLMs) which have computational efficiency in performing the task of interest, however, and support reliable on-premises and edge deployment \[, \].

The development of SLMs has been investigated for applications in specialized fields such as industry and science. Previous research has shown that lightweight, task-specific configurations can achieve performance comparable to or even superior performance to LLMs in tasks like industrial text classification and content moderation, particularly under realistic computational and latency constraints \[, \]. Biomedicine-oriented applications entail competitive comprehension and generation performance for bilingual SLMs such as BioQwen while making use of quantized equivalents for mobile and embedded platform utilization \[\]. Similarly, data-intensive fine-tuning methods improve technical requirement accuracy extracted by SLMs to human-level dependability while keeping confidentiality through local computation \[\]. Domain adaptation also holds true for technical commercialization and industrial question-responding tools where expertly curated datasets find highly augmented contextual and factually correct pertinence by compact model fine-tuning \[,\]. Viewed from the angle of edge computing, SLM models that have undergone training by way of parameter-efficient fine-tuning (PEFT) and quantization yield low-latency operation amenable to a wide variety of scenarios such as handheld instrumentation and industrial automation controls \[,\].

Despite significant progress in related fields, ensuring the reliability of language models remains a significant and pressing challenge. The definition of hallucination in traditional natural language generation research includes: the generated content is meaningless or inconsistent with the original content. When hallucination occurs in language models, it will have a negative impact on applications in specific sensitive fields, such as medicine, law, and policy \[,\]. While retrieval-augmented generation (RAG) methods have mitigated some of these factual discrepancies, even with highly accurate retrieval results, models can still misinterpret evidence or provide only superficial arguments, leading to persistent issues of factual errors and insufficient fidelity \[,,\].

Several studies have proposed approaches to mitigate hallucination in the RAG pipeline. For instance, evidence re-ranking mechanisms and automated evaluation pipelines such as RAGAS have been employed to enhance factual accuracy and semantic coherence to reduce reliance on manual annotation \[,,\]. Other research has focused on model adaptation and fine-tuning approaches including both full and parameter-efficient methods such as LoRA and QLoRA, which improve model fidelity and reasoning capabilities when generalizing to domain-specific data \[,,\]. Farquhar et al. \[\] proposed an uncertainty perception decoding technique and semantic entropy estimation method that can promptly eliminate false or unfounded outputs, thereby enhancing the reliability of language models in zero-reference scenarios. Moreover, task-oriented learning strategies (such as solution-guided fine-tuning (SGFT)) can enhance logical reasoning in low-data environments \[\], while curriculum-based techniques (such as arithmetic GPT) can develop procedural and numerical reasoning abilities in small models \[\].

In spite of the fast-methodological development, empirical studies still suffer from fundamental limitations. Standard datasets that emerge heavily in the literature are either synthetic or public and cannot represent the heterogeneity, sparsity, and temporal drift typical of enterprise-wide data. Thus, domain-specific evidence on characterizing residual hallucination in deployed, self-improving models—especially within end-to-end RAG pipelines under privacy, computational, and annotation scarcity constraints—is lacking. Moreover, any existing taxonomies on hallucination are largely descriptive and detection-driven in nature, overlooking failure modes like misattribution, overgeneralization, and context drift witnessed in clinical (Huang et al., 2024) and policy-centric applications \[\]. From a practical perspective, instead of static accuracy benchmarks, practitioners should also consider utility-oriented evaluation that involves marginal efficiency metrics (e.g., fidelity improvement per GPU-hour or data increment) to weigh the model quality against resource consumption \[,\].

This study employs an empirical approach, utilizing real-world industrial customer service and formal internal regulatory documents RAG logs to compare the performance differences between untrained models and models trained on scaled datasets across multiple single-language models (SLMs) and GPT-4o-mini. It further examines the quality improvements and computational costs associated with quantitative fine-tuning. We also proposed a heuristic hallucination taxonomy and developed classification criteria based on root cause analysis. The primary contributions of this research can be summarized as follows:
- (1)
	Empirical evidence of residual hallucinations in RAG and mitigation via fine-tuning.
	We provide empirical evidence demonstrating that RAG systems still produce unfounded or erroneous outputs in SLMs; employ automated metrics to quantify hallucination rates; and confirm that domain-specific fine-tuning significantly reduces such errors.
- (2)
	Systematic analysis of training-data scaling on four quality metrics and its cost–benefit implications (Δmetric per GPU-hour).
	We systematically quantify how varying training-data volumes affect faithfulness, response relevancy factual correctness, and F1 score across multiple SLMs, and we introduce Δ(metric)/GPU-hour as a practical cost-efficiency measure to identify diminishing returns.
- (3)
	Development of a heuristic hallucination taxonomy.
	We develop and validate a practical heuristic hallucination taxonomy framework for RAG systems based on SLMs. This framework employs automated heuristic methods and has been validated through human gold-standard ratings of 154 samples.

## 2\. Related work

### 2.1. Small language models and parameter-efficient fine-tuning

Recent developments of parameter-efficient fine-tuning (PEFT) approaches have reshaped the flexibility of pre-trained models by considerably lowering the computational and memory budgets for domain transfer. Methods such as LoRA \[\], QLoRA \[\] and other adapter-based architectures achieve selective low-rank updates during training to few weights, retaining the generalization power of epic models at a faster pace for task-specific learning. For example, the empirical results of Zhang et al. \[\] and Kwon et al. (2025) show that small language models (SLMs) can achieve the same level of accuracy as LLMs while having much fewer parameters and energy consumption. Other related works on model compression, quantization, and domain-adaptive fine-tuning further justified SLMs to be promising for edge deployment and industrial-scale applications with limited resources \[,\]. Since PEFT only optimizes a partial set of parameters, the evaluation framework has been increasingly focusing on efficiency-normalized comparison—whether per unit investment of computational resource can be achieved. In this spirit, we take an efficiency-centric view in our study and cast Δ(metric)/GPU-hour as a quantitative measure to quantify reduction in data scaling efficiencies and returns of fine-tuned SLMs.

### 2.2. Hallucination of large language models

Research on hallucinations in large-scale language models (LLMs) has reached an advanced stage, encompassing frameworks for definition, benchmarking, and automated detection techniques. Previous research has primarily categorized hallucinations into two types: intrinsic hallucinations (arising from internal flaws in model inference) and extrinsic hallucinations (occurring when generated content contradicts existing evidence or memory contexts) \[, \]. Previous research has primarily categorized hallucinations into two types: intrinsic hallucinations, stemming from internal flaws in model reasoning; and extrinsic hallucinations, occurring when generated content conflicts with existing evidence or contextual memory \[, \]. Other studies have proposed classification frameworks for hallucination evaluation. For example, HalluLens evaluates general factual accuracy \[\], whereas HalluCode and assessments at the repository level concentrate on hallucinations in program synthesis and code generation \[,\]. These studies show that combined accuracy metrics can mask a variety of failure types, including outright fabrication, unsupported reasoning, and partially or inconsistently correct logic.

Furthermore, previous studies proposed methods for detecting hallucinations. Manakul, Liusie, and Gales \[\] proposed the SelfCheckGPT, a simple sampling-based approach that can be used to fact-check the responses of black-box models in a zero-resource fashion. However, the detection of subtle or complex hallucinations is still an open problem. Further, even RAG models suffer from extrinsic hallucinations in multi-hop reasoning or specialized domain settings, suggesting that the presence of retrieval does not ensure factual faithfulness. In a collective sense, this hierarchical accounting provides the conceptual underpinning for efficient light-weight heuristics (intended to support further scalable and semi-automatic hallucination annotations subsequently confirmed via formal human verification in our study).

### 2.3. Mitigation strategies and taxonomic frameworks

Modern hallucination reduction methods employ retrieval-based grounding and promotion optimization, as well as parameter-wise efficient adaptation for enhancing factual reliability. Retrieval-Augmented Generation (RAG) models and automatic evaluators such as RAGAS \[\] actively mitigate incomplete assertions by directly conditioning explanations on retrieved evidence. Intra-shot and Inter-shot therefore exhibit strong model-dependent sensitivities as well: when comparing between the models, our proprietary LLMs (e.g., GPT-4o) benefit more from retrieval integration, in contrast to open-weight models (e.g., Llama-3. 1–8B) would gain more from in-context learning and adaptive prompting \[,\]. Unified evaluation setup: by incorporating THaMES \[\] in the integrated environment, RAG, ICL and PEFT are benchmarked under a single setting that includes not only standard task scales, but also efficiency measures for reproducibility and cost-aware benchmarks (e.g. Δ(metric)/GPU-hour).

Our work extends the efficiency-normalized evaluation to small language models (SLMs) as well and we quantify Δ(metric) per GPU-hour and across the range of SLMs, and explore how various data-scaling methods impact faithfulness, contextuality, and factuality. Previous evidence shows that retrieval grounding together with domain-specific PEFT significantly decreases unsupported inferences and leaked content, which justifies our empirical analysis dedicated to residual hallucinations and fine-tuning efficacy. At the same time, polished hallucination taxonomies now distinguish error modes at finer granularity: general divisions such as fabrication, unsupported inference, misinterpretation, and low faithfulness are further carved out by domain-specific schemes like the five-type structure used in HalluCode \[\]. Motivated by these frameworks, we create a task-relevant, rule-based taxonomy for small model RAG outputs and validate it with human cross-annotation.

### 2.4. Automatic evaluation using LLM evaluators

One recent direction of research involves the use of large language models as judges — i.e. LLM-as-judge frameworks — for automatically evaluating the quality or factual consistency of model-generated output over a large-scale. First systems, like G-Eval, take inspiration from this paradigm that they try to implement through structured reasoning-based querying and decomposition of thought chains that allow for multi-faceted scoring much closer to humans. Empirical evidence shows that task-dependent and query-related factors have substantial influences on the LLM’s capacity of generating high-quality generated text, with moderate to strong correlations observed between them and human evaluation \[\]. Recent studies and meta-analyses aggregate the work in this space, drawing attention to lingering issues such as systematic evaluator bias (e.g., towards LLM-generated text), prompt sensitivity, calibration drift, and a lack of overarching meta-evaluation protocols that dictate when judges based on an LLM can reliably replace human raters \[,\]. Given these constraints, this work utilizes a hybrid evaluation setup which combines scalable LLM-as-judge testing with rule-based heuristic taxonomy scoring and verification on a curated subset of 154 samples along with human judgments.

### 2.5. RAG Evaluation Frameworks and Metrics

Recently, RAG has been proposed as a principled way to improve the factual grounding of large and small language models. By utilizing external retrieval together with generative reasoning, RAG enhances factual accuracy and reduces neural hallucination, particularly in knowledge-rich domains like legal, clinical and industrial knowledge management \[,,,\]. Nevertheless, quantifying RAG's quality is difficult since its performance derives from a combination of retrieval, reasoning and generation. Ren et al. s analysis of scientific policy interpretation even if retrieval methods can find relevant documents, lack the capability to provide comprehensive decision support for user-oriented policy explanations–highlighting once more that model understanding is still a major bottleneck. However, previous work demonstrates that even a strong RAG pipeline may lead to hallucinations due to the fact retrieval or reasoning is off, supporting taxonomy-guided error analysis and cost-sensitive interventions. Based on these observations, we present a complementary approach to reinforce domain-specific concepts by fine-tuning small language models (SLMs) such that answer grounding and model comprehension are enhanced during RAG’s ultimate synthesis, which provides defense against residual hallucinations. We measure the remaining hallucination types through automatic metrics and empirically verify the proposed fine-tuning method with efficiency-normalized experimentation.

## 3\. Methods

### 3.1. Dataset construction and augmentation

Our goal is not to train a language model from scratch, but to perform domain adaptation on instruction-tuned SLMs using parameter-efficient fine-tuning. Therefore, the learning problem is closer to aligning model behavior with enterprise-specific terminology, evidence usage patterns, and answer style under RAG, rather than learning general language competence. The empirical dataset for this study was obtained from the customer service department of Sakura Company in Taiwan, which utilizes an interactive knowledge management system based on a Retrieval-Augmented Generation (RAG) architecture. A total of 383 customer service RAG query logs and 179 internal regulation RAG query logs were collected from customer service agents, with each record containing the user query, the top two retrieved reference documents, the LLM-generated response, and the corresponding human feedback rating on answer quality. Consistent with previous research emphasizing the critical importance of data reliability in fine-tuning and evaluation \[\], this study selected only items with a RAG generation score of gold-standard.

The gold-standard labels were provided by two senior domain experts with direct operational experience in industrial customer service and two senior domain experts in internal compliance workflows. For the customer service RAG log data, the dataset was split into 229 training samples and 154 testing samples. The internal regulation RAG log data was split into 119 training samples and 60 testing samples. To increase data diversity given the limited real-world samples, this study used the Sakura RAG knowledge base and the GPT-4o model combined with a few-shot data synthesis strategy to generate 200 synthetic RAG samples for customer service and 215 synthetic RAG samples for internal regulation. The synthetic RAG samples were not used directly after generation. All synthetic RAG question–answer pairs were reviewed and, if necessary, corrected by domain experts to ensure validity, coherence, and consistency with retrieved evidence. Only validated synthetic samples were included in the fine-tuning process. Only real-world industrial logs (154 testing samples from customer service and 60 testing samples from internal regulation) were used for evaluation tasks.

### 3.2. Data format and representative example

This study prepares fine-tuning data in JSON format, which consists of a three-part structure: command-input-output (each entry contains command, input, and output fields). Each data entry may also contain metadata fields to indicate the source and process annotations. The following example illustrates this:

,,.

![[1-s2.0-S0920548926000371-gr1.jpg|Fig 1 dummy alt text]]

Download: Download high-res image (655KB)

![[1-s2.0-S0920548926000371-gr2.jpg|Fig 2 dummy alt text]]

Download: Download high-res image (720KB)

Table 1. The experiment models.

| Model | Source |
| --- | --- |
| DeepSeek-R1-Distill-Qwen-1.5B | [https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B) |
| Llama-Breeze2–3B-Instruct | [https://huggingface.co/MediaTek-Research/Llama-Breeze2-3B-Instruct](https://huggingface.co/MediaTek-Research/Llama-Breeze2-3B-Instruct) |
| Llama-3.2–3B-F1-Instruct | [https://huggingface.co/twinkle-ai/Llama-3.2-3B-F1-Instruct](https://huggingface.co/twinkle-ai/Llama-3.2-3B-F1-Instruct) |
| Qwen3–4B | [https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) |
| gemma-3–4b-it | [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) |
| Llama-3-Taiwan-8B-Instruct | [https://huggingface.co/yentinglin/Llama-3-Taiwan-8B-Instruct](https://huggingface.co/yentinglin/Llama-3-Taiwan-8B-Instruct) |

Table 2. System configuration.

| System OS | Ubuntu 20.04.6 LTS, 64-bit OS |
| --- | --- |
| Processor | Intel® Xeon(R) Gold 6242 CPU @ 2.80 GHz × 12 |
| Memory | 64 GB |
| Graphics Card (GPU) | 48GB Nvidia Quadro RTX8000 |

### 3.3. Small language models

Our study assesses a total of 6 unique models. We opt for various sizes for different family models, ranging from 1.5 billion to 8 billion parameters making them suitable for on-premises industrial RAG deployment. We defined small language models, models within the size range 1.5 B to 4B parameters. These models are comparatively smaller, ranging from 17 to 47 times less in parameter count than famous open-sourced large language models, such as Llama-3.3–70B Although Llama-3-Taiwan-8B-Instruct exceeds this strict parameter limit, it is explicitly included in this study as a mid-sized reference baseline. This allows for a comparative analysis between compact SLMs and a larger, more resource-intensive model to contextualize efficiency-quality trade-offs. These models were chosen based on their prevalence in literature and industrial experiment domain. The users primarily expressed themselves in Traditional Chinese. It was demonstrated that all language models selected for preliminary testing could generate responses in Traditional Chinese. We also selected several models that had undergone pre-training on Chinese corpora and were fine-tuned with instructions. The sources of these models are as shown in the table below.

### 3.4. Experimental Settings and system configuration

To examine and compare the generation evaluation of SLMs with fine-tuning, we used four open-source SLMs in our study: DeepSeek-R1-Distill-Qwen-1.5B, Llama-Breeze2–3B-Instruct, Gemma-3–4B-it, Qwen-3–4B, Llama-3.2–3B-F1-Instruct and Llama-3-Taiwan-8B-Instruct. The system configuration for model setup and fine-tuning is as follows:

During the model fine-tuning process, we adopted QLoRA as optimized fine-tuning techniques. Model fine-tuning was performed using the HuggingFace Trainer framework. To assess the robustness of parameter-efficient fine-tuning under low-resource conditions, we conducted a controlled sensitivity analysis on key training hyperparameters while keeping all other settings fixed using gemma3–4b-it. The default configuration used throughout the main experiments was epoch = 2, learning rate = 1e−4, LoRA rank *r* = 8, and batch size = 8. Starting from this baseline, we varied one hyperparameter at a time to isolate its effect: (i) epochs ∈ {1, 2, 4, 8}, (ii) learning rate ∈ {1e−4, 1e−5, 1e−6}, (iii) LoRA rank r ∈ {4, 8, 16, 32, 64}, and (iv) batch size ∈ {2, 4, 8, 16, 32}. This design avoids exhaustive grid search while enabling systematic examination of training stability and performance trends. The sensitivity results indicate that although certain metrics, such as factual correctness, are moderately influenced by specific hyperparameters, the overall performance trends and cross-model comparisons remain stable across a broad range of reasonable configurations. Based on this analysis, the baseline setting is adopted for all experiments to ensure a balanced trade-off between generation quality, training stability, and computational efficiency. Detailed sensitivity results are reported in.

Table 3. Fine-tuning configuration and hyperparameter selection.

| lora\_rank | epoch | batch | learning rate | train/train runtime(min) | Fal | AR | Fac |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 2 | 8 | 0.0001 | 27.288 | 0.973 | 0.832 | 0.750 |
| 16 | 2 | 8 | 0.0001 | 27.646 | 0.961 | 0.818 | 0.777 |
| 32 | 2 | 8 | 0.0001 | 28.037 | 0.969 | 0.830 | 0.801 |
| 64 | 2 | 8 | 0.0001 | 28.431 | 0.966 | 0.825 | 0.806 |
| 8 | 1 | 8 | 0.0001 | 13.681 | 0.978 | 0.841 | 0.735 |
| 8 | 4 | 8 | 0.0001 | 54.712 | 0.954 | 0.812 | 0.800 |
| 8 | 8 | 8 | 0.0001 | 109.434 | 0.877 | 0.818 | 0.817 |
| 8 | 2 | 2 | 0.0001 | 27.427 | 0.941 | 0.803 | 0.780 |
| 8 | 2 | 4 | 0.0001 | 27.386 | 0.957 | 0.820 | 0.784 |
| 8 | 2 | 16 | 0.0001 | 27.357 | 0.973 | 0.836 | 0.736 |
| 8 | 2 | 32 | 0.0001 | 27.345 | 0.963 | 0.828 | 0.716 |
| **8** | **2** | **8** | **0.0001** | **27.366** | **0.964** | **0.837** | **0.761** |
| 8 | 2 | 8 | 0.00001 | 27.355 | 0.954 | 0.849 | 0.640 |
| 8 | 2 | 8 | 0.000001 | 27.365 | 0.895 | 0.899 | 0.509 |

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness.

### 3.5. RAG Baseline configuration

The fine-tuned models were evaluated using 154 examples from customer service tests and 60 examples from internal regulatory tests for answer generation. The evaluation focused exclusively on generation performance. The same RAG prompt configuration was applied to the GPT-4o-mini baseline, which was evaluated in a zero-shot retrieval-augmented generation (RAG) setting. To ensure a controlled and fair comparison, the same retriever, the same top-2 retrieved documents, and the same RAG prompt template were used for both GPT-4o-mini and all SLMs. No few-shot demonstrations or task-specific fine-tuning were applied to GPT-4o-mini. All decoding parameters were fixed across runs. This configuration isolates the effect of parameter-efficient fine-tuning in SLMs from differences arising from prompting or retrieval strategies. The SLM generation prompt was defined as follows:

### 3.6. Data-scaling protocol

We experimented with varying data sizes, fine-tuning the model using 50, 100, 150, 200, 300, and 429 examples for the customer service dataset, and using 50, 100, 150, 200, and 334 examples for the internal regulation dataset. For the customer service dataset, training subsets of 50, 100, 150, and 200 samples were constructed exclusively from real-world annotated log data. For the internal regulation dataset, all available real-world annotations (119 samples) were used for the smaller training sizes (50, 100) before any synthetic augmentation was introduced. Synthetic RAG question–answer pairs were incorporated only when larger training sizes were required and the real annotations had been fully utilized in both datasets. Each fine-tuning iteration used identical hyperparameter settings and prompt configurations to ensure consistency across datasets and training scales. This design allows the study to examine performance trends and saturation behavior under low-resource domain adaptation, rather than to optimize absolute performance through large-scale supervision.

### 3.7. Evaluation Metrics of generation quality

Based on the research of Es et al. \[\], we use the RAGAS metrics to evaluate the generation quality of fine-tuned SLMs, including faithfulness, answer relevance, factual correctness, and F1 score. Generation quality refers to the effectiveness of the content produced by the generative model. To ensure consistency and fairness in the evaluation, all metrics are evaluated using GPT-4o as the reviewer, with automatic scoring and comparison performed according to the standardized RAGAS prompts. A description of each metric is as follows:

**Faithfulness.** It is described as the proportion of an LLM output to reference data or to a benchmark set. This dimension pertains to the need for model outputs not to be misguided on exaggerated, slanted, or uninformed assertions so that they are true-oriented. It is calculated like this:$Faithfulness=NumberofclaimsthatcanbeinferredfromgivencontextTotalnumberofclaimsinthegeneratedanswer$

**Answer Relevance.** The relevance measures are applied to measure the overlap of outputs and user provided input. Higher scores represent a closer correspondence between the responses and user intended meaning, while lower scores are assigned when answers miss crucial information or fail to accurately address the question at issue, or provide irrelevant content. It can be calculated:$AnswerRelevance=1N∑i=1Ncosinesimility(Egi,Eo)$ where *Eg <sub>i</sub>* is the embedding of the generated question *i, Eo* is the embedding of the original question, *N* is the number of generated questions.

**Factual Correctness.** Used to compare and assess the factual accuracy of generated responses against reference material. This metric determines how closely the generated response matches the reference material. Factual accuracy scores range from 0 to 1, with higher values indicating better performance. The formula for calculating True Positive (TP), False Positive (FP), and False Negative (FN) are as follows:

True Positive (TP)=Number of claims in the response that are also present in the reference.

False Positive (FP)=Number of claims in the response that are not present in the reference.

False Negative (FN)=Number of claims in the reference that are not present in the response.$Precision=TPTP+FP,Recall=TPTP+FN,F1Score=2×Precision×RecallPrecision+Recall$

**F1 Score.** This metric measures the average overlap between the predicted answer and the actual answer \[\]. Both the prediction and the ground truth are treated as bags of tokens, and their F1 score is calculated. For each question, the maximum F1 score among all ground truth answers is selected, and these scores are then averaged over all questions.

### 3.8. Cost-efficiency measure

For each model and evaluation metric—Faithfulness, Answer Relevancy, Factual Correctness, and F1—we quantified the marginal performance gain per unit of compute by comparing adjacent training data volumes. For a pair of experiments, A (smaller training size) and B (larger training size), we define cost-efficiency as follows:$ΔmetrixGPU−hour=metricB−metricAGPUhourB−GPUhourA$

Where A and B represent adjacent training data volume settings (e.g., from 100 to 150 samples). The metric refers to the quantitative measure being evaluated, while GPU-hours are derived by converting the wall-clock runtime (in minutes) recorded in the training log to hours (minutes ÷ 60). To estimate uncertainty, we apply a non-parametric bootstrap at the pair level (using 500 resamples) by resampling with replacement within groups A and B, computing the pairwise Δ(metric)/GPU-hour for each resample, and reporting the bootstrap mean along with the 95% percentile interval.

### 3.9. The taxonomy of hallucination

We proposed a heuristic framework for detecting the taxonomy of hallucination based on Huang et al. \[\], Ji et al. \[\], and Liu et al. \[\]. The goal is to enable the RAG system to automatically determine which type of error may have occurred based on the three quantitative evaluation scores generated by the model output, without relying on human labeling. The framework assigns hallucination-type labels to model outputs using three standardized automated metrics: faithfulness, factual correctness, and answer relevance. shows that a total of five taxonomy labels were identified, including Fabrication/Invented fact, Unsupported inference/Over-generalization, Misinterpretation/Low relevance, Suspected hallucination, and Low faithfulness.

Table 4. Heuristic annotation rules for automated taxonomy labeling.

| Code | Taxonomy label | Trigger condition | Interpretation/Rationale |
| --- | --- | --- | --- |
| FAB | Fabrication/Invented fact | factual ≤ 0.20 and faith ≥ 0.80 | Highly consistent with retrieved evidence but factually incorrect; indicates confident hallucination or fabricated statement. |
| UNSUP | Unsupported inference/Over-generalization | 0.20 < factual < 0.60 and faith < 0.80 | Contains partially correct content but extends beyond evidence or makes over-generalized claims. |
| MIS | Misinterpretation/Low relevance | relev ≤ 0.60 | Response misreads the prompt or diverges semantically from the user query; low topical alignment. |
| SUS | Suspected hallucination | factual ≤ 0.30 | Ensures coverage of low factual cases not captured by other rules; possible hallucination. |
| LF | Low faithfulness | faith ≤ 0.50 | Output loosely connected to retrieved context; potential misuse or misinterpretation of evidence. |

*factual* = factual correctness; *faith* = faithfulness; *relev* = answer relevancy.

## 4\. Results

### 4.1. Overall model performance

The evaluation models cover a wide range of architectural scales and design requirements, from compact, distilled models (1.5B) to region-specific instruction models (8B). These models will allow the study to examine the trade-off between efficiency and quality. For reference, GPT-4o-mini was evaluated as a baseline under the same zero-shot retrieval-augmented generation (RAG) configuration, using identical retrievers, top-2 retrieved documents, and prompt templates, without task-specific fine-tuning.

presents the comparative performance of all evaluated SLMs for customer service RAG logs across four primary metrics—faithfulness, answer relevance, factual correctness, and F1 score—using the held-out enterprise test set. Averaged across architectures and data-scaling configurations, the mean scores were as follows: faithfulness = 0.937, answer relevance = 0.847, factual correctness = 0.668, and F1 = 0.653. The best-performing models for each metric are: Qwen3–4B, which achieved the highest faithfulness (0.973), indicating superior grounding to retrieved evidence; Llama-3.2–3B-F1, which attained the best answer relevance (0.904), reflecting effective contextual alignment; and Llama-Breeze2–3B, which outperformed others in both factual correctness (0.776) and overall F1 score (0.765). These findings suggest that the evaluated SLMs exhibit complementary performance profiles rather than a single dominant architecture. Specifically, Qwen excels in evidence-grounded generation, Llama-3.2 variants prioritize contextual relevance, and Breeze2 demonstrates stronger factual correctness and end-task balance—highlighting the trade-offs inherent in optimizing multi-objective RAG reasoning tasks.

Tabel 5. Comparison of overall model performance for customer service RAG logs.

<table><thead><tr><th>Model</th><th>Training size</th><th>Fal</th><th>AR</th><th>Fac</th><th>F1</th></tr></thead><tbody><tr><td rowspan="7">MediaTek-Research/Llama-Breeze2–3B-Instruct</td><td>No Finetuned</td><td>0.856</td><td>0.856</td><td>0.454</td><td>0.481</td></tr><tr><td>50</td><td>0.9</td><td>0.897</td><td>0.529</td><td>0.559</td></tr><tr><td>100</td><td>0.901</td><td>0.852</td><td>0.643</td><td>0.647</td></tr><tr><td>150</td><td>0.933</td><td>0.872</td><td>0.698</td><td>0.707</td></tr><tr><td>200</td><td>0.954</td><td>0.82</td><td>0.735</td><td>0.723</td></tr><tr><td>300</td><td>0.94</td><td>0.824</td><td>0.757</td><td>0.727</td></tr><tr><td>429</td><td>0.968</td><td>0.82</td><td>0.776</td><td>0.765</td></tr><tr><td rowspan="7">Google/gemma–3–4b-it</td><td>No Finetuned</td><td>0.902</td><td>0.886</td><td>0.525</td><td>0.499</td></tr><tr><td>50</td><td>0.954</td><td>0.849</td><td>0.599</td><td>0.562</td></tr><tr><td>100</td><td>0.962</td><td>0.823</td><td>0.719</td><td>0.649</td></tr><tr><td>150</td><td>0.962</td><td>0.833</td><td>0.699</td><td>0.668</td></tr><tr><td>200</td><td>0.945</td><td>0.824</td><td>0.725</td><td>0.69</td></tr><tr><td>300</td><td>0.948</td><td>0.806</td><td>0.72</td><td>0.69</td></tr><tr><td>429</td><td>0.968</td><td>0.837</td><td>0.76</td><td>0.729</td></tr><tr><td rowspan="7">Qwen/Qwen3–4B</td><td>No Finetuned</td><td>0.886</td><td>0.897</td><td>0.537</td><td>0.5</td></tr><tr><td>50</td><td>0.919</td><td>0.896</td><td>0.54</td><td>0.548</td></tr><tr><td>100</td><td>0.93</td><td>0.824</td><td>0.677</td><td>0.627</td></tr><tr><td>150</td><td>0.968</td><td>0.839</td><td>0.674</td><td>0.659</td></tr><tr><td>200</td><td>0.962</td><td>0.822</td><td>0.719</td><td>0.691</td></tr><tr><td>300</td><td>0.973</td><td>0.84</td><td>0.721</td><td>0.701</td></tr><tr><td>429</td><td>0.96</td><td>0.83</td><td>0.731</td><td>0.709</td></tr><tr><td rowspan="7">twinkle-ai/Llama-3.2–3B-F1-Instruct</td><td>No Finetuned</td><td>0.810</td><td>0.855</td><td>0.470</td><td>0.42</td></tr><tr><td>50</td><td>0.849</td><td>0.904</td><td>0.512</td><td>0.491</td></tr><tr><td>100</td><td>0.887</td><td>0.879</td><td>0.545</td><td>0.572</td></tr><tr><td>150</td><td>0.904</td><td>0.878</td><td>0.55</td><td>0.581</td></tr><tr><td>200</td><td>0.923</td><td>0.85</td><td>0.63</td><td>0.627</td></tr><tr><td>300</td><td>0.942</td><td>0.857</td><td>0.662</td><td>0.66</td></tr><tr><td>429</td><td>0.947</td><td>0.858</td><td>0.721</td><td>0.686</td></tr><tr><td rowspan="7">deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B</td><td>No Finetuned</td><td>0.606</td><td>0.808</td><td>0.320</td><td>0.226</td></tr><tr><td>50</td><td>0.693</td><td>0.885</td><td>0.406</td><td>0.316</td></tr><tr><td>100</td><td>0.766</td><td>0.866</td><td>0.480</td><td>0.406</td></tr><tr><td>150</td><td>0.856</td><td>0.835</td><td>0.622</td><td>0.537</td></tr><tr><td>200</td><td>0.813</td><td>0.843</td><td>0.599</td><td>0.573</td></tr><tr><td>300</td><td>0.853</td><td>0.836</td><td>0.653</td><td>0.614</td></tr><tr><td>429</td><td>0.884</td><td>0.839</td><td>0.710</td><td>0.657</td></tr><tr><td rowspan="7">yentinglin/Llama-3-Taiwan-8B-Instruct</td><td>No Finetuned</td><td>0.891</td><td>0.892</td><td>0.563</td><td>0.542</td></tr><tr><td>50</td><td>0.948</td><td>0.860</td><td>0.659</td><td>0.636</td></tr><tr><td>100</td><td>0.925</td><td>0.846</td><td>0.661</td><td>0.622</td></tr><tr><td>150</td><td>0.940</td><td>0.823</td><td>0.695</td><td>0.639</td></tr><tr><td>200</td><td>0.946</td><td>0.821</td><td>0.738</td><td>0.702</td></tr><tr><td>300</td><td>0.949</td><td>0.809</td><td>0.786</td><td>0.731</td></tr><tr><td>429</td><td>0.945</td><td>0.820</td><td>0.760</td><td>0.740</td></tr><tr><td>Means of Fine-Tuned SLMs</td><td></td><td>0.917</td><td>0.845</td><td>0.661</td><td>0.634</td></tr><tr><td>gpt-4o-mini</td><td></td><td>0.91</td><td>0.895</td><td>0.586</td><td>0.531</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

The performance comparison of all SLMs assessed on the internal regulation RAG logs across four primary metrics is shown in. The average performance of fine-tuned SLMs on these metrics is 0.865 for faithfulness, 0.895 for answer relevance, 0.488 for factual correctness, and 0.533 for F1 score, respectively. These performance values are expected given the increased difficulty levels and stricter evidence sourcing demands required by regulation-oriented questions as compared to customer service questions. On each individual metric, models display disparate merits as compared to a single overall preference to any given architecture. Qwen3–4B reports the highest value on the faithfulness metric (0.947), corroborating high evidence groundedness and appropriateness to the searched-for regulation texts. Llama-3-Taiwan-8B-Instruct reports the highest value on the answer relevance metric (0.935), establishing supremacy over others regarding question-targeted appropriateness to formal policy questions. However, Qwen3–4B and Llama-Breeze2–3B-Instruct demonstrate competitive performance on factual correctness, with highest values reported as 0.576 and 0.530, respectively, and Qwen3–4B reports the highest value on overall F1 score with 0.622.

Tabel 6. Comparison of Overall model performance for internal regulations RAG logs.

<table><thead><tr><th>Model</th><th>Training size</th><th>Fal</th><th>AR</th><th>Fac</th><th>F1</th></tr></thead><tbody><tr><td rowspan="6">MediaTek-Research/Llama-Breeze2–3B-Instruct</td><td>No Finetuned</td><td>0.878</td><td>0.691</td><td>0.425</td><td>0.402</td></tr><tr><td>50</td><td>0.889</td><td>0.879</td><td>0.555</td><td>0.499</td></tr><tr><td>100</td><td>0.920</td><td>0.939</td><td>0.512</td><td>0.553</td></tr><tr><td>150</td><td>0.905</td><td>0.920</td><td>0.544</td><td>0.537</td></tr><tr><td>200</td><td>0.883</td><td>0.884</td><td>0.555</td><td>0.573</td></tr><tr><td>334</td><td>0.916</td><td>0.933</td><td>0.554</td><td>0.570</td></tr><tr><td rowspan="6">Google/gemma–3–4b-it</td><td>No Finetuned</td><td>0.936</td><td>0.897</td><td>0.504</td><td>0.543</td></tr><tr><td>50</td><td>0.854</td><td>0.882</td><td>0.462</td><td>0.466</td></tr><tr><td>100</td><td>0.922</td><td>0.922</td><td>0.542</td><td>0.569</td></tr><tr><td>150</td><td>0.913</td><td>0.926</td><td>0.521</td><td>0.578</td></tr><tr><td>200</td><td>0.895</td><td>0.927</td><td>0.519</td><td>0.564</td></tr><tr><td>334</td><td>0.930</td><td>0.930</td><td>0.568</td><td>0.594</td></tr><tr><td rowspan="6">Qwen/Qwen3–4B</td><td>No Finetuned</td><td>0.917</td><td>0.865</td><td>0.524</td><td>0.562</td></tr><tr><td>50</td><td>0.940</td><td>0.908</td><td>0.561</td><td>0.595</td></tr><tr><td>100</td><td>0.934</td><td>0.921</td><td>0.535</td><td>0.537</td></tr><tr><td>150</td><td>0.935</td><td>0.921</td><td>0.566</td><td>0.612</td></tr><tr><td>200</td><td>0.943</td><td>0.920</td><td>0.548</td><td>0.611</td></tr><tr><td>334</td><td>0.932</td><td>0.938</td><td>0.557</td><td>0.622</td></tr><tr><td rowspan="6">twinkle-ai/Llama-3.2–3B-F1-Instruct</td><td>No Finetuned</td><td>0.829</td><td>0.889</td><td>0.367</td><td>0.402</td></tr><tr><td>50</td><td>0.831</td><td>0.909</td><td>0.425</td><td>0.499</td></tr><tr><td>100</td><td>0.858</td><td>0.917</td><td>0.519</td><td>0.553</td></tr><tr><td>150</td><td>0.871</td><td>0.920</td><td>0.460</td><td>0.537</td></tr><tr><td>200</td><td>0.869</td><td>0.906</td><td>0.495</td><td>0.573</td></tr><tr><td>334</td><td>0.864</td><td>0.937</td><td>0.529</td><td>0.570</td></tr><tr><td rowspan="6">deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B</td><td>No Finetuned</td><td>0.580</td><td>0.729</td><td>0.240</td><td>0.258</td></tr><tr><td>50</td><td>0.608</td><td>0.804</td><td>0.310</td><td>0.280</td></tr><tr><td>100</td><td>0.724</td><td>0.871</td><td>0.271</td><td>0.255</td></tr><tr><td>150</td><td>0.747</td><td>0.915</td><td>0.289</td><td>0.332</td></tr><tr><td>200</td><td>0.738</td><td>0.899</td><td>0.289</td><td>0.335</td></tr><tr><td>334</td><td>0.794</td><td>0.922</td><td>0.323</td><td>0.419</td></tr><tr><td rowspan="6">yentinglin/Llama-3-Taiwan-8B-Instruct</td><td>No Finetuned</td><td>0.898</td><td>0.912</td><td>0.486</td><td>0.531</td></tr><tr><td>50</td><td>0.926</td><td>0.908</td><td>0.544</td><td>0.582</td></tr><tr><td>100</td><td>0.916</td><td>0.933</td><td>0.537</td><td>0.596</td></tr><tr><td>150</td><td>0.918</td><td>0.935</td><td>0.554</td><td>0.592</td></tr><tr><td>200</td><td>0.914</td><td>0.930</td><td>0.550</td><td>0.617</td></tr><tr><td>334</td><td>0.932</td><td>0.930</td><td>0.530</td><td>0.620</td></tr><tr><td>Means of Fine-Tuned SLMs</td><td></td><td>0.865</td><td>0.895</td><td>0.488</td><td>0.533</td></tr><tr><td>gpt-4o-mini</td><td></td><td>0.918</td><td>0.881</td><td>0.578</td><td>0.554</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

The larger Llama-3-Taiwan-8B-Instruct model shows consistent and robust performance across all metrics but is not necessarily better than smaller SLM models in general, especially in regard to factual accuracy. At the same time, the DeepSeek-R1-Distill-Qwen-1.5B model, which has fewer parameters but otherwise shows consistent improvement in regard to the trained sample size, is still less advanced in regard to factual accuracy. These patterns confirm that smaller SLM models are still complementary in regard to regulation-oriented retrieval and generative tasks. In summary, optimization of models for evidence grounding, contextuality, and factuality of models targets different aspects of regulation-oriented reasoning in their own right and illustrates that optimization for multiple criteria faces underlying challenges when models are applied in low-resource settings concerning regulation.

### 4.2. Learning curves: metric vs train size

The mean learning curves of SLMs across four evaluation metrics for RAG tasks are illustrated in as a function of training set size. For the customer service dataset (), faithfulness increases steadily from approximately 0.88 to 0.96 as training size grows from 50 to 429 samples, indicating improved alignment between generated responses and retrieved evidence. In contrast, answer relevance decreases from around 0.90 to approximately 0.82, reflecting a shift from semantically expansive responses toward more evidence-constrained and conservative generation behavior as fine-tuning reinforces reliance on retrieved documents. Factual correctness exhibits a consistent upward trend, rising from 0.57 to 0.75, while overall generation quality, measured by F1 score, improves from 0.52 to 0.73 with increasing training data.

![[1-s2.0-S0920548926000371-gr3.jpg|Fig 3 dummy alt text]]

Download: Download high-res image (421KB)

Moreover, there is a similar learning curve for the internal regulation question dataset (). The results showed a simultaneous increase in faithfulness, factual correctness, and F1 score. However, once a certain level of training is reached, there is a tendency towards saturation of the curves. The absolute improvement measures are not as drastic as the internal regulation dataset, compared to those in the customer service field. There is a plateau in the relevance of responses, and it does not change much with more training.

In case of customer service data, sets of 229 labeled samples maximum were created solely based on actual-world RAG logs. Their respective learning curves show greater rates of improvement in factual correctness as well as F1 score, especially between 50 and 200 samples before leveling off. These trends imply that domain-related data of small quantities is adequate to significantly improve end-task performance on conversational RAG tasks. In contrast, the internal regulation dataset demonstrates more conservative absolute gains and wider variability bands, especially for factual correctness and F1. This is expected given the smaller dataset size and the more formal, document-centric nature of regulation queries, which require stricter evidence alignment and longer-context reasoning. Nevertheless, the directionality of improvement remains consistent, with no evidence of performance degradation as training size increases.

### 4.3. Δ(metric)/GPU-hour analysis

The marginal improvement in each quality metric per GPU-hour (Δ(metric)/GPU-hour) is reported in and for the cost-efficiency analysis among two different datasets. Marginal gains were estimated in each incremental step of training size over four important dimensions: faithfulness, relevance, factual correctness, and F1 score. Activation patterns are found to have varied efficiency profiles among model structures. In the customer service dataset (), the gemma-3–4b-it model exhibits a similarly balanced cost-effectiveness, with +0.317 factual correctness and +0.309 F1 per GPU-hour, mild gains in answer relevance (+0.246) and faithfulness (+0.159). The Llama-3.2–3B-F1-Instruct shows the largest marginal gain in factual correctness (+0.488 per GPU-hour) and a decent increase in F1 (+0.215), with marginal improvements on faithfulness (+0.041) and relevance (+0.008). Llama-Breeze2–3B-Instruct, on the other hand, compares favourably only in terms of efficiency for F1 (+0.300) and faithfulness (+0.221), with a drop in relevance (−0.032), corresponding to a precision-context tradeoff aspect. In contrast, Qwen-3–4B has near-zero or negative marginal efficiency in most of the metrics (F1 +0.049, factual correctness +0.062, faithfulness −0.080, relevance −0.062), stressing there are diminishing returns under our fine-tuning setting currently. Additionally, we further examined the larger and smaller model parameter size (Llama-3-Taiwan-8B-Instruct and DeepSeek-R1-Distill-Qwen-1.5B). The DeepSeek-R1-Distill-Qwen-1.5B model demonstrates relatively strong cost-efficiency despite its smaller model size. It achieves marginal gains of approximately +0.300 in F1 score and +0.305 in factual correctness per GPU-hour, along with moderate improvements in faithfulness (+0.167) and answer relevance (+0.048). The Llama-3-Taiwan-8B-Instruct model shows limited marginal gains across all evaluated metrics, with small positive improvements in F1 score (+0.115), factual correctness (+0.078), faithfulness (+0.038), and answer relevance (+0.014).

![[1-s2.0-S0920548926000371-gr4.jpg|Fig 4 dummy alt text]]

Download: Download high-res image (601KB)

Table 7. Δ(metric)/GPU-hour summary for each model and metric.

<table><thead><tr><th>Dataset</th><th>Model</th><th>F1</th><th>Fac</th><th>Fail</th><th>AR</th></tr></thead><tbody><tr><td rowspan="6">Customer service logs</td><td>Llama-3-Taiwan-8B-Instruct</td><td>0.117</td><td>0.079</td><td>0.039</td><td>0.015</td></tr><tr><td>Llama-3.2–3B-F1-Instruct</td><td>0.215</td><td>0.488</td><td>0.041</td><td>0.008</td></tr><tr><td>Llama-Breeze2–3B-Instruct</td><td>0.300</td><td>0.150</td><td>0.221</td><td>-0.032</td></tr><tr><td>Qwen3–4B</td><td>0.049</td><td>0.062</td><td>-0.080</td><td>-0.062</td></tr><tr><td>gemma–3–4b-it</td><td>0.309</td><td>0.317</td><td>0.159</td><td>0.246</td></tr><tr><td>DeepSeek-R1-Distill-Qwen-1.5B</td><td>0.299</td><td>0.306</td><td>0.167</td><td>0.049</td></tr><tr><td rowspan="6">Internal Regulations logs</td><td>Llama-3-Taiwan-8B-Instruct</td><td>0.076</td><td>-0.003</td><td>-0.01</td><td>0.045</td></tr><tr><td>Llama-3.2–3B-F1-Instruct</td><td>0.081</td><td>0.23</td><td>-0.033</td><td>0.21</td></tr><tr><td>Llama-Breeze2–3B-Instruct</td><td>0.018</td><td>-0.006</td><td>0.197</td><td>0.293</td></tr><tr><td>Qwen3–4B</td><td>0.053</td><td>0.044</td><td>-0.053</td><td>0.088</td></tr><tr><td>gemma–3–4b-it</td><td>0.170</td><td>0.272</td><td>0.198</td><td>0.017</td></tr><tr><td>DeepSeek-R1-Distill-Qwen-1.5B</td><td>0.534</td><td>0.216</td><td>0.356</td><td>0.146</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

In the internal regulation dataset (), a markedly different cost-efficiency pattern is observed. The DeepSeek-R1-Distill-Qwen-1.5B model again has the strongest marginal improvement profile, showing the strongest F1Score improvement (roughly +0.53 every GPU hour) and concurrent strong improvements in faithfulness and answer relevance. Although this model has only small sized parameters, it is still the most cost-efficient in the regulatory environment where rigid adherence to rigorously formatted and legally bound source texts is required. Conversely, for several larger-parameter models, notable trade-offs between answer relevance and faithfulness are observed in the internal regulation setting. In particular, the Llama-3.2–3B-F1-Instruct model exhibits a positive marginal improvement in answer relevance (+0.21) while simultaneously showing a reduction in faithfulness (−0.033), suggesting an increased tendency to generate contextually appropriate responses that are progressively less anchored to the retrieved regulatory evidence. Analogously, the gemma-3–4b-it model demonstrates positive marginal improvements in factual correctness (+0.272); however, this gain is accompanied by only minimal improvement in answer relevance (+0.017), indicating that increases in factual precision do not necessarily translate into stronger question–document alignment in the regulatory context.

Consistent with observations from the customer service dataset, Qwen-3–4B shows near-zero or negative marginal gains in faithfulness (−0.053). The overall implication of these findings is that, in high-stakes regulatory scenarios, improvements in surface-level appropriateness or factual accuracy may occur alongside a deterioration in source adherence, underscoring the importance of cost-normalized evaluation when selecting models for compliance-oriented RAG applications.

### 4.4. Error analysis (hallucination taxonomy)

Building on the finetuning results for factual accuracy and F1 performance, we conducted a taxonomy-based analysis of hallucination patterns using the MediaTek-Research/Llama-Breeze2–3B-Instruct model in customer service log dataset. To assess the impact of domain-specific fine-tuning, we compared the heuristic taxonomy distributions of the fine-tuned and unfine-tuned models under identical evaluation conditions.

As illustrated in a, hallucinations were prevalent prior to adaptation. Among the 154 responses generated by the unfine-tuned model, only 90 (58.4%) were labeled as No major issue (OK), while the remaining 64 cases exhibited various error types: Fabrication (FAB, 28), Suspected hallucination (SUS, 17), Misinterpretation or Low relevance (MIS, 8), Unsupported inference (UNSUP, 7), and Low faithfulness (LF, 1). According to the results of domain-specific fine-tuning on industrial customer service RAG logs, we found that the hallucination rate decreased significantly. 84.4% (130/154) no major issues (OK) were reported, with the remaining outputs categorized as FAB (12), MIS (4), SUS (4), LF (1), FAB + MIS (1), UNSUP + MIS (1), and UNSUP (1), indicating strong alignment between automated and human evaluations of factual adequacy.

![[1-s2.0-S0920548926000371-gr5a.jpg|Fig 5 dummy alt text]]

Download: Download high-res image (165KB)

A comparison between -a and -b shows a 26-point rise in outputs, accompanied by no major issues, and a significant decrease in instances of fabrication and unsupported inferences. These findings provide empirical evidence that fine-tuning with domain-specific RAG data significantly reduces hallucinations, improving factual correctness and alignment with evidence in industrial knowledge retrieval applications.

In the internal regulation dataset, we observed a slight improvement after model fine-tuning. A total of six additional items were labeled as No major issue (OK), with the remaining outputs categorized as UNSUP (7), FAB (6), and SUS (1). Overall, despite the limitations imposed by the small sample size, a marginal improvement in the fine-tuned model's RAG answer generation can still be observed ().

![[1-s2.0-S0920548926000371-gr6a.jpg|Fig 6 dummy alt text]]

Download: Download high-res image (150KB)

## 5\. Discussion

### 5.1. Interpretation of findings

The present study investigated the factual reliability, computational efficiency, and stability of SLMs when adopting domain-specific fine-tuning for the RAG models. This is based on the same zero-shot RAG setup because the fine-tuned SLMs had comparable performance with respect to faithfulness and factual accuracy to GPT-4o-mini and showed a substantial improvement over their non-fine-tuned models for the same datasets. These findings align with prior studies showing that SLMs can reach LLM-comparable accuracy when adapted through domain-specific fine-tuning (\[\]; Kwon et al., 2025; \[\]).

In addition, the results of learning curve analysis showed that the greatest performance improvements occurred between 50 and 200 annotated cases for the customer service data, beyond which performance gains became marginal. For the internal regulation dataset, a similar saturation pattern was observed at a smaller scale, with performance stabilizing once the training size reached approximately 100 real-world annotated samples. Faithfulness had a monotonically increasing trend, while the relevance of the answers had a non-monotonic trend, first reducing and then settling on averages ranging between 0.83 and 0.84. This trend reveals an increasing trend toward being more conservative in extraction as the accuracy of facts and evidential support is steadily incremented via fine-tuning. This observation is consistent with the findings of Lin et al. \[\], which indicate that factuality-aware alignment approaches not only guide language models to produce more precise and reliable responses but also reduce the likelihood of generating unsupported or false claims.

There were evident trade-offs between efficiency and quality of response in each model architecture through the Δ(metric)/GPU-hour analysis. On the customer service task, gemma-3–4B-it was the model with the largest marginal improvement in factual accuracy (+0.317) and F1 score (+0.309), trailed closely by Llama-Breeze2–3B-Instruct, which was efficient in F1 (+0.300) and Faithfulness (+0.221). Conversely, on the internal regulation task, DeepSeek-R1-Distill-Qwen-1.5B was the model with the highest cost efficiency, as it achieved the largest marginal improvement in F1 score of +0.534 per GPU-hour along with large gains in both Faithfulness (+0.356) and Answer Relevance (+0.146). On both tasks, the marginal returns on each increase in model scale were diminishing in nature, so as to support the observations made in the studies of Tian et al. \[\] & Yuan et al. \[\] on the early saturation in performance gains through excessive supervision.

Moreover, an analysis of the hallucination types between the original and the fine-tuned SLMs through a hallucination analysis showed a dramatic decrease in the errors of generation after the domain-specific fine-tuning. In the customer service corpus, the “No major issue” category increased from 58.4% to 84.4%, while in the internal regulation corpus, although the results were limited by the small sample size, there was a reduction in the number of fabrications and unsupported inferences with a considerable number of additional outputs qualified as having no major issues after performing the domain-specific fine-tuning. These findings are in line with an existing body of research which has established the efficacy of domain-specific fine-tuning in diminishing hallucinations and boosting factual alignment in various industrial tasks \[,,\].

Overall, the results affirm that small, domain-adapted models, when fine-tuned with factuality-aware objectives, can attain LLM-comparable factual reliability at a fraction of the computational cost. Nevertheless, the observed performance saturation and semantic narrowing highlight the importance of balanced optimization. Future research should pursue hybrid alignment strategies that preserve expressive diversity while consolidating factual accuracy and evidential grounding \[,\].

### 5.2. Limitation

While our findings demonstrate that fine-tuned SLMs can rival GPT-4o-mini and significantly reduce the answer generation of hallucination in using RAG pipeline, several limitations warrant consideration. The impact of different dataset sizes and hallucination taxonomy analysis on fine-tuning language models in specific domains still requires extensive verification. Despite the encouraging results of this experiment, there are some limitations to its size that must be considered when evaluating real-world data. While absolute performance may vary with larger datasets, the observed relative trends – such as early performance saturation and trade-offs between factuality, relevance, and efficiency – remain informative for low-resource industrial RAG scenarios. Therefore, any generalization about other enterprise settings may not be applicable. The application of this experiment to real-world settings of increasing size is a high-priority area for future exploration. This study mainly provides companies with a reference for feasible solutions for fine-tuning language models through the analysis of empirical data. These limitations frame, rather than undermine, the contribution and point to clear steps for broader verification.

## 6\. Conclusion

In conclusion, this study shows that retrieval-augmented SLMs still have residual hallucination behaviors even in evidence-aware configurations, particularly in terms of the indicators of factual correctness and F1 score performance. However, the results of domain-specific fine-tuning demonstrate that it could reduce the hallucinations of answer generation, thus enhancing both indicators. Moreover, we examined the marginal improvement values per GPU-hour across each quality metric, estimating the marginal gains at each incremental stage of training scale for four key dimensions: fidelity, relevance, factual accuracy, and F1 score. Finally, we proposed a practical heuristic hallucination taxonomy framework that could detect the error pattern of answer generation quality in RAG systems. Future work could extend this research by scaling taxonomy validation in different domains and integrate the automated detectors with RAG systems.

## Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this work the author(s) used ChatGPT and Wordvice AI in order to writing assistance. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article.

## CRediT authorship contribution statement

**Kai-Chih Pai:** Writing – review & editing, Writing – original draft, Supervision, Project administration, Formal analysis, Data curation, Conceptualization. **Wen-Chuan Hsu:** Methodology, Formal analysis.

## Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgement

We would like to thank the National Science and Technology Council (NSTC ), DDS-THU AI center and SAKURA Company for supporting this project.

## Data availability

The data that has been used is confidential.

## References

[^1]: ## 1\. Introduction

The rise of large language models (LLMs) has changed the nature of natural language processing (NLP): they can achieve state-of-the-art performance on knowledge intensive reasoning tasks and for open domain conversational systems. Even with these advances, however, their parametric knowledge is a static field that is difficult to interpret and susceptible to factual hallucination \[,\]. Recent work incorporates a generative model with an external read-only non-parametric memory for better generative factuality and interpretability \[,\], which is referred to as Retrieval-Augmented Generation (RAG) models, filling the mentioned gaps. However, deployment in practice introduces new challenges regarding how to balance model size, latency and cost trade-offs; protecting data ethics and locality; domain specific robustness requirements for safety critical applications \[,\]. These concerns have influenced the trend toward Small Language Models (SLMs) which have computational efficiency in performing the task of interest, however, and support reliable on-premises and edge deployment \[, \].

The development of SLMs has been investigated for applications in specialized fields such as industry and science. Previous research has shown that lightweight, task-specific configurations can achieve performance comparable to or even superior performance to LLMs in tasks like industrial text classification and content moderation, particularly under realistic computational and latency constraints \[, \]. Biomedicine-oriented applications entail competitive comprehension and generation performance for bilingual SLMs such as BioQwen while making use of quantized equivalents for mobile and embedded platform utilization \[\]. Similarly, data-intensive fine-tuning methods improve technical requirement accuracy extracted by SLMs to human-level dependability while keeping confidentiality through local computation \[\]. Domain adaptation also holds true for technical commercialization and industrial question-responding tools where expertly curated datasets find highly augmented contextual and factually correct pertinence by compact model fine-tuning \[,\]. Viewed from the angle of edge computing, SLM models that have undergone training by way of parameter-efficient fine-tuning (PEFT) and quantization yield low-latency operation amenable to a wide variety of scenarios such as handheld instrumentation and industrial automation controls \[,\].

Despite significant progress in related fields, ensuring the reliability of language models remains a significant and pressing challenge. The definition of hallucination in traditional natural language generation research includes: the generated content is meaningless or inconsistent with the original content. When hallucination occurs in language models, it will have a negative impact on applications in specific sensitive fields, such as medicine, law, and policy \[,\]. While retrieval-augmented generation (RAG) methods have mitigated some of these factual discrepancies, even with highly accurate retrieval results, models can still misinterpret evidence or provide only superficial arguments, leading to persistent issues of factual errors and insufficient fidelity \[,,\].

Several studies have proposed approaches to mitigate hallucination in the RAG pipeline. For instance, evidence re-ranking mechanisms and automated evaluation pipelines such as RAGAS have been employed to enhance factual accuracy and semantic coherence to reduce reliance on manual annotation \[,,\]. Other research has focused on model adaptation and fine-tuning approaches including both full and parameter-efficient methods such as LoRA and QLoRA, which improve model fidelity and reasoning capabilities when generalizing to domain-specific data \[,,\]. Farquhar et al. \[\] proposed an uncertainty perception decoding technique and semantic entropy estimation method that can promptly eliminate false or unfounded outputs, thereby enhancing the reliability of language models in zero-reference scenarios. Moreover, task-oriented learning strategies (such as solution-guided fine-tuning (SGFT)) can enhance logical reasoning in low-data environments \[\], while curriculum-based techniques (such as arithmetic GPT) can develop procedural and numerical reasoning abilities in small models \[\].

In spite of the fast-methodological development, empirical studies still suffer from fundamental limitations. Standard datasets that emerge heavily in the literature are either synthetic or public and cannot represent the heterogeneity, sparsity, and temporal drift typical of enterprise-wide data. Thus, domain-specific evidence on characterizing residual hallucination in deployed, self-improving models—especially within end-to-end RAG pipelines under privacy, computational, and annotation scarcity constraints—is lacking. Moreover, any existing taxonomies on hallucination are largely descriptive and detection-driven in nature, overlooking failure modes like misattribution, overgeneralization, and context drift witnessed in clinical (Huang et al., 2024) and policy-centric applications \[\]. From a practical perspective, instead of static accuracy benchmarks, practitioners should also consider utility-oriented evaluation that involves marginal efficiency metrics (e.g., fidelity improvement per GPU-hour or data increment) to weigh the model quality against resource consumption \[,\].

This study employs an empirical approach, utilizing real-world industrial customer service and formal internal regulatory documents RAG logs to compare the performance differences between untrained models and models trained on scaled datasets across multiple single-language models (SLMs) and GPT-4o-mini. It further examines the quality improvements and computational costs associated with quantitative fine-tuning. We also proposed a heuristic hallucination taxonomy and developed classification criteria based on root cause analysis. The primary contributions of this research can be summarized as follows:
- (1)
	Empirical evidence of residual hallucinations in RAG and mitigation via fine-tuning.
	We provide empirical evidence demonstrating that RAG systems still produce unfounded or erroneous outputs in SLMs; employ automated metrics to quantify hallucination rates; and confirm that domain-specific fine-tuning significantly reduces such errors.
- (2)
	Systematic analysis of training-data scaling on four quality metrics and its cost–benefit implications (Δmetric per GPU-hour).
	We systematically quantify how varying training-data volumes affect faithfulness, response relevancy factual correctness, and F1 score across multiple SLMs, and we introduce Δ(metric)/GPU-hour as a practical cost-efficiency measure to identify diminishing returns.
- (3)
	Development of a heuristic hallucination taxonomy.
	We develop and validate a practical heuristic hallucination taxonomy framework for RAG systems based on SLMs. This framework employs automated heuristic methods and has been validated through human gold-standard ratings of 154 samples.

## 2\. Related work

### 2.1. Small language models and parameter-efficient fine-tuning

Recent developments of parameter-efficient fine-tuning (PEFT) approaches have reshaped the flexibility of pre-trained models by considerably lowering the computational and memory budgets for domain transfer. Methods such as LoRA \[\], QLoRA \[\] and other adapter-based architectures achieve selective low-rank updates during training to few weights, retaining the generalization power of epic models at a faster pace for task-specific learning. For example, the empirical results of Zhang et al. \[\] and Kwon et al. (2025) show that small language models (SLMs) can achieve the same level of accuracy as LLMs while having much fewer parameters and energy consumption. Other related works on model compression, quantization, and domain-adaptive fine-tuning further justified SLMs to be promising for edge deployment and industrial-scale applications with limited resources \[,\]. Since PEFT only optimizes a partial set of parameters, the evaluation framework has been increasingly focusing on efficiency-normalized comparison—whether per unit investment of computational resource can be achieved. In this spirit, we take an efficiency-centric view in our study and cast Δ(metric)/GPU-hour as a quantitative measure to quantify reduction in data scaling efficiencies and returns of fine-tuned SLMs.

### 2.2. Hallucination of large language models

Research on hallucinations in large-scale language models (LLMs) has reached an advanced stage, encompassing frameworks for definition, benchmarking, and automated detection techniques. Previous research has primarily categorized hallucinations into two types: intrinsic hallucinations (arising from internal flaws in model inference) and extrinsic hallucinations (occurring when generated content contradicts existing evidence or memory contexts) \[, \]. Previous research has primarily categorized hallucinations into two types: intrinsic hallucinations, stemming from internal flaws in model reasoning; and extrinsic hallucinations, occurring when generated content conflicts with existing evidence or contextual memory \[, \]. Other studies have proposed classification frameworks for hallucination evaluation. For example, HalluLens evaluates general factual accuracy \[\], whereas HalluCode and assessments at the repository level concentrate on hallucinations in program synthesis and code generation \[,\]. These studies show that combined accuracy metrics can mask a variety of failure types, including outright fabrication, unsupported reasoning, and partially or inconsistently correct logic.

Furthermore, previous studies proposed methods for detecting hallucinations. Manakul, Liusie, and Gales \[\] proposed the SelfCheckGPT, a simple sampling-based approach that can be used to fact-check the responses of black-box models in a zero-resource fashion. However, the detection of subtle or complex hallucinations is still an open problem. Further, even RAG models suffer from extrinsic hallucinations in multi-hop reasoning or specialized domain settings, suggesting that the presence of retrieval does not ensure factual faithfulness. In a collective sense, this hierarchical accounting provides the conceptual underpinning for efficient light-weight heuristics (intended to support further scalable and semi-automatic hallucination annotations subsequently confirmed via formal human verification in our study).

### 2.3. Mitigation strategies and taxonomic frameworks

Modern hallucination reduction methods employ retrieval-based grounding and promotion optimization, as well as parameter-wise efficient adaptation for enhancing factual reliability. Retrieval-Augmented Generation (RAG) models and automatic evaluators such as RAGAS \[\] actively mitigate incomplete assertions by directly conditioning explanations on retrieved evidence. Intra-shot and Inter-shot therefore exhibit strong model-dependent sensitivities as well: when comparing between the models, our proprietary LLMs (e.g., GPT-4o) benefit more from retrieval integration, in contrast to open-weight models (e.g., Llama-3. 1–8B) would gain more from in-context learning and adaptive prompting \[,\]. Unified evaluation setup: by incorporating THaMES \[\] in the integrated environment, RAG, ICL and PEFT are benchmarked under a single setting that includes not only standard task scales, but also efficiency measures for reproducibility and cost-aware benchmarks (e.g. Δ(metric)/GPU-hour).

Our work extends the efficiency-normalized evaluation to small language models (SLMs) as well and we quantify Δ(metric) per GPU-hour and across the range of SLMs, and explore how various data-scaling methods impact faithfulness, contextuality, and factuality. Previous evidence shows that retrieval grounding together with domain-specific PEFT significantly decreases unsupported inferences and leaked content, which justifies our empirical analysis dedicated to residual hallucinations and fine-tuning efficacy. At the same time, polished hallucination taxonomies now distinguish error modes at finer granularity: general divisions such as fabrication, unsupported inference, misinterpretation, and low faithfulness are further carved out by domain-specific schemes like the five-type structure used in HalluCode \[\]. Motivated by these frameworks, we create a task-relevant, rule-based taxonomy for small model RAG outputs and validate it with human cross-annotation.

### 2.4. Automatic evaluation using LLM evaluators

One recent direction of research involves the use of large language models as judges — i.e. LLM-as-judge frameworks — for automatically evaluating the quality or factual consistency of model-generated output over a large-scale. First systems, like G-Eval, take inspiration from this paradigm that they try to implement through structured reasoning-based querying and decomposition of thought chains that allow for multi-faceted scoring much closer to humans. Empirical evidence shows that task-dependent and query-related factors have substantial influences on the LLM’s capacity of generating high-quality generated text, with moderate to strong correlations observed between them and human evaluation \[\]. Recent studies and meta-analyses aggregate the work in this space, drawing attention to lingering issues such as systematic evaluator bias (e.g., towards LLM-generated text), prompt sensitivity, calibration drift, and a lack of overarching meta-evaluation protocols that dictate when judges based on an LLM can reliably replace human raters \[,\]. Given these constraints, this work utilizes a hybrid evaluation setup which combines scalable LLM-as-judge testing with rule-based heuristic taxonomy scoring and verification on a curated subset of 154 samples along with human judgments.

### 2.5. RAG Evaluation Frameworks and Metrics

Recently, RAG has been proposed as a principled way to improve the factual grounding of large and small language models. By utilizing external retrieval together with generative reasoning, RAG enhances factual accuracy and reduces neural hallucination, particularly in knowledge-rich domains like legal, clinical and industrial knowledge management \[,,,\]. Nevertheless, quantifying RAG's quality is difficult since its performance derives from a combination of retrieval, reasoning and generation. Ren et al. s analysis of scientific policy interpretation even if retrieval methods can find relevant documents, lack the capability to provide comprehensive decision support for user-oriented policy explanations–highlighting once more that model understanding is still a major bottleneck. However, previous work demonstrates that even a strong RAG pipeline may lead to hallucinations due to the fact retrieval or reasoning is off, supporting taxonomy-guided error analysis and cost-sensitive interventions. Based on these observations, we present a complementary approach to reinforce domain-specific concepts by fine-tuning small language models (SLMs) such that answer grounding and model comprehension are enhanced during RAG’s ultimate synthesis, which provides defense against residual hallucinations. We measure the remaining hallucination types through automatic metrics and empirically verify the proposed fine-tuning method with efficiency-normalized experimentation.

## 3\. Methods

### 3.1. Dataset construction and augmentation

Our goal is not to train a language model from scratch, but to perform domain adaptation on instruction-tuned SLMs using parameter-efficient fine-tuning. Therefore, the learning problem is closer to aligning model behavior with enterprise-specific terminology, evidence usage patterns, and answer style under RAG, rather than learning general language competence. The empirical dataset for this study was obtained from the customer service department of Sakura Company in Taiwan, which utilizes an interactive knowledge management system based on a Retrieval-Augmented Generation (RAG) architecture. A total of 383 customer service RAG query logs and 179 internal regulation RAG query logs were collected from customer service agents, with each record containing the user query, the top two retrieved reference documents, the LLM-generated response, and the corresponding human feedback rating on answer quality. Consistent with previous research emphasizing the critical importance of data reliability in fine-tuning and evaluation \[\], this study selected only items with a RAG generation score of gold-standard.

The gold-standard labels were provided by two senior domain experts with direct operational experience in industrial customer service and two senior domain experts in internal compliance workflows. For the customer service RAG log data, the dataset was split into 229 training samples and 154 testing samples. The internal regulation RAG log data was split into 119 training samples and 60 testing samples. To increase data diversity given the limited real-world samples, this study used the Sakura RAG knowledge base and the GPT-4o model combined with a few-shot data synthesis strategy to generate 200 synthetic RAG samples for customer service and 215 synthetic RAG samples for internal regulation. The synthetic RAG samples were not used directly after generation. All synthetic RAG question–answer pairs were reviewed and, if necessary, corrected by domain experts to ensure validity, coherence, and consistency with retrieved evidence. Only validated synthetic samples were included in the fine-tuning process. Only real-world industrial logs (154 testing samples from customer service and 60 testing samples from internal regulation) were used for evaluation tasks.

### 3.2. Data format and representative example

This study prepares fine-tuning data in JSON format, which consists of a three-part structure: command-input-output (each entry contains command, input, and output fields). Each data entry may also contain metadata fields to indicate the source and process annotations. The following example illustrates this:

,,.

![[1-s2.0-S0920548926000371-gr1.jpg|Fig 1 dummy alt text]]

Download: Download high-res image (655KB)

![[1-s2.0-S0920548926000371-gr2.jpg|Fig 2 dummy alt text]]

Download: Download high-res image (720KB)

Table 1. The experiment models.

| Model | Source |
| --- | --- |
| DeepSeek-R1-Distill-Qwen-1.5B | [https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B) |
| Llama-Breeze2–3B-Instruct | [https://huggingface.co/MediaTek-Research/Llama-Breeze2-3B-Instruct](https://huggingface.co/MediaTek-Research/Llama-Breeze2-3B-Instruct) |
| Llama-3.2–3B-F1-Instruct | [https://huggingface.co/twinkle-ai/Llama-3.2-3B-F1-Instruct](https://huggingface.co/twinkle-ai/Llama-3.2-3B-F1-Instruct) |
| Qwen3–4B | [https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) |
| gemma-3–4b-it | [https://huggingface.co/google/gemma-3-4b-it](https://huggingface.co/google/gemma-3-4b-it) |
| Llama-3-Taiwan-8B-Instruct | [https://huggingface.co/yentinglin/Llama-3-Taiwan-8B-Instruct](https://huggingface.co/yentinglin/Llama-3-Taiwan-8B-Instruct) |

Table 2. System configuration.

| System OS | Ubuntu 20.04.6 LTS, 64-bit OS |
| --- | --- |
| Processor | Intel® Xeon(R) Gold 6242 CPU @ 2.80 GHz × 12 |
| Memory | 64 GB |
| Graphics Card (GPU) | 48GB Nvidia Quadro RTX8000 |

### 3.3. Small language models

Our study assesses a total of 6 unique models. We opt for various sizes for different family models, ranging from 1.5 billion to 8 billion parameters making them suitable for on-premises industrial RAG deployment. We defined small language models, models within the size range 1.5 B to 4B parameters. These models are comparatively smaller, ranging from 17 to 47 times less in parameter count than famous open-sourced large language models, such as Llama-3.3–70B Although Llama-3-Taiwan-8B-Instruct exceeds this strict parameter limit, it is explicitly included in this study as a mid-sized reference baseline. This allows for a comparative analysis between compact SLMs and a larger, more resource-intensive model to contextualize efficiency-quality trade-offs. These models were chosen based on their prevalence in literature and industrial experiment domain. The users primarily expressed themselves in Traditional Chinese. It was demonstrated that all language models selected for preliminary testing could generate responses in Traditional Chinese. We also selected several models that had undergone pre-training on Chinese corpora and were fine-tuned with instructions. The sources of these models are as shown in the table below.

### 3.4. Experimental Settings and system configuration

To examine and compare the generation evaluation of SLMs with fine-tuning, we used four open-source SLMs in our study: DeepSeek-R1-Distill-Qwen-1.5B, Llama-Breeze2–3B-Instruct, Gemma-3–4B-it, Qwen-3–4B, Llama-3.2–3B-F1-Instruct and Llama-3-Taiwan-8B-Instruct. The system configuration for model setup and fine-tuning is as follows:

During the model fine-tuning process, we adopted QLoRA as optimized fine-tuning techniques. Model fine-tuning was performed using the HuggingFace Trainer framework. To assess the robustness of parameter-efficient fine-tuning under low-resource conditions, we conducted a controlled sensitivity analysis on key training hyperparameters while keeping all other settings fixed using gemma3–4b-it. The default configuration used throughout the main experiments was epoch = 2, learning rate = 1e−4, LoRA rank *r* = 8, and batch size = 8. Starting from this baseline, we varied one hyperparameter at a time to isolate its effect: (i) epochs ∈ {1, 2, 4, 8}, (ii) learning rate ∈ {1e−4, 1e−5, 1e−6}, (iii) LoRA rank r ∈ {4, 8, 16, 32, 64}, and (iv) batch size ∈ {2, 4, 8, 16, 32}. This design avoids exhaustive grid search while enabling systematic examination of training stability and performance trends. The sensitivity results indicate that although certain metrics, such as factual correctness, are moderately influenced by specific hyperparameters, the overall performance trends and cross-model comparisons remain stable across a broad range of reasonable configurations. Based on this analysis, the baseline setting is adopted for all experiments to ensure a balanced trade-off between generation quality, training stability, and computational efficiency. Detailed sensitivity results are reported in.

Table 3. Fine-tuning configuration and hyperparameter selection.

| lora\_rank | epoch | batch | learning rate | train/train runtime(min) | Fal | AR | Fac |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4 | 2 | 8 | 0.0001 | 27.288 | 0.973 | 0.832 | 0.750 |
| 16 | 2 | 8 | 0.0001 | 27.646 | 0.961 | 0.818 | 0.777 |
| 32 | 2 | 8 | 0.0001 | 28.037 | 0.969 | 0.830 | 0.801 |
| 64 | 2 | 8 | 0.0001 | 28.431 | 0.966 | 0.825 | 0.806 |
| 8 | 1 | 8 | 0.0001 | 13.681 | 0.978 | 0.841 | 0.735 |
| 8 | 4 | 8 | 0.0001 | 54.712 | 0.954 | 0.812 | 0.800 |
| 8 | 8 | 8 | 0.0001 | 109.434 | 0.877 | 0.818 | 0.817 |
| 8 | 2 | 2 | 0.0001 | 27.427 | 0.941 | 0.803 | 0.780 |
| 8 | 2 | 4 | 0.0001 | 27.386 | 0.957 | 0.820 | 0.784 |
| 8 | 2 | 16 | 0.0001 | 27.357 | 0.973 | 0.836 | 0.736 |
| 8 | 2 | 32 | 0.0001 | 27.345 | 0.963 | 0.828 | 0.716 |
| **8** | **2** | **8** | **0.0001** | **27.366** | **0.964** | **0.837** | **0.761** |
| 8 | 2 | 8 | 0.00001 | 27.355 | 0.954 | 0.849 | 0.640 |
| 8 | 2 | 8 | 0.000001 | 27.365 | 0.895 | 0.899 | 0.509 |

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness.

### 3.5. RAG Baseline configuration

The fine-tuned models were evaluated using 154 examples from customer service tests and 60 examples from internal regulatory tests for answer generation. The evaluation focused exclusively on generation performance. The same RAG prompt configuration was applied to the GPT-4o-mini baseline, which was evaluated in a zero-shot retrieval-augmented generation (RAG) setting. To ensure a controlled and fair comparison, the same retriever, the same top-2 retrieved documents, and the same RAG prompt template were used for both GPT-4o-mini and all SLMs. No few-shot demonstrations or task-specific fine-tuning were applied to GPT-4o-mini. All decoding parameters were fixed across runs. This configuration isolates the effect of parameter-efficient fine-tuning in SLMs from differences arising from prompting or retrieval strategies. The SLM generation prompt was defined as follows:

### 3.6. Data-scaling protocol

We experimented with varying data sizes, fine-tuning the model using 50, 100, 150, 200, 300, and 429 examples for the customer service dataset, and using 50, 100, 150, 200, and 334 examples for the internal regulation dataset. For the customer service dataset, training subsets of 50, 100, 150, and 200 samples were constructed exclusively from real-world annotated log data. For the internal regulation dataset, all available real-world annotations (119 samples) were used for the smaller training sizes (50, 100) before any synthetic augmentation was introduced. Synthetic RAG question–answer pairs were incorporated only when larger training sizes were required and the real annotations had been fully utilized in both datasets. Each fine-tuning iteration used identical hyperparameter settings and prompt configurations to ensure consistency across datasets and training scales. This design allows the study to examine performance trends and saturation behavior under low-resource domain adaptation, rather than to optimize absolute performance through large-scale supervision.

### 3.7. Evaluation Metrics of generation quality

Based on the research of Es et al. \[\], we use the RAGAS metrics to evaluate the generation quality of fine-tuned SLMs, including faithfulness, answer relevance, factual correctness, and F1 score. Generation quality refers to the effectiveness of the content produced by the generative model. To ensure consistency and fairness in the evaluation, all metrics are evaluated using GPT-4o as the reviewer, with automatic scoring and comparison performed according to the standardized RAGAS prompts. A description of each metric is as follows:

**Faithfulness.** It is described as the proportion of an LLM output to reference data or to a benchmark set. This dimension pertains to the need for model outputs not to be misguided on exaggerated, slanted, or uninformed assertions so that they are true-oriented. It is calculated like this:$Faithfulness=NumberofclaimsthatcanbeinferredfromgivencontextTotalnumberofclaimsinthegeneratedanswer$

**Answer Relevance.** The relevance measures are applied to measure the overlap of outputs and user provided input. Higher scores represent a closer correspondence between the responses and user intended meaning, while lower scores are assigned when answers miss crucial information or fail to accurately address the question at issue, or provide irrelevant content. It can be calculated:$AnswerRelevance=1N∑i=1Ncosinesimility(Egi,Eo)$ where *Eg <sub>i</sub>* is the embedding of the generated question *i, Eo* is the embedding of the original question, *N* is the number of generated questions.

**Factual Correctness.** Used to compare and assess the factual accuracy of generated responses against reference material. This metric determines how closely the generated response matches the reference material. Factual accuracy scores range from 0 to 1, with higher values indicating better performance. The formula for calculating True Positive (TP), False Positive (FP), and False Negative (FN) are as follows:

True Positive (TP)=Number of claims in the response that are also present in the reference.

False Positive (FP)=Number of claims in the response that are not present in the reference.

False Negative (FN)=Number of claims in the reference that are not present in the response.$Precision=TPTP+FP,Recall=TPTP+FN,F1Score=2×Precision×RecallPrecision+Recall$

**F1 Score.** This metric measures the average overlap between the predicted answer and the actual answer \[\]. Both the prediction and the ground truth are treated as bags of tokens, and their F1 score is calculated. For each question, the maximum F1 score among all ground truth answers is selected, and these scores are then averaged over all questions.

### 3.8. Cost-efficiency measure

For each model and evaluation metric—Faithfulness, Answer Relevancy, Factual Correctness, and F1—we quantified the marginal performance gain per unit of compute by comparing adjacent training data volumes. For a pair of experiments, A (smaller training size) and B (larger training size), we define cost-efficiency as follows:$ΔmetrixGPU−hour=metricB−metricAGPUhourB−GPUhourA$

Where A and B represent adjacent training data volume settings (e.g., from 100 to 150 samples). The metric refers to the quantitative measure being evaluated, while GPU-hours are derived by converting the wall-clock runtime (in minutes) recorded in the training log to hours (minutes ÷ 60). To estimate uncertainty, we apply a non-parametric bootstrap at the pair level (using 500 resamples) by resampling with replacement within groups A and B, computing the pairwise Δ(metric)/GPU-hour for each resample, and reporting the bootstrap mean along with the 95% percentile interval.

### 3.9. The taxonomy of hallucination

We proposed a heuristic framework for detecting the taxonomy of hallucination based on Huang et al. \[\], Ji et al. \[\], and Liu et al. \[\]. The goal is to enable the RAG system to automatically determine which type of error may have occurred based on the three quantitative evaluation scores generated by the model output, without relying on human labeling. The framework assigns hallucination-type labels to model outputs using three standardized automated metrics: faithfulness, factual correctness, and answer relevance. shows that a total of five taxonomy labels were identified, including Fabrication/Invented fact, Unsupported inference/Over-generalization, Misinterpretation/Low relevance, Suspected hallucination, and Low faithfulness.

Table 4. Heuristic annotation rules for automated taxonomy labeling.

| Code | Taxonomy label | Trigger condition | Interpretation/Rationale |
| --- | --- | --- | --- |
| FAB | Fabrication/Invented fact | factual ≤ 0.20 and faith ≥ 0.80 | Highly consistent with retrieved evidence but factually incorrect; indicates confident hallucination or fabricated statement. |
| UNSUP | Unsupported inference/Over-generalization | 0.20 < factual < 0.60 and faith < 0.80 | Contains partially correct content but extends beyond evidence or makes over-generalized claims. |
| MIS | Misinterpretation/Low relevance | relev ≤ 0.60 | Response misreads the prompt or diverges semantically from the user query; low topical alignment. |
| SUS | Suspected hallucination | factual ≤ 0.30 | Ensures coverage of low factual cases not captured by other rules; possible hallucination. |
| LF | Low faithfulness | faith ≤ 0.50 | Output loosely connected to retrieved context; potential misuse or misinterpretation of evidence. |

*factual* = factual correctness; *faith* = faithfulness; *relev* = answer relevancy.

## 4\. Results

### 4.1. Overall model performance

The evaluation models cover a wide range of architectural scales and design requirements, from compact, distilled models (1.5B) to region-specific instruction models (8B). These models will allow the study to examine the trade-off between efficiency and quality. For reference, GPT-4o-mini was evaluated as a baseline under the same zero-shot retrieval-augmented generation (RAG) configuration, using identical retrievers, top-2 retrieved documents, and prompt templates, without task-specific fine-tuning.

presents the comparative performance of all evaluated SLMs for customer service RAG logs across four primary metrics—faithfulness, answer relevance, factual correctness, and F1 score—using the held-out enterprise test set. Averaged across architectures and data-scaling configurations, the mean scores were as follows: faithfulness = 0.937, answer relevance = 0.847, factual correctness = 0.668, and F1 = 0.653. The best-performing models for each metric are: Qwen3–4B, which achieved the highest faithfulness (0.973), indicating superior grounding to retrieved evidence; Llama-3.2–3B-F1, which attained the best answer relevance (0.904), reflecting effective contextual alignment; and Llama-Breeze2–3B, which outperformed others in both factual correctness (0.776) and overall F1 score (0.765). These findings suggest that the evaluated SLMs exhibit complementary performance profiles rather than a single dominant architecture. Specifically, Qwen excels in evidence-grounded generation, Llama-3.2 variants prioritize contextual relevance, and Breeze2 demonstrates stronger factual correctness and end-task balance—highlighting the trade-offs inherent in optimizing multi-objective RAG reasoning tasks.

Tabel 5. Comparison of overall model performance for customer service RAG logs.

<table><thead><tr><th>Model</th><th>Training size</th><th>Fal</th><th>AR</th><th>Fac</th><th>F1</th></tr></thead><tbody><tr><td rowspan="7">MediaTek-Research/Llama-Breeze2–3B-Instruct</td><td>No Finetuned</td><td>0.856</td><td>0.856</td><td>0.454</td><td>0.481</td></tr><tr><td>50</td><td>0.9</td><td>0.897</td><td>0.529</td><td>0.559</td></tr><tr><td>100</td><td>0.901</td><td>0.852</td><td>0.643</td><td>0.647</td></tr><tr><td>150</td><td>0.933</td><td>0.872</td><td>0.698</td><td>0.707</td></tr><tr><td>200</td><td>0.954</td><td>0.82</td><td>0.735</td><td>0.723</td></tr><tr><td>300</td><td>0.94</td><td>0.824</td><td>0.757</td><td>0.727</td></tr><tr><td>429</td><td>0.968</td><td>0.82</td><td>0.776</td><td>0.765</td></tr><tr><td rowspan="7">Google/gemma–3–4b-it</td><td>No Finetuned</td><td>0.902</td><td>0.886</td><td>0.525</td><td>0.499</td></tr><tr><td>50</td><td>0.954</td><td>0.849</td><td>0.599</td><td>0.562</td></tr><tr><td>100</td><td>0.962</td><td>0.823</td><td>0.719</td><td>0.649</td></tr><tr><td>150</td><td>0.962</td><td>0.833</td><td>0.699</td><td>0.668</td></tr><tr><td>200</td><td>0.945</td><td>0.824</td><td>0.725</td><td>0.69</td></tr><tr><td>300</td><td>0.948</td><td>0.806</td><td>0.72</td><td>0.69</td></tr><tr><td>429</td><td>0.968</td><td>0.837</td><td>0.76</td><td>0.729</td></tr><tr><td rowspan="7">Qwen/Qwen3–4B</td><td>No Finetuned</td><td>0.886</td><td>0.897</td><td>0.537</td><td>0.5</td></tr><tr><td>50</td><td>0.919</td><td>0.896</td><td>0.54</td><td>0.548</td></tr><tr><td>100</td><td>0.93</td><td>0.824</td><td>0.677</td><td>0.627</td></tr><tr><td>150</td><td>0.968</td><td>0.839</td><td>0.674</td><td>0.659</td></tr><tr><td>200</td><td>0.962</td><td>0.822</td><td>0.719</td><td>0.691</td></tr><tr><td>300</td><td>0.973</td><td>0.84</td><td>0.721</td><td>0.701</td></tr><tr><td>429</td><td>0.96</td><td>0.83</td><td>0.731</td><td>0.709</td></tr><tr><td rowspan="7">twinkle-ai/Llama-3.2–3B-F1-Instruct</td><td>No Finetuned</td><td>0.810</td><td>0.855</td><td>0.470</td><td>0.42</td></tr><tr><td>50</td><td>0.849</td><td>0.904</td><td>0.512</td><td>0.491</td></tr><tr><td>100</td><td>0.887</td><td>0.879</td><td>0.545</td><td>0.572</td></tr><tr><td>150</td><td>0.904</td><td>0.878</td><td>0.55</td><td>0.581</td></tr><tr><td>200</td><td>0.923</td><td>0.85</td><td>0.63</td><td>0.627</td></tr><tr><td>300</td><td>0.942</td><td>0.857</td><td>0.662</td><td>0.66</td></tr><tr><td>429</td><td>0.947</td><td>0.858</td><td>0.721</td><td>0.686</td></tr><tr><td rowspan="7">deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B</td><td>No Finetuned</td><td>0.606</td><td>0.808</td><td>0.320</td><td>0.226</td></tr><tr><td>50</td><td>0.693</td><td>0.885</td><td>0.406</td><td>0.316</td></tr><tr><td>100</td><td>0.766</td><td>0.866</td><td>0.480</td><td>0.406</td></tr><tr><td>150</td><td>0.856</td><td>0.835</td><td>0.622</td><td>0.537</td></tr><tr><td>200</td><td>0.813</td><td>0.843</td><td>0.599</td><td>0.573</td></tr><tr><td>300</td><td>0.853</td><td>0.836</td><td>0.653</td><td>0.614</td></tr><tr><td>429</td><td>0.884</td><td>0.839</td><td>0.710</td><td>0.657</td></tr><tr><td rowspan="7">yentinglin/Llama-3-Taiwan-8B-Instruct</td><td>No Finetuned</td><td>0.891</td><td>0.892</td><td>0.563</td><td>0.542</td></tr><tr><td>50</td><td>0.948</td><td>0.860</td><td>0.659</td><td>0.636</td></tr><tr><td>100</td><td>0.925</td><td>0.846</td><td>0.661</td><td>0.622</td></tr><tr><td>150</td><td>0.940</td><td>0.823</td><td>0.695</td><td>0.639</td></tr><tr><td>200</td><td>0.946</td><td>0.821</td><td>0.738</td><td>0.702</td></tr><tr><td>300</td><td>0.949</td><td>0.809</td><td>0.786</td><td>0.731</td></tr><tr><td>429</td><td>0.945</td><td>0.820</td><td>0.760</td><td>0.740</td></tr><tr><td>Means of Fine-Tuned SLMs</td><td></td><td>0.917</td><td>0.845</td><td>0.661</td><td>0.634</td></tr><tr><td>gpt-4o-mini</td><td></td><td>0.91</td><td>0.895</td><td>0.586</td><td>0.531</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

The performance comparison of all SLMs assessed on the internal regulation RAG logs across four primary metrics is shown in. The average performance of fine-tuned SLMs on these metrics is 0.865 for faithfulness, 0.895 for answer relevance, 0.488 for factual correctness, and 0.533 for F1 score, respectively. These performance values are expected given the increased difficulty levels and stricter evidence sourcing demands required by regulation-oriented questions as compared to customer service questions. On each individual metric, models display disparate merits as compared to a single overall preference to any given architecture. Qwen3–4B reports the highest value on the faithfulness metric (0.947), corroborating high evidence groundedness and appropriateness to the searched-for regulation texts. Llama-3-Taiwan-8B-Instruct reports the highest value on the answer relevance metric (0.935), establishing supremacy over others regarding question-targeted appropriateness to formal policy questions. However, Qwen3–4B and Llama-Breeze2–3B-Instruct demonstrate competitive performance on factual correctness, with highest values reported as 0.576 and 0.530, respectively, and Qwen3–4B reports the highest value on overall F1 score with 0.622.

Tabel 6. Comparison of Overall model performance for internal regulations RAG logs.

<table><thead><tr><th>Model</th><th>Training size</th><th>Fal</th><th>AR</th><th>Fac</th><th>F1</th></tr></thead><tbody><tr><td rowspan="6">MediaTek-Research/Llama-Breeze2–3B-Instruct</td><td>No Finetuned</td><td>0.878</td><td>0.691</td><td>0.425</td><td>0.402</td></tr><tr><td>50</td><td>0.889</td><td>0.879</td><td>0.555</td><td>0.499</td></tr><tr><td>100</td><td>0.920</td><td>0.939</td><td>0.512</td><td>0.553</td></tr><tr><td>150</td><td>0.905</td><td>0.920</td><td>0.544</td><td>0.537</td></tr><tr><td>200</td><td>0.883</td><td>0.884</td><td>0.555</td><td>0.573</td></tr><tr><td>334</td><td>0.916</td><td>0.933</td><td>0.554</td><td>0.570</td></tr><tr><td rowspan="6">Google/gemma–3–4b-it</td><td>No Finetuned</td><td>0.936</td><td>0.897</td><td>0.504</td><td>0.543</td></tr><tr><td>50</td><td>0.854</td><td>0.882</td><td>0.462</td><td>0.466</td></tr><tr><td>100</td><td>0.922</td><td>0.922</td><td>0.542</td><td>0.569</td></tr><tr><td>150</td><td>0.913</td><td>0.926</td><td>0.521</td><td>0.578</td></tr><tr><td>200</td><td>0.895</td><td>0.927</td><td>0.519</td><td>0.564</td></tr><tr><td>334</td><td>0.930</td><td>0.930</td><td>0.568</td><td>0.594</td></tr><tr><td rowspan="6">Qwen/Qwen3–4B</td><td>No Finetuned</td><td>0.917</td><td>0.865</td><td>0.524</td><td>0.562</td></tr><tr><td>50</td><td>0.940</td><td>0.908</td><td>0.561</td><td>0.595</td></tr><tr><td>100</td><td>0.934</td><td>0.921</td><td>0.535</td><td>0.537</td></tr><tr><td>150</td><td>0.935</td><td>0.921</td><td>0.566</td><td>0.612</td></tr><tr><td>200</td><td>0.943</td><td>0.920</td><td>0.548</td><td>0.611</td></tr><tr><td>334</td><td>0.932</td><td>0.938</td><td>0.557</td><td>0.622</td></tr><tr><td rowspan="6">twinkle-ai/Llama-3.2–3B-F1-Instruct</td><td>No Finetuned</td><td>0.829</td><td>0.889</td><td>0.367</td><td>0.402</td></tr><tr><td>50</td><td>0.831</td><td>0.909</td><td>0.425</td><td>0.499</td></tr><tr><td>100</td><td>0.858</td><td>0.917</td><td>0.519</td><td>0.553</td></tr><tr><td>150</td><td>0.871</td><td>0.920</td><td>0.460</td><td>0.537</td></tr><tr><td>200</td><td>0.869</td><td>0.906</td><td>0.495</td><td>0.573</td></tr><tr><td>334</td><td>0.864</td><td>0.937</td><td>0.529</td><td>0.570</td></tr><tr><td rowspan="6">deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B</td><td>No Finetuned</td><td>0.580</td><td>0.729</td><td>0.240</td><td>0.258</td></tr><tr><td>50</td><td>0.608</td><td>0.804</td><td>0.310</td><td>0.280</td></tr><tr><td>100</td><td>0.724</td><td>0.871</td><td>0.271</td><td>0.255</td></tr><tr><td>150</td><td>0.747</td><td>0.915</td><td>0.289</td><td>0.332</td></tr><tr><td>200</td><td>0.738</td><td>0.899</td><td>0.289</td><td>0.335</td></tr><tr><td>334</td><td>0.794</td><td>0.922</td><td>0.323</td><td>0.419</td></tr><tr><td rowspan="6">yentinglin/Llama-3-Taiwan-8B-Instruct</td><td>No Finetuned</td><td>0.898</td><td>0.912</td><td>0.486</td><td>0.531</td></tr><tr><td>50</td><td>0.926</td><td>0.908</td><td>0.544</td><td>0.582</td></tr><tr><td>100</td><td>0.916</td><td>0.933</td><td>0.537</td><td>0.596</td></tr><tr><td>150</td><td>0.918</td><td>0.935</td><td>0.554</td><td>0.592</td></tr><tr><td>200</td><td>0.914</td><td>0.930</td><td>0.550</td><td>0.617</td></tr><tr><td>334</td><td>0.932</td><td>0.930</td><td>0.530</td><td>0.620</td></tr><tr><td>Means of Fine-Tuned SLMs</td><td></td><td>0.865</td><td>0.895</td><td>0.488</td><td>0.533</td></tr><tr><td>gpt-4o-mini</td><td></td><td>0.918</td><td>0.881</td><td>0.578</td><td>0.554</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

The larger Llama-3-Taiwan-8B-Instruct model shows consistent and robust performance across all metrics but is not necessarily better than smaller SLM models in general, especially in regard to factual accuracy. At the same time, the DeepSeek-R1-Distill-Qwen-1.5B model, which has fewer parameters but otherwise shows consistent improvement in regard to the trained sample size, is still less advanced in regard to factual accuracy. These patterns confirm that smaller SLM models are still complementary in regard to regulation-oriented retrieval and generative tasks. In summary, optimization of models for evidence grounding, contextuality, and factuality of models targets different aspects of regulation-oriented reasoning in their own right and illustrates that optimization for multiple criteria faces underlying challenges when models are applied in low-resource settings concerning regulation.

### 4.2. Learning curves: metric vs train size

The mean learning curves of SLMs across four evaluation metrics for RAG tasks are illustrated in as a function of training set size. For the customer service dataset (), faithfulness increases steadily from approximately 0.88 to 0.96 as training size grows from 50 to 429 samples, indicating improved alignment between generated responses and retrieved evidence. In contrast, answer relevance decreases from around 0.90 to approximately 0.82, reflecting a shift from semantically expansive responses toward more evidence-constrained and conservative generation behavior as fine-tuning reinforces reliance on retrieved documents. Factual correctness exhibits a consistent upward trend, rising from 0.57 to 0.75, while overall generation quality, measured by F1 score, improves from 0.52 to 0.73 with increasing training data.

![[1-s2.0-S0920548926000371-gr3.jpg|Fig 3 dummy alt text]]

Download: Download high-res image (421KB)

Moreover, there is a similar learning curve for the internal regulation question dataset (). The results showed a simultaneous increase in faithfulness, factual correctness, and F1 score. However, once a certain level of training is reached, there is a tendency towards saturation of the curves. The absolute improvement measures are not as drastic as the internal regulation dataset, compared to those in the customer service field. There is a plateau in the relevance of responses, and it does not change much with more training.

In case of customer service data, sets of 229 labeled samples maximum were created solely based on actual-world RAG logs. Their respective learning curves show greater rates of improvement in factual correctness as well as F1 score, especially between 50 and 200 samples before leveling off. These trends imply that domain-related data of small quantities is adequate to significantly improve end-task performance on conversational RAG tasks. In contrast, the internal regulation dataset demonstrates more conservative absolute gains and wider variability bands, especially for factual correctness and F1. This is expected given the smaller dataset size and the more formal, document-centric nature of regulation queries, which require stricter evidence alignment and longer-context reasoning. Nevertheless, the directionality of improvement remains consistent, with no evidence of performance degradation as training size increases.

### 4.3. Δ(metric)/GPU-hour analysis

The marginal improvement in each quality metric per GPU-hour (Δ(metric)/GPU-hour) is reported in and for the cost-efficiency analysis among two different datasets. Marginal gains were estimated in each incremental step of training size over four important dimensions: faithfulness, relevance, factual correctness, and F1 score. Activation patterns are found to have varied efficiency profiles among model structures. In the customer service dataset (), the gemma-3–4b-it model exhibits a similarly balanced cost-effectiveness, with +0.317 factual correctness and +0.309 F1 per GPU-hour, mild gains in answer relevance (+0.246) and faithfulness (+0.159). The Llama-3.2–3B-F1-Instruct shows the largest marginal gain in factual correctness (+0.488 per GPU-hour) and a decent increase in F1 (+0.215), with marginal improvements on faithfulness (+0.041) and relevance (+0.008). Llama-Breeze2–3B-Instruct, on the other hand, compares favourably only in terms of efficiency for F1 (+0.300) and faithfulness (+0.221), with a drop in relevance (−0.032), corresponding to a precision-context tradeoff aspect. In contrast, Qwen-3–4B has near-zero or negative marginal efficiency in most of the metrics (F1 +0.049, factual correctness +0.062, faithfulness −0.080, relevance −0.062), stressing there are diminishing returns under our fine-tuning setting currently. Additionally, we further examined the larger and smaller model parameter size (Llama-3-Taiwan-8B-Instruct and DeepSeek-R1-Distill-Qwen-1.5B). The DeepSeek-R1-Distill-Qwen-1.5B model demonstrates relatively strong cost-efficiency despite its smaller model size. It achieves marginal gains of approximately +0.300 in F1 score and +0.305 in factual correctness per GPU-hour, along with moderate improvements in faithfulness (+0.167) and answer relevance (+0.048). The Llama-3-Taiwan-8B-Instruct model shows limited marginal gains across all evaluated metrics, with small positive improvements in F1 score (+0.115), factual correctness (+0.078), faithfulness (+0.038), and answer relevance (+0.014).

![[1-s2.0-S0920548926000371-gr4.jpg|Fig 4 dummy alt text]]

Download: Download high-res image (601KB)

Table 7. Δ(metric)/GPU-hour summary for each model and metric.

<table><thead><tr><th>Dataset</th><th>Model</th><th>F1</th><th>Fac</th><th>Fail</th><th>AR</th></tr></thead><tbody><tr><td rowspan="6">Customer service logs</td><td>Llama-3-Taiwan-8B-Instruct</td><td>0.117</td><td>0.079</td><td>0.039</td><td>0.015</td></tr><tr><td>Llama-3.2–3B-F1-Instruct</td><td>0.215</td><td>0.488</td><td>0.041</td><td>0.008</td></tr><tr><td>Llama-Breeze2–3B-Instruct</td><td>0.300</td><td>0.150</td><td>0.221</td><td>-0.032</td></tr><tr><td>Qwen3–4B</td><td>0.049</td><td>0.062</td><td>-0.080</td><td>-0.062</td></tr><tr><td>gemma–3–4b-it</td><td>0.309</td><td>0.317</td><td>0.159</td><td>0.246</td></tr><tr><td>DeepSeek-R1-Distill-Qwen-1.5B</td><td>0.299</td><td>0.306</td><td>0.167</td><td>0.049</td></tr><tr><td rowspan="6">Internal Regulations logs</td><td>Llama-3-Taiwan-8B-Instruct</td><td>0.076</td><td>-0.003</td><td>-0.01</td><td>0.045</td></tr><tr><td>Llama-3.2–3B-F1-Instruct</td><td>0.081</td><td>0.23</td><td>-0.033</td><td>0.21</td></tr><tr><td>Llama-Breeze2–3B-Instruct</td><td>0.018</td><td>-0.006</td><td>0.197</td><td>0.293</td></tr><tr><td>Qwen3–4B</td><td>0.053</td><td>0.044</td><td>-0.053</td><td>0.088</td></tr><tr><td>gemma–3–4b-it</td><td>0.170</td><td>0.272</td><td>0.198</td><td>0.017</td></tr><tr><td>DeepSeek-R1-Distill-Qwen-1.5B</td><td>0.534</td><td>0.216</td><td>0.356</td><td>0.146</td></tr></tbody></table>

*Note.* Fal: faithfulness; AR: answer relevance; Fac: factual correctness; F1: F1 score.

In the internal regulation dataset (), a markedly different cost-efficiency pattern is observed. The DeepSeek-R1-Distill-Qwen-1.5B model again has the strongest marginal improvement profile, showing the strongest F1Score improvement (roughly +0.53 every GPU hour) and concurrent strong improvements in faithfulness and answer relevance. Although this model has only small sized parameters, it is still the most cost-efficient in the regulatory environment where rigid adherence to rigorously formatted and legally bound source texts is required. Conversely, for several larger-parameter models, notable trade-offs between answer relevance and faithfulness are observed in the internal regulation setting. In particular, the Llama-3.2–3B-F1-Instruct model exhibits a positive marginal improvement in answer relevance (+0.21) while simultaneously showing a reduction in faithfulness (−0.033), suggesting an increased tendency to generate contextually appropriate responses that are progressively less anchored to the retrieved regulatory evidence. Analogously, the gemma-3–4b-it model demonstrates positive marginal improvements in factual correctness (+0.272); however, this gain is accompanied by only minimal improvement in answer relevance (+0.017), indicating that increases in factual precision do not necessarily translate into stronger question–document alignment in the regulatory context.

Consistent with observations from the customer service dataset, Qwen-3–4B shows near-zero or negative marginal gains in faithfulness (−0.053). The overall implication of these findings is that, in high-stakes regulatory scenarios, improvements in surface-level appropriateness or factual accuracy may occur alongside a deterioration in source adherence, underscoring the importance of cost-normalized evaluation when selecting models for compliance-oriented RAG applications.

### 4.4. Error analysis (hallucination taxonomy)

Building on the finetuning results for factual accuracy and F1 performance, we conducted a taxonomy-based analysis of hallucination patterns using the MediaTek-Research/Llama-Breeze2–3B-Instruct model in customer service log dataset. To assess the impact of domain-specific fine-tuning, we compared the heuristic taxonomy distributions of the fine-tuned and unfine-tuned models under identical evaluation conditions.

As illustrated in a, hallucinations were prevalent prior to adaptation. Among the 154 responses generated by the unfine-tuned model, only 90 (58.4%) were labeled as No major issue (OK), while the remaining 64 cases exhibited various error types: Fabrication (FAB, 28), Suspected hallucination (SUS, 17), Misinterpretation or Low relevance (MIS, 8), Unsupported inference (UNSUP, 7), and Low faithfulness (LF, 1). According to the results of domain-specific fine-tuning on industrial customer service RAG logs, we found that the hallucination rate decreased significantly. 84.4% (130/154) no major issues (OK) were reported, with the remaining outputs categorized as FAB (12), MIS (4), SUS (4), LF (1), FAB + MIS (1), UNSUP + MIS (1), and UNSUP (1), indicating strong alignment between automated and human evaluations of factual adequacy.

![[1-s2.0-S0920548926000371-gr5a.jpg|Fig 5 dummy alt text]]

Download: Download high-res image (165KB)

A comparison between -a and -b shows a 26-point rise in outputs, accompanied by no major issues, and a significant decrease in instances of fabrication and unsupported inferences. These findings provide empirical evidence that fine-tuning with domain-specific RAG data significantly reduces hallucinations, improving factual correctness and alignment with evidence in industrial knowledge retrieval applications.

In the internal regulation dataset, we observed a slight improvement after model fine-tuning. A total of six additional items were labeled as No major issue (OK), with the remaining outputs categorized as UNSUP (7), FAB (6), and SUS (1). Overall, despite the limitations imposed by the small sample size, a marginal improvement in the fine-tuned model's RAG answer generation can still be observed ().

![[1-s2.0-S0920548926000371-gr6a.jpg|Fig 6 dummy alt text]]

Download: Download high-res image (150KB)

## 5\. Discussion

### 5.1. Interpretation of findings

The present study investigated the factual reliability, computational efficiency, and stability of SLMs when adopting domain-specific fine-tuning for the RAG models. This is based on the same zero-shot RAG setup because the fine-tuned SLMs had comparable performance with respect to faithfulness and factual accuracy to GPT-4o-mini and showed a substantial improvement over their non-fine-tuned models for the same datasets. These findings align with prior studies showing that SLMs can reach LLM-comparable accuracy when adapted through domain-specific fine-tuning (\[\]; Kwon et al., 2025; \[\]).

In addition, the results of learning curve analysis showed that the greatest performance improvements occurred between 50 and 200 annotated cases for the customer service data, beyond which performance gains became marginal. For the internal regulation dataset, a similar saturation pattern was observed at a smaller scale, with performance stabilizing once the training size reached approximately 100 real-world annotated samples. Faithfulness had a monotonically increasing trend, while the relevance of the answers had a non-monotonic trend, first reducing and then settling on averages ranging between 0.83 and 0.84. This trend reveals an increasing trend toward being more conservative in extraction as the accuracy of facts and evidential support is steadily incremented via fine-tuning. This observation is consistent with the findings of Lin et al. \[\], which indicate that factuality-aware alignment approaches not only guide language models to produce more precise and reliable responses but also reduce the likelihood of generating unsupported or false claims.

There were evident trade-offs between efficiency and quality of response in each model architecture through the Δ(metric)/GPU-hour analysis. On the customer service task, gemma-3–4B-it was the model with the largest marginal improvement in factual accuracy (+0.317) and F1 score (+0.309), trailed closely by Llama-Breeze2–3B-Instruct, which was efficient in F1 (+0.300) and Faithfulness (+0.221). Conversely, on the internal regulation task, DeepSeek-R1-Distill-Qwen-1.5B was the model with the highest cost efficiency, as it achieved the largest marginal improvement in F1 score of +0.534 per GPU-hour along with large gains in both Faithfulness (+0.356) and Answer Relevance (+0.146). On both tasks, the marginal returns on each increase in model scale were diminishing in nature, so as to support the observations made in the studies of Tian et al. \[\] & Yuan et al. \[\] on the early saturation in performance gains through excessive supervision.

Moreover, an analysis of the hallucination types between the original and the fine-tuned SLMs through a hallucination analysis showed a dramatic decrease in the errors of generation after the domain-specific fine-tuning. In the customer service corpus, the “No major issue” category increased from 58.4% to 84.4%, while in the internal regulation corpus, although the results were limited by the small sample size, there was a reduction in the number of fabrications and unsupported inferences with a considerable number of additional outputs qualified as having no major issues after performing the domain-specific fine-tuning. These findings are in line with an existing body of research which has established the efficacy of domain-specific fine-tuning in diminishing hallucinations and boosting factual alignment in various industrial tasks \[,,\].

Overall, the results affirm that small, domain-adapted models, when fine-tuned with factuality-aware objectives, can attain LLM-comparable factual reliability at a fraction of the computational cost. Nevertheless, the observed performance saturation and semantic narrowing highlight the importance of balanced optimization. Future research should pursue hybrid alignment strategies that preserve expressive diversity while consolidating factual accuracy and evidential grounding \[,\].

### 5.2. Limitation

While our findings demonstrate that fine-tuned SLMs can rival GPT-4o-mini and significantly reduce the answer generation of hallucination in using RAG pipeline, several limitations warrant consideration. The impact of different dataset sizes and hallucination taxonomy analysis on fine-tuning language models in specific domains still requires extensive verification. Despite the encouraging results of this experiment, there are some limitations to its size that must be considered when evaluating real-world data. While absolute performance may vary with larger datasets, the observed relative trends – such as early performance saturation and trade-offs between factuality, relevance, and efficiency – remain informative for low-resource industrial RAG scenarios. Therefore, any generalization about other enterprise settings may not be applicable. The application of this experiment to real-world settings of increasing size is a high-priority area for future exploration. This study mainly provides companies with a reference for feasible solutions for fine-tuning language models through the analysis of empirical data. These limitations frame, rather than undermine, the contribution and point to clear steps for broader verification.

## 6\. Conclusion

In conclusion, this study shows that retrieval-augmented SLMs still have residual hallucination behaviors even in evidence-aware configurations, particularly in terms of the indicators of factual correctness and F1 score performance. However, the results of domain-specific fine-tuning demonstrate that it could reduce the hallucinations of answer generation, thus enhancing both indicators. Moreover, we examined the marginal improvement values per GPU-hour across each quality metric, estimating the marginal gains at each incremental stage of training scale for four key dimensions: fidelity, relevance, factual accuracy, and F1 score. Finally, we proposed a practical heuristic hallucination taxonomy framework that could detect the error pattern of answer generation quality in RAG systems. Future work could extend this research by scaling taxonomy validation in different domains and integrate the automated detectors with RAG systems.

## Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this work the author(s) used ChatGPT and Wordvice AI in order to writing assistance. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article.

## CRediT authorship contribution statement

**Kai-Chih Pai:** Writing – review & editing, Writing – original draft, Supervision, Project administration, Formal analysis, Data curation, Conceptualization. **Wen-Chuan Hsu:** Methodology, Formal analysis.

[^2]: We proposed a heuristic framework for detecting the taxonomy of hallucination based on Huang et al. \[\], Ji et al. \[\], and Liu et al. \[\]. The goal is to enable the RAG system to automatically determine which type of error may have occurred based on the three quantitative evaluation scores generated by the model output, without relying on human labeling. The framework assigns hallucination-type labels to model outputs using three standardized automated metrics: faithfulness, factual correctness, and answer relevance. shows that a total of five taxonomy labels were identified, including Fabrication/Invented fact, Unsupported inference/Over-generalization, Misinterpretation/Low relevance, Suspected hallucination, and Low faithfulness.

Table 4. Heuristic annotation rules for automated taxonomy labeling.

| Code | Taxonomy label | Trigger condition | Interpretation/Rationale |
| --- | --- | --- | --- |
| FAB | Fabrication/Invented fact | factual ≤ 0.20 and faith ≥ 0.80 | Highly consistent with retrieved evidence but factually incorrect; indicates confident hallucination or fabricated statement. |
| UNSUP | Unsupported inference/Over-generalization | 0.20 < factual < 0.60 and faith < 0.80 | Contains partially correct content but extends beyond evidence or makes over-generalized claims. |
| MIS | Misinterpretation/Low relevance | relev ≤ 0.60 | Response misreads the prompt or diverges semantically from the user query; low topical alignment. |
| SUS | Suspected hallucination | factual ≤ 0.30 | Ensures coverage of low factual cases not captured by other rules; possible hallucination. |
| LF | Low faithfulness | faith ≤ 0.50 | Output loosely connected to retrieved context; potential misuse or misinterpretation of evidence. |

*factual* = factual correctness; *faith* = faithfulness; *relev* = answer relevancy.