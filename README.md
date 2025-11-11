[//]: # (# MedEQBench: Medical Emotional Intelligence Benchmark for LLMs)
<div align="center">
  <img src="./img/1.png" alt="MedEQ" width="180" style="max-width:100%; height:auto;">
  <h1 style="margin:16px 0 8px;">MedEQBench: Medical Emotional Intelligence Benchmark for LLMs</h1>
</div>

<a href="https://opensource.org/licenses/Apache-2.0">
  <img src="https://img.shields.io/badge/License-Apache%202.0-green.svg" alt="License: Apache 2.0">
</a>


---

## Overview

The MedEQBench is **the first evaluation suite** specifically designed for **medical contexts** to assess Large Language Models' (LLMs) capabilities in **emotional perception** (recognition/understanding) and **empathic expression** (supportive, safe, and context-aware responses). This suite focuses on 51 realistic and semi-realistic psychology/health scenarios, including 400 dialogues derived from real-world medical interactions. It employs fine-grained rubrics and a multi-dimensional scoring system (with at least 20+ rubric items per scenario) to enable reproducible experiments and validate model alignment.

- **Scenarios**: **400** 
- **Rubric items**: **8,000** (≈20 atomic items per scenario on average)  
- **Evaluation dimensions**: **22** (perception, reasoning/attribution, empathy style, safety/ethics, etc.)


---
## Key features
🩺 **The First Systematic Benchmark for Humanistic Care Evaluation in Medical LLMs** → Proposes the inaugural assessment standard for humanistic care capabilities of medical large language models, focusing on evaluating Emotional Perception (recognition/understanding) and Empathic Expression (supportive, safe, context-aware responses) abilities in clinician-patient dialogue scenarios.

🌐 **Real-World Anchoring** → Built on 400 authentic medical dialogues (semi/fully realistic), capturing nuanced emotional dynamics and context-aware challenges in healthcare interactions.

📊 **Granular Multidimensionality** → Adapt existing large language model emotional intelligence measurement metrics to medical scenarios, with each dialogue co-authored by multiple medical and psychology experts to create at least 20+ rubrics.

🛡️ **Expert-Validated Framework** → 400 scenarios and 8,000 rubric items rigorously designed and cross-checked by psychology/healthcare experts to ensure clinical relevance and alignment.


## Liscense

We are releasing this project under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). This allows for both personal and commercial use, provided that the original license and copyright notice are included in any distributed copies or substantial portions of the software.

We are releasing this project under the Creative Commons Attribution 4.0 International License (CC BY 4.0).


---

## What’s Inside

### Scenario Types
- Counseling/clinical dialogue snippets (anonymized)
- Medical communication & health concerns
- 51 different department scenario sources (including gynecology, pediatrics, oncology, emergency department, etc.)

### Evaluation Dimensions
Spanning three domains:  
* **Empathic Communication Competence**: Disease-Related Emotional Responsiveness, Clinical Inquiry Navigation, Therapeutic Affirmation, Jargon-to-Lay Translation, Clinical Register Adaptation, Information Architecture, Content Structuring and Emotionally-Integrated Interaction.
*  **Clinical Emotional Literacy**: Emotional Transition, Mixed Affect States, Counterintuitive Emotional Outcomes, Cultural Contextualization, Personal Value Recognition, Role-Driven Affect Analysis, Implicit Signal Decoding, Attributional Reasoning, Clinical Miscommunication Contexts, Atypical Pathology-Affect Inference and Medical Misconception Resolution.
* **Affective Safety Praxis**: Self-Regulation in Clinical Contexts, Safety-Centric Care Protocols and Personalized Intervention Design.


### Rubric Design (8,000 items)
- **Atomicity**: each rubric item targets one actionable criterion  
- **Scales**: 0–4 (or 0–5) anchored levels with positive/negative examples  
- **Coverage**: emotion correctness & granularity, intensity & wording, reflective listening, non-blaming language, risk alerting & referral, etc.

---

## Data Structure

