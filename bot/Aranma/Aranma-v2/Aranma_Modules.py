import asyncio
from transformers import pipeline as pipe
from transformers import T5Tokenizer as t5t
import mcrcon
import discord
import csv
import json
import requests
import random
import re
import os

async def set_generator():
    return await asyncio.to_thread(pipe,"text-generation", model="rinna/japanese-gpt2-medium", tokenizer=t5t.from_pretrained("rinna/japanese-gpt2-medium"))

def set_intents(intents:discord.Intents):
    intents.messages = True
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True
    intents.voice_states = True
    return intents

def server_rcon(cmd:str, res:bool, info:list[str]):
    try:
        with mcrcon.MCRcon(info[0],info[1],int(info[2])) as rcon:
            response = rcon.command(cmd)
            if res == True:
                return response
            else:
                return 0
    except Exception as e:
        return str(e)

def addcsv(id:str):
    file_exists = False
    try:
        with open('request.csv','r',newline='') as csvfile:
            file_exists = True
    except FileNotFoundError :
        pass

    with open('request.csv','a',newline='') as csvfile:
        fieldname = ['mcids']
        writer = csv.DictWriter(csvfile, fieldnames=fieldname)

        if not file_exists:
            writer.writeheader()

        writer.writerow({'mcids': id})

def readcsv():
    ids = []

    try:
        with open('request.csv','r',newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ids.append(row['mcids'])
    except FileNotFoundError :
        print("File is not found")
    except KeyError:
        print("\"mcids\" row is not found")

    return ids

def operatecsv(target:int,permit:bool,info:list[str]):
    update = []
    header = None

    idlist = readcsv()

    try:
        if target < 0 or target > len(idlist):
            return IndexError("out of index")
        select_id = idlist[target-1]
    except IndexError as e:
        return e

    if permit == True:
        response = server_rcon(f'whitelist add {select_id}',True,info)
        if "Added" not in response:
            return response
    else:
        response = f'mcid:{select_id} refused'

    try:
        with open('request.csv','r',newline='') as csvfile:
            reader = csv.reader(csvfile)
            try:
                header = next(reader)
            except StopIteration as e:
                print(f'error occered:{e}')
                return

            for i,row in enumerate(reader):
                if i != target -1:
                    update.append(row)
    except FileNotFoundError:
        print("file is not found")
        return
    except IndexError:
        print("Index out of range")
        return
    except OSError as ose:
        print(f"Error:{ose}")
    
    with open('request.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(update)

    return response

def search_prefecture(prefecture:str):
    with open('pre.json','r',encoding='utf-8') as pre_f:
        pre_data = json.load(pre_f)

        return pre_data.get(prefecture)

def get_weather(prefecture):
    #get data
    url = f'https://www.jma.go.jp/bosai/forecast/data/forecast/{prefecture}.json'
    weather_json = requests.get(url).json()
    #choose data
    weather_date = weather_json[0]["timeSeries"][0]["timeDefines"][0]
    weather_weather = weather_json[0]["timeSeries"][0]["areas"][0]["weathers"][0]
    weather_temp = weather_json[0]["timeSeries"][2]["areas"][0]["temps"]
    temp_max = int(max(weather_temp))
    temp_min = int(min(weather_temp))
    if(temp_max < temp_min):
        copy = temp_min
        temp_min = temp_max
        temp_max = copy
    #delete fullsize space
    weather_weather = weather_weather.replace('　','')
    return weather_date,weather_weather,temp_max,temp_min

def dice_roll(dice:int,roll:int):
    nums = []
    for i in range(dice):
        nums.append(random.randint(1,roll))
    return nums

def get_mikuji():
    results = ["大吉","吉","中吉","小吉","アルティメット極凡","末吉","凶","大凶","極凶","家野吉"]
    weight = [5,10,20,25,1,10,8,6,3,2]

    result = random.choices(results, weights=weight)[0]
    return result

async def generate_mikuji(fortune,generator):
    output = await asyncio.to_thread(
                generator,
                f"今日の運勢は「{fortune}」だ！ラッキーカラーは",
                    max_length = 100,
                    num_return_sequences = 1,
                    truncation = True,
                    no_repeat_ngram_size = 2,
                    #early_stopping = True,
                    temperature = 0.5,
                    top_k = 50,
                    top_p = 0.8,
                    eos_token_id = 50256,
                    return_full_text = False
                )
    return(output[0]["generated_text"])

def replace(content:str):
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

async def play_sound(guild_id,vccl):
    file_path = os.path.join(os.path.dirname(__file__), 'フォルダ', 'output.wav')
    audio = discord.FFmpegPCMAudio(file_path) #ffmpegのインストール必須
    vccl[guild_id].play(audio)
    while vccl[guild_id].is_playing():
        await asyncio.sleep(1)
    os.remove(file_path)

