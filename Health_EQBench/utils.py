# -*-coding:utf-8-*-
import json
import random
import re
import requests
import time
import os
import uuid
import pandas as pd
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

ASYNC_CHAT_LOOP_TIME_OUT = 600
ASYNC_CHAT_LOOP_WAIT_SEC = 10
EVAL_MODEL_NAME='gpt-4.1'

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

def evaluate_score(prompt):
    output = llm_infer(prompt, EVAL_MODEL_NAME)
    if not output:
        return ""
    response = output.strip()
    return response

def create_weight_map(rubric_part): # 暂时弃用
    weight_map = {}
    rubric_part = rubric_part.strip()
    if not rubric_part:
        return {}
    weight_regex = r'\{[+-]?\s*(\d+)\s*\}'
    items = re.split(r'\n(?=\s*\d+[、【.])', rubric_part)
    if items and not re.match(r'^\s*\d+', items[0]):
        items.pop(0)
    for item_text in items:
        index_match = re.match(r'\s*(\d+)', item_text)
        if not index_match:
            continue
        index_str = index_match.group(1)
        weights_found = re.findall(weight_regex, item_text)
        total_weight = sum(int(w) for w in weights_found)
        if total_weight > 0:
            weight_map[index_str] = total_weight
    return weight_map

def get_rubric_weights(rubric): # 暂时弃用
    rubric_parts = re.split(r'减分项', rubric, maxsplit=1)
    bonus_rubric_part = rubric_parts[0]
    deduction_rubric_part = rubric_parts[1] if len(rubric_parts) > 1 else ""
    bonus_weights_map = create_weight_map(bonus_rubric_part)
    deduction_weights_map = create_weight_map(deduction_rubric_part)
    return bonus_weights_map, deduction_weights_map

def parse_rubric(rubric_text):
    rubric_dict = {}
    idx = 0
    flag = 100000
    for line in rubric_text.split('\n'):
        idx += 1
        line = line.strip()
        if not line or '加分项' in line:
            continue
        if '减分项' in line:
            flag = idx

        try:
            start_index = line.index('{')
            end_index = line.index('}')
            score = int(line[start_index + 1:end_index].replace(" ", ""))

            item_name = line.split('、')[0].strip()
            if idx < flag:
                item_key = f"加分项_{item_name}"
            elif idx > flag:
                item_key = f"减分项_{item_name}"
            start_index = line.index('【')
            end_index = line.index('】')
            tag = line[start_index + 1:end_index].replace(" ", "")
            # 寻找最相似的标签
            best_match, match_score = find_most_similar_tag(tag, rubrics_tags)
            rubric_dict[item_key] = {'score': score, 'tag': best_match, 'original_tag': tag}
        except ValueError:
            continue

    return rubric_dict

def parse_llm_evaluation(llm_response: str):
    if not isinstance(llm_response, str):
        return None
    try:
        pattern = r"(加分项|减分项)_(\d+)[^:]*:([01])\s*\|\s*Reason:\s*(.*?)\s*\|"
        llm_evaluations = re.findall(pattern, llm_response)
        parsed_details = []
        for item_type, index_str, score_str, reason_str in llm_evaluations:
            parsed_details.append({
                "type": item_type,
                "index": index_str,
                "score": int(score_str),
                "reason": reason_str.strip()
            })
        return parsed_details
    except Exception as e:
        print(f"Error parsing LLM evaluation: {e}\nResponse: {llm_response}")
        return None

def parse_llm_evaluation_rl(llm_response: str):
    if not isinstance(llm_response, str):
        return None
    try:
        pattern = r"(?m)^(?:[\d._\s]*?(?:加分项_|维度_))?(\d+)[._\s]*\"?([^:\"]+)\"?:[^\d\n]*?(\d)[^\n|]*?\|\s*Reason:\s*(.*?)(?:\s*\||$)"
        llm_evaluations = re.findall(pattern, llm_response, re.VERBOSE)
        parsed_details = []
        for index_str, dimension_name, score_str, reason_str in llm_evaluations:
            dimension_name_clean, _ = find_most_similar_tag(dimension_name, rubrics_tags)
            parsed_details.append({
                "index": index_str.strip(),
                "dimension": dimension_name_clean,
                "score": int(score_str),
                "reason": reason_str.strip()
            })
        return parsed_details if parsed_details else None
    except Exception as e:
        print(f"Error parsing LLM evaluation: {e}\nResponse: {llm_response}")
        return None