```
.
├── data/
│   ├── med_eq.csv
│   ├── examples.csv
├── config/
│   ├── examples_config.py
│   └── ...
├── Health_EQBench/
│   ├── __init__.py            
│   └── Health_EQBench.py  
│   └── utils.py
├── outputs/
│   └── ...
├── run_examples.sh
├── requirements.txt
└── README.md
```

### Data Example
```
Question: 三岁小朋友没发烧，流清涕，要吃什么药？
Rubrics:
1、【疾病情绪及时响应】答复的开篇立刻、直接地识别并回应了家长最核心的焦虑和担忧情绪。使用温暖、理解的语言，如：“看到宝宝不舒服，您一定很着急/很心疼吧。”，迅速与家长建立情感连接。{+6}
2、【诊疗信息引导提问】通过关怀式的提问来引导家长提供更多信息。提问的目的不仅是收集信息，更是为了展示“我想更全面地了解宝宝的情况来帮助你”。例如：“为了能更准确地判断，您可以多告诉我一些细节吗？比如宝宝的精神状态怎么样，还愿意玩吗？胃口好不好？”{+1}
3、 ...
```
---

## Quick Start

### Installation
```bash
git clone https://github.com/AQ-MedAI/MedEQBench.git
cd AQ-MedAI/MedEQBench

conda create --name opencompass python=3.10 
conda activate opencompass
pip install -U opencompass
pip install -r requirements.txt
```

### Run a Baseline Evaluation
```bash
export OPENAI_API_KEY=xxxx

bash run_examples.sh
```


### Example Report (excerpt)
| dataset | version | metric | mode | gpt-4.1 |
|----- | ----- | ----- | ----- | -----|
| Health_EQBench | 83f4b2 | score | gen | 44.27 |


---
## Evaluation Results

### Evaluation Protocol
- **Dimension-level scoring**: Based on 22 dimensions, each question comes with 15-22 independent rubrics as scoring criteria.
- **LLM-as-Judge (optional)**: We use LLMs to score each question's response against these rubrics.
- **Human Review (recommended)**: Scripts process and aggregate the LLM scoring results - detailed code can be found  in `Health_EQBench/utils.py`.

---
### Main Results
| Model | HealthBench | EmoBench | MedEQBench (ours) | 
|-------|-------------|----------|-------------------|
| Qwen3-235B-A22B-Thinking-2507   | 54.88 | 48.80 | 69.95             |
| Baichuan-M2-32B-Thinking        | 59.93 | 31.20 | 67.13             |
| Qwen3-30B-A3B-Thinking-2507     | 47.80 | 47.60 | 64.98             |
| DeepSeek-V3.1-Terminus-Thinking | 50.37 | 64.00 | 63.69             |
| DeepSeek-R1-0528                | 54.56 | 61.60 | 62.58             |
| Gemini-2.5-Pro-With-Thinking    | 49.72 | 66.10 | 61.38             |
| GPT-5-2025-08-07-Thinking-High  | 67.20 | 70.50 | 51.01             |
| Doubao-Seed-1.6-thinking        | 53.51 | 66.40 | 44.79             |
| GPT-4.1-2025-04-14              | 47.37 | 57.20 | 35.72             |
| Claude-sonnet-4.5-20250929      | 43.65 | 65.10 | 33.91             |
| GPT-4o-2024-11-20               | 43.26 | 56.90 | 31.18             |

* Unlike HealthBench, which purely tests models' medical expertise, and EmoBench, which evaluates models' emotional intelligence capabilities, MedEQBench assesses the degree of empathetic care models demonstrate toward patient emotions in medical scenarios.



