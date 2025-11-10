import json
import os.path as osp
import pandas as pd
import numpy as np
from datasets import Dataset

from opencompass.registry import (LOAD_DATASET, ICL_EVALUATORS)
from .utils import *
from opencompass.datasets.base import BaseDataset
from opencompass.openicl import BaseEvaluator

evaluate_prompt = """
## 角色
你是一位内容评审员，负责根据评分细则对大模型生成的回答逐项评分。

## 任务
根据【评分细则】，逐条评估【待评分回答】中的内容，对每条细则分别做二元判断（1/0），并对每个判断给出简短理由。

## 评分准则
1. 加分项必须符合描述才能得分，减分项内容若存在相关表述即可扣分；
2. 对每个评分条目进行二进制判定（0/1），1表示符合条件，0表示不符合；
3. 输出格式必须严格遵循指定模板，不多加解释。

## 问题
<question>
{question}
</question>

## 待评分回答
<answer>
{answer}
</answer>

## 评分细则
{rubric}

## 输出要求
1. 每条评分细则必须转换为带序号的标记行。
2. 对每个判断结果（0或1）都需提供一个简短的判断理由。
3. 使用以下格式标记每个条目：
    加分项_序号_"条目具体名称":判定结果(1/0) | Reason: [请在此处填写40字以内的简短判断理由] | 给出具体出现的内容: [请在此处填写40字以内的简短位置]
    减分项_序号_"条目具体名称":判定结果(1/0) | Reason: [请在此处填写40字以内的简短判断理由] | 给出具体出现的内容: [请在此处填写40字以内的简短位置]
4. 不要添加任何解释性文字。
5. 保持输出纯净以便正则解析。

## 示例
加分项_9_"疾病情绪即时响应":1 | Reason: 在回应的第一段中，准确识别并命名用户的核心情绪 | 出现内容: "我理解您对医生未开药的决定可能有些困惑，但请放心"
""".strip()

rubrics_tags = [
    '个性化方案', '医疗安全关怀导向', '个人情绪 / 行动管理',
    '疾病错误认知', '疾病反常情绪推理', '医疗沟通失言情境',
    '暗示线索', '情绪归因理解',
    '角色影响', '个体情感价值', '文化背景考量',
    '意外情绪结果', '混合情绪', '情绪转换',
    '情感体验贯穿始终',
    '格式与重点呈现', '医疗语境语气适配', '医学语言通俗转化', '内容结构',
    '医疗行为肯定鼓励',
    '诊疗信息引导提问',
    '疾病情绪即时响应'
]


@LOAD_DATASET.register_module()
class Health_EQBenchDataset(BaseDataset):
    @staticmethod
    def load(path, name):
        filename = osp.join(path, f'{name}.csv')
        raw_data = []

        df = pd.read_csv(filename, encoding='utf-8')
        df = df.dropna(how='all')

        for _, row in df.iterrows():
            if pd.isna(row.get('id')) or pd.isna(row.get('question')) or pd.isna(row.get('rubrics')):
                continue

            question = row['question']
            rubrics = row['rubrics']

            eval_dict = {
                "id": row['id'],
                "question": question,
                "rubrics": rubrics,
            }

            new_data = {
                'question': question,
                'eval_dict': json.dumps(eval_dict, ensure_ascii=False)
            }

            raw_data.append(new_data)

        dataset = Dataset.from_list(raw_data)
        return dataset


@ICL_EVALUATORS.register_module()
class Health_EQBenchEvaluator(BaseEvaluator):
    def score(self, predictions, references, origin_prompt) -> dict:
        # test_set, origin_prompt, origin_prediction, input_columns
        if len(predictions) != len(references):
            return {'error': 'predictions and references have different length'}
        judge_details = []
        cases = []
        scores = []
        tag_score_bucket = {tag: [] for tag in rubrics_tags}

        for idx, (pred, ref) in enumerate(zip(predictions, references)):
            ref = json.loads(ref)
            rubrics = ref['rubrics']

            prompt = evaluate_prompt.format(question=ref['question'],
                                            answer=pred,
                                            rubric=rubrics)
            model_output = evaluate_score(prompt)

            parsed_rubrics = parse_rubric(rubrics)
            model_output_parsed = parse_llm_evaluation(model_output)
            single_score, tag_scores = calc_score_percent_one_query(parsed_rubrics, model_output_parsed)

            scores.append(single_score)
            for tag in rubrics_tags:
                tag_score_bucket[tag].append(tag_scores.get(tag, float('nan')))

            judge_detail = {
                "idx": idx,
                'prompt': origin_prompt[idx],
                'origin_prompt': origin_prompt[idx],
                # 'origin_prompt_hash': md5(origin_prompt[idx][0]['prompt'].encode('utf8')).hexdigest(),
                'processed_prediction': pred,
                'reference': rubrics,
                'correct': single_score
            }
            case = {
                'id': ref['id'],
                'question': ref['question'],
                'rubrics': rubrics,
                'model_answer': pred,
                'judge_model_scoring': model_output,
                'single_score': single_score,
                'tag_scores': tag_scores
            }

            judge_details.append(judge_detail)
            cases.append(case)

        final_score = sum(scores) / len(scores)

        avg_tag_scores = {
            tag: round(np.nanmean(vals), 2) if any(not np.isnan(v) for v in vals) else float('nan')
            for tag, vals in tag_score_bucket.items()
        }

        result = {
            'score': final_score,
            'detail': {
                'cases': cases,
                'tag_scores': avg_tag_scores
            },
            'judge_details': judge_details
        }
        return result