def parse_scores(score_text): # Temporarily deprecated
    score_dict = {}
    for line in score_text.split('\n'):
        line = line.strip().replace('：', ':')
        if line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key, value = parts
                try:
                    score_dict[key.strip()] = int(value.strip())
                except ValueError:
                    print(f"Warning: Unable to convert value '{value.strip()}' to an integer for key '{key.strip()}'.")
            else:
                print(f"Warning: Line '{line}' is not in the expected format 'key: value'.")
    return score_dict

def calculate_score_from_details(parsed_details, bonus_weights_map, deduction_weights_map): # Temporarily deprecated
    final_score = 0
    if not parsed_details:
        return 0
    for item in parsed_details:
        score = item.get("score", 0)
        item_type = item.get("type")
        index_str = item.get("index")

        if score == 0:
            continue
        if item_type == "加分项":
            weight = bonus_weights_map.get(index_str, 0)
            final_score += weight
        elif item_type == "减分项":
            weight = deduction_weights_map.get(index_str, 0)
            final_score -= weight
    total_possible_score = sum(bonus_weights_map.values())
    if total_possible_score == 0:
        return "0"
    percentage = (final_score / total_possible_score) * 100
    clamped_percentage = max(0, min(100, percentage))
    final_percentage_int = round(clamped_percentage)
    return final_percentage_int

def calculate_final_score(scores): # Temporarily deprecated
    valid_scores = [score for score in scores if pd.notna(score)]
    if not valid_scores:
        return pd.NA
    return int(round(sum(valid_scores) / len(valid_scores)))

def find_most_similar_tag(source_tag, candidate_tags):
   # --- Step 1: Text Preprocessing (Tokenization) ---
    def tokenize(text):
        return jieba.lcut(text)

    # Put source tag and all candidate tags in one list for unified processing
    all_tags = [source_tag] + candidate_tags
    corpus = [" ".join(tokenize(tag)) for tag in all_tags]

    # --- Step 2: Text Vectorization (TF-IDF) ---
    vectorizer = TfidfVectorizer()

    # Vectorize the tokenized corpus
    tfidf_matrix = vectorizer.fit_transform(corpus)


    # --- Step 3: Similarity Calculation (Cosine Similarity) ---
    # Source tag vector
    source_vector = tfidf_matrix[0]

    # Candidate tag vectors
    candidate_vectors = tfidf_matrix[1:]
    

    cosine_similarities = cosine_similarity(source_vector, candidate_vectors)
    similarities = cosine_similarities.flatten()
    most_similar_index = similarities.argmax()

    max_similarity_score = similarities[most_similar_index]
    most_similar_tag = candidate_tags[most_similar_index]

    return most_similar_tag, max_similarity_score

def calc_score_percent_one_query(parsed_rubrics, judge_model_scoring):
    add_max_total = 0          # Maximum possible score for all bonus items
    add_actual_total = 0       # Actual score obtained

    tag_addmax = {tag: 0 for tag in rubrics_tags}   # Maximum bonus score for each tag
    tag_add = {tag: 0 for tag in rubrics_tags}      # Actual score obtained

    for key, data in parsed_rubrics.items():
        tag = data['tag']
        score = data['score']
        if key.startswith('加分项'):
            add_max_total += score
            if tag in tag_addmax:
                tag_addmax[tag] += score

    for item in judge_model_scoring:
        t = item['type']
        idx = item['index']
        val = item['score']
        rubric_key = f"{t}_{idx}"
        if rubric_key not in parsed_rubrics:
            continue  # Skip items not in rubric
        tag = parsed_rubrics[rubric_key]['tag']
        score = parsed_rubrics[rubric_key]['score']
        add_actual_total += val * score
        tag_add[tag] += val * score

    total_score_percent = (add_actual_total / add_max_total * 100) if add_max_total else 0

    tag_score_percent = {}
    for tag in rubrics_tags:
        maxscore = tag_addmax[tag]
        addscore = tag_add[tag]
        if maxscore > 0:
            percent = (addscore / maxscore) * 100
            percent = round(percent, 2)
        else:
            percent = float('nan')
        tag_score_percent[tag] = percent

    return round(total_score_percent, 2), tag_score_percent