### Results Across 22 Dimensions
| Dimensions | DeepSeek-R1-0528 | Qwen3-235B-A22B-Thinking-2507 | Gpt-5-2025-08-07 | Doubao_Seed_1.6_Thinking | Gemini-2.5-Pro-With-Thinking | Baichuan-M2-32B-Thinking | Claude-4.5-sonnet |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Personalized Care Plan | 71.35 | 79.19 | 91.35 | 69.46 | 66.49 | 93.51 | 44.86 |
| Safety- and Compassion-Oriented Medical Care | 94.19 | 96.85 | 82.81 | 81.36 | 91.71 | 98.55 | 68.52 |
| Personal Emotion and Behavior Regulation | 80.87 | 88.62 | 84.50 | 73.12 | 85.85 | 94.92 | 62.95 |
| Misconceptions About Illness | 84.50 | 90.56 | 82.57 | 80.87 | 80.73 | 88.14 | 52.54 |
| Suggestive Cues | 76.27 | 84.99 | 68.52 | 61.74 | 78.78 | 83.78 | 46.25 |
| Understanding Emotional Attribution | 57.38 | 66.83 | 22.03 | 22.52 | 57.07 | 54.00 | 8.96 |
| Role Influence | 47.57 | 58.50 | 26.70 | 26.94 | 48.66 | 52.91 | 18.20 |
| Cultural Context Consideration | 23.93 | 39.32 | 22.22 | 21.79 | 29.18 | 39.32 | 13.68 |
| Mixed Emotions | 48.67 | 61.74 | 25.67 | 25.18 | 47.07 | 48.67 | 8.72 |
| Emotionally Continuous Experience | 57.38 | 62.71 | 7.02 | 9.44 | 53.41 | 48.67 | 1.94 |
| Structure and Emphasis in Presentation | 99.76 | 100.00 | 99.51 | 100.00 | 99.75 | 100.00 | 100.00 |
| Tone Adaptation in Clinical Context | 97.09 | 96.13 | 94.19 | 91.77 | 96.83 | 97.82 | 83.78 |
| Translation of Medical Terminology into Lay Language | 83.05 | 85.96 | 71.67 | 80.63 | 90.73 | 74.82 | 56.51 |
| Positive Reinforcement of Health Behaviors | 22.76 | 35.35 | 2.66 | 5.81 | 18.54 | 19.61 | 2.18 |
| Guided Questioning in Clinical Communication | 28.09 | 36.56 | 91.28 | 19.13 | 19.27 | 69.98 | 26.39 |
| Real-Time Emotional Response to Illness | 51.21 | 52.91 | 8.01 | 4.85 | 51.34 | 40.53 | 2.67 |
| Emotional Transition | 56.48 | 61.14 | 26.42 | 30.05 | 58.85 | 50.78 | 16.58 |
| Medical Communication Misstatement Scenarios | 73.25 | 72.43 | 72.84 | 72.84 | 73.14 | 73.66 | 71.60 |
| Individual Emotional Value | 27.85 | 42.92 | 6.39 | 6.39 | 27.06 | 29.68 | 1.37 |
| Unexpected Emotional Outcomes | 62.58 | 69.94 | 52.15 | 56.44 | 62.96 | 66.87 | 43.56 |
| Atypical Emotional Reasoning in Illness | 48.68 | 59.87 | 29.61 | 27.63 | 46.71 | 53.95 | 16.45 |
| **Total** | **62.22** | **69.62** | **51.41** | **45.61** | **62.68** | **67.44** | **35.46** |

### Radar Chart for Model Capability 
![MedEQ Radar Chart](img/radar_chart.png)
📊 [Download PDF](img/radar_chart.pdf)

### Case Study
* **Question**: 
  ```
  儿童出现高热，伴有踝关节肿胀，医生怀疑骨髓炎
  ```
* High Score Result Sample
    ```
    看到孩子高烧不退还伴踝关节肿胀，医生怀疑骨髓炎，这确实是个需要高度重视的情况！作为家长，此刻的焦虑和担忧我完全理解。**儿童高热伴单关节（尤其是踝关节）肿胀、疼痛、活动受限，骨髓炎确实是必须紧急排查的严重疾病之一，但同时也需要与其他几种关键疾病进行鉴别。**

    以下是对这种情况的详细分析，帮助你理解医生的思路和接下来可能发生的事情：

    ## 🦴 一、 为什么医生高度怀疑骨髓炎？

    1.  **典型表现：**
        *   **高热：** 急性骨髓炎通常起病急骤，伴有高热（常 > 38.5°C）、寒战等全身中毒症状。
        *   **局部症状：** 感染骨的**干骺端**（长骨两端靠近关节的部分）是儿童骨髓炎最常见部位。踝关节附近的大骨头（胫骨远端、腓骨远端）的干骺端感染非常常见。
        *   **疼痛：** 患处（踝关节周围，可能小腿下段或足跟上方）有**剧烈、持续性疼痛**，孩子会**拒绝活动患肢、拒绝负重行走**，甚至轻微触碰或移动关节都会引起剧痛哭闹。
        *   **肿胀与发红：** 感染部位及周围软组织会出现明显肿胀、皮肤发红、皮温升高。
        *   **功能障碍：** 踝关节活动严重受限。

    ...
    ```

