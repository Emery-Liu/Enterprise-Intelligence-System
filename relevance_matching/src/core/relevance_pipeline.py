import json

from relevance_matching.src.core.relevance_prompt import PROMPT_SETTING
from relevance_matching.src.llm.extraction_client import chat


def judge_enterprise_relevance(
    enterprise_name: str,
    title: str,
    summary: str,
    content: str,
) -> bool:
    # step 1
    input_json = {
        "enterprise_name": enterprise_name,
        "title": title,
        "summary": summary,
        "content": content,
    }

    # step 
    prompt = PROMPT_SETTING.format(
        input_json=json.dumps(
            input_json,
            ensure_ascii=False,
            indent=2,
        )
    )

    print("【Judge Pipeline】Prepare for LLM...\n")

    # step 3
    response = chat(prompt)

    print("【Judge Pipeline】LLM return: \n")
    print(response)
    print("----------------------------------\n")

    # step 4
    response_clean = response.strip()
    if response_clean.startswith("```"):
        lines = response_clean.splitlines()
        response_clean = "\n".join(lines[1:-1]).strip()

    # step 5
    result = json.loads(response_clean)

    print("【Judge Pipeline】JSON encode successfully\n")

    # Step 6
    if "related" not in result:
        raise KeyError("JSON returned by LLM has no 'related'\n")

    if not isinstance(result["related"], bool):
        raise TypeError(
            f" 'related' should be bool, but {type(result['related']).__name__}。"
        )

    related = result["related"]

    print(f"【Judge Pipeline】final judgement: {related}\n")

    return related