def calc_score_percent_one_query_rl(parsed_rubrics, judge_model_scoring):
    rubrics_tags_per_query = list(parsed_rubrics.keys())

    tag_actual_score = {tag: None for tag in rubrics_tags_per_query}  # LLM scores for each dimension (raw scores, not weighted)
    tag_weighted_score = {}  # Score*weight for each dimension
    tag_max_score = {}  # Maximum score for each dimension (weight*5)

    for item in judge_model_scoring:
        tag = item['dimension']
        score = item['score']  # 0~5
        tag_actual_score[tag] = score

    total_score = 0
    total_max = 0
    tag_score_percent = {}

    for tag in rubrics_tags_per_query:
        weight = parsed_rubrics[tag]
        score = tag_actual_score[tag]
        max_score = weight * 5
        tag_max_score[tag] = max_score
        if score is not None:
            weighted_score = score * weight
            percent = weighted_score / max_score * 100
            total_score += weighted_score
            percent = round(percent, 2)
            tag_weighted_score[tag] = weighted_score
        else:
            percent = float('nan')
            tag_weighted_score[tag] = float('nan')
        tag_score_percent[tag] = percent
        total_max += max_score

    total_score_percent = round(total_score / total_max * 100, 2) if total_max else float('nan')
    return total_score_percent, tag_score_percent


def llm_infer(messages, model, attemp_count=5, max_tokens=8192, temperature=0.0):
    if model == 'gpt-4-turbo-2024-04-09' and max_tokens > 4096:
        max_tokens = 4096

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    assert OPENAI_API_KEY is not None, "OPENAI_API_KEY is not set "

    return openai_api_infer_stream(
        messages=messages,
        model=model,
        url='https://api.openai.com/v1',
        key=OPENAI_API_KEY,
        attemp_count=attemp_count,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=1
    )

def openai_api_infer_stream(
        messages,
        model,
        url,
        key,
        attemp_count=5,
        max_tokens=8192,
        temperature=0.0,
        top_p=1
    ):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    client = OpenAI(
        api_key=key,
        base_url=url,
    )

    base_delay, max_delay = 4, 64
    result = ''
    attemp = 1
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                messages=messages,
                stream=True,
            )
            
            reasoning_content = []  # Define complete reasoning process
            prediction_content = []     # Define complete response
            is_answering = False   # Determine if reasoning process has ended and response has started
            
            for chunk in response:
                delta = chunk.choices[0].delta
                # print(delta)
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                    reasoning_content.append(delta.reasoning_content)
                else:
                    if delta.content != "" and is_answering == False:
                        is_answering = True
                    if delta.content:
                        prediction_content.append(delta.content)

            reasoning_content = ''.join(reasoning_content)
            prediction_content = ''.join(prediction_content)

            if len(reasoning_content) > 0:
                result = f"<think>{reasoning_content}</think>" + prediction_content
            else:
                result = ''.join(prediction_content)
            break

        except Exception as e:
            if attemp > attemp_count:
                print("Model {} Attemp {} failed, Exist. Exception: {}".format(model, attemp, e), flush=True)
                break
            else:
                print("Model {} Attemp {} failed, Exception: {}".format(model, attemp, e), flush=True)
            delay = min(base_delay * (2 ** attemp), max_delay)
            time.sleep(delay)
            attemp += 1
    # raise ValueError(f"{model} infer failed")
    return result

def split_and_remove_think(text) -> str:
    if type(text) is not str:
        return text
    try:
        text = think_process(text)
    except:
        pass

    THINK_TOKENS = ['</think>']
    for special_token in THINK_TOKENS:
        text = text.split(special_token)[-1]
    return text

def think_process(text):

    def gpt_oss_think(text):
        try:
            if "assistantfinal" in text:
                text = str(text).split("analysis", 1)[-1]
                parts = text.split("assistantfinal", 1)
                if len(parts) > 1:
                    text = f"<think>{text[0]}</think>\n{text[1]}"
                else:
                    text = parts[0]
            return text
        except Exception as e:
            return text

    def seed_oss_think(text):
        if "</seed:think>" in text:
            text = text.replace("</seed:think>", "</think>").replace("<seed:think>", "<think>")
        return text

    def hunyuan_remove_answer(text):
        if '<answer>' in text:
            text = text.split('<answer>')[-1].split('</answer>')[0]
        return text
    
    try:
        text = seed_oss_think(text)
        text = gpt_oss_think(text)
        text = hunyuan_remove_answer(text)
        return text
    except Exception as e:
        print(f"think_process error: {e}")
        return ""
