"""
Health Q&A Evaluation Configuration
Using custom dataset + DeepSeek API
"""
# Import custom dataset (automatically registered)
from Health_EQBench import Health_EQBenchDataset, Health_EQBenchEvaluator

# Import OpenCompass components
from opencompass.models import OpenAI
from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer


# ===== 1. Configure GPT 4.1 Model =====
models = [
    dict(
        abbr='gpt-4.1',
        type=OpenAI,
        path='gpt-4.1',
        key="ENV",
        query_per_second=2,
        max_out_len=16384,
        batch_size=1,
        temperature=0.7,
        retry=3,
    )
]


# ===== 2. Configure Med EQBench Dataset =====
Health_EQBench_reader_cfg = dict(
    input_columns=['question'],
    output_column='eval_dict'
)

Health_EQBench_infer_cfg = dict(
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(round=[
            dict(role='HUMAN', prompt='{question}'),
        ])),
    retriever=dict(type=ZeroRetriever),
    inferencer=dict(type=GenInferencer, max_out_len=1024 * 16),
)

Health_EQBench_eval_cfg = dict(
    evaluator=dict(type=Health_EQBenchEvaluator)
)


datasets = [
    dict(
        type=Health_EQBenchDataset,
        abbr='Health_EQBench',
        path='data',
        name='examples',
        reader_cfg=Health_EQBench_reader_cfg,
        infer_cfg=Health_EQBench_infer_cfg,
        eval_cfg=Health_EQBench_eval_cfg,
    )
]


# ===== 3. Other Configure =====
work_dir = './outputs/examples'