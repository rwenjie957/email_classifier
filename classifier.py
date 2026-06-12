from openai import OpenAI

def classifer(api_key, promt_file, content, base_url, model):
    client = OpenAI(api_key=api_key, base_url=base_url)
    with open(promt_file, 'r', encoding='utf-8') as file:
        system_prompt = file.read()

    messages=[{"role":"system", "content":system_prompt},
        {"role":"user", "content":content}]


    response = client.chat.completions.create(
        model=model,
        messages = messages,
        stream=False,
        extra_body={"thinking":{"type":"enabled"}}
    )
    result_reasoning, result = response.choices[0].message.reasoning_content, response.choices[0].message.content
    return result_reasoning, result

if __name__ == '__main__':
    pass