* Low Score Result Sample
    ```
    # 儿童高热伴踝关节肿胀的鉴别诊断

    当儿童出现**高热 + 踝关节肿胀**时，需要考虑以下疾病：

    ## 主要鉴别诊断

    ### 1. **化脓性关节炎（更可能）**
    - **特点**：关节腔内感染
    - **表现**：
    - 关节红、肿、热、痛
    - 活动受限明显（被动活动剧痛）
    - 高热、全身中毒症状
    - **好发部位**：髋、膝关节多见

    ### 2. **急性骨髓炎**
    - **特点**：骨髓及骨质感染
    - **表现**：
    - 骨干痛、压痛
    - 邻近关节可能肿胀
    - 但**关节活动相对较好**
    ****

    ...
    ```

* GPT-5 Sample
    ```
    孩子出现高热并伴踝关节肿胀，需要尽快就医（急诊）。这种情况提示可能的急性骨髓炎或化脓性关节炎，属于儿科/骨科急症，延误治疗可能导致关节破坏、骨生长受影响甚至全身感染。

    建议立即做的事
    - 立刻前往医院急诊或按医生安排住院。如果孩子不能行走/拒绝负重、踝部明显红肿热痛、持续高热（≥39°C）、精神差或出现寒战，务必尽快就诊。
    - 路上可给予退烧止痛：对乙酰氨基酚（扑热息痛）10–15 mg/kg，每6–8小时一次；或布洛芬10 mg/kg，每8小时一次。不要超过说明书总剂量；如果孩子脱水、有肾病或胃病请避免布洛芬。切勿给儿童服用阿司匹林。
    - 让孩子休息、限制患肢活动，鼓励少量多次喝水。

    医院通常会做的检查与治疗
    - 血液检查：血常规、CRP/ESR、可能加降钙素原；抽血培养（尽量在使用抗生素前）。
    - 影像学：X片早期常正常；超声可看关节积液；MRI最敏感，有助于明确骨髓炎范围和是否有脓肿。
    - 必要时做关节穿刺或骨/软组织穿刺引流并送培养，既帮助确诊也能减压。
    - 抗生素：经验性静脉抗生素尽早启动，并根据培养结果调整。常需覆盖金黄色葡萄球菌（包括可能的耐甲氧西林），学龄前儿童还要考虑金氏杆菌（Kingella kingae）；患有镰状细胞病的孩子需要考虑沙门菌。
    
    ...
    ```

  * Notably, we found that while GPT-5 demonstrates strong emotional consideration for conversational partners in general scenarios, it tends toward a more serious tone in medical contexts, reducing warm and approachable language. We speculate this may be related to GPT-5's response strategy selection or its medical training data.


---

## Annotation & Quality Assurance

- **Process**: scenario drafting → preliminary review → dimension/rubric assignment → secondary review → pilot scoring (LLM/human) → anchor tuning   
- **Bias & Safety**: additional checklist for sensitive groups, cultures, and medical/clinical contexts

---

## Ethics & Use

- For **research and evaluation** only. Not for medical diagnosis, emergency intervention, legal/disciplinary decisions, or other high-risk purposes.  
- Potentially triggering content (self-harm, abuse, etc.) is minimized and labeled; safety metrics highlight risk-related dimensions.  
- In clinical/medical contexts, ensure qualified professionals are involved and follow local laws and ethics.

---

## Contact

- Author:AQ-Med Team,Ant-ADS Team,Ant-DILAB
- Email:joyce.yxy@antgroup.com,yangzhengkai.yzk@antgroup.com

