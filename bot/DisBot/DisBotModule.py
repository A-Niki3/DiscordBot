import random
import requests
import re

def get_mikuji():
    result = ["大吉","吉","中吉","小吉"]
    return result[random.randint(0,3)]

def get_simple_dice():
    return random.randint(1,6)

def get_n_dice(n):
    return random.randint(1,n)

def gen_voice(style_id, text):
    try:
        # ベースURL
        base_url = "http://127.0.0.1:10101"

        # audio_queryリクエスト
        query_response = requests.post(
            f"{base_url}/audio_query",
            #json={},
            params={"speaker": style_id,
                    "text": text}
        )

        if query_response.status_code != 200:
            print("audio_queryリクエスト失敗:", query_response.status_code, query_response.text)
            return f'audio_queryリクエスト失敗: {query_response.status_code}, {query_response.text}'

        # synthesisリクエスト
        synthesis_response = requests.post(
            f"{base_url}/synthesis",
            params={"speaker": style_id},
            headers={"Content-Type": "application/json"},
            data=query_response.content
        )

        if synthesis_response.status_code == 200:
            # 音声ファイルを保存
            with open(f'voices/output.wav', "wb") as f:
                f.write(synthesis_response.content)
            print(f"音声ファイルを保存しました: voices/output.wav")
            return 0
        else:
            print("synthesisリクエスト失敗:", synthesis_response.status_code, synthesis_response.text)
            return f"synthesisリクエスト失敗: {synthesis_response.status_code}, {synthesis_response.text}"

    except Exception as e:
        return e

def replace_mentions(content):
    # URL
    url_pattern = r"(https?://\S+|www\.\S+)"
    content = re.sub(url_pattern,"URL",content)
    # <@&id>
    content = re.sub(r"<@&\d+>","ロール",content)
    # <@id>
    content = re.sub(r"<@\d+>","ユーザー",content)
    # <#id>
    content = re.sub(r"<#\d+>","チャンネル",content)
    
    return content

