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
import uuid
import emoji

bad_words_ids = []
tokenizer = t5t.from_pretrained("rinna/japanese-gpt2-medium")

async def set_generator():
    load_bad_words()
    #print(bad_words_ids)
    return await asyncio.to_thread(pipe,"text-generation", model="rinna/japanese-gpt2-medium", tokenizer=tokenizer)

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

async def generate_mikuji(fortune:str,generator):
    inputs = prompt_tokenizer(f"今日の運勢は「{fortune}」だ！ラッキーカラーは")
    output = await asyncio.to_thread(
                generator.model.generate,
                inputs["input_ids"],
                    max_length = 100,
                    num_return_sequences = 1,
                    attention_mask = inputs["attention_mask"],
                    pad_token_id = tokenizer.eos_token_id,
                    #truncation = True,
                    no_repeat_ngram_size = 2,
                    #early_stopping = True,
                    temperature = 0.5,
                    top_k = 50,
                    top_p = 0.8,
                    eos_token_id = 50256,
                    #return_full_text = False,
                    bad_words_ids = bad_words_ids,
                    do_sample = True
                )
    gen_text = decode_output(output[0])
    return await asyncio.to_thread(check_text, gen_text)

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
    # <#!id>
    content = re.sub(r"<#!\d+>","ボイス",content)
    # <:stamp:>
    content = re.sub(r"<a:\w+:\d+>|<:\w+:\d+>","",content)
    # 記号
    symbol_pattern = r"[;:；：'’\"\”`‘*＊｜|ᐡﻌᐧ^£฿₰₣₤฿₣∀Å$€?？]"
    content = re.sub(symbol_pattern,"",content)
    # 絵文字類
    content = emoji.replace_emoji(content,"")
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
            file_name = f'{uuid.uuid4()}.wav'
            with open(f'voices/{file_name}', "wb") as f:
                f.write(synthesis_response.content)
            print(f"音声ファイルを保存しました: voices/{file_name}")
            return 0,file_name
        else:
            print("synthesisリクエスト失敗:", synthesis_response.status_code, synthesis_response.text)
            return 1,f"synthesisリクエスト失敗: {synthesis_response.status_code}, {synthesis_response.text}"

    except Exception as e:
        return 1,e

async def play_sound(vccl:discord.VoiceClient,file_name:str,queue:asyncio.Queue):
    file_path = os.path.join(os.path.dirname(__file__), 'voices', f'{file_name}')
    await queue.put(file_path) #ここまではいったんok

    if not vccl.is_playing():
        await handle_queue(vccl,queue)

async def handle_queue(vccl: discord.VoiceClient, queue: asyncio.Queue):
    while not queue.empty():
        file_path = await queue.get()

        audio = discord.FFmpegPCMAudio(file_path)
        vccl.play(audio)
        
        while vccl.is_playing():
            await asyncio.sleep(1)
        
        os.remove(file_path)

async def generate_text(text: str,generator):
    #print(bad_words_ids)
    inputs = prompt_tokenizer(text)
    output = await asyncio.to_thread(
                generator.model.generate,
                inputs["input_ids"],
                    max_length = 50,
                    num_return_sequences = 1,
                    #truncation = True,
                    no_repeat_ngram_size = 2,
                    #early_stopping = True,
                    attention_mask = inputs["attention_mask"],
                    pad_token_id = tokenizer.eos_token_id,
                    temperature = 0.75,
                    top_k = 50,
                    top_p = 0.9,
                    eos_token_id = 50256,
                    #return_full_text = True,
                    bad_words_ids = bad_words_ids,
                    do_sample = True
                )
    gen_text = decode_output(output[0])
    return await asyncio.to_thread(check_text,gen_text)

def prompt_tokenizer(prompt:str):
    return tokenizer(prompt, return_tensors="pt")

def decode_output(output):
    return tokenizer.decode(output,skip_special_tokens=True)

def load_bad_words():
    with open("bad_words.json","r",encoding="utf-8") as f:
        bad_words = [json.load(f)["bad_words"]]
    bad_words_ids.extend([tokenizer.encode(word, add_special_tokens=False) for word in bad_words])

def check_text(text:str):
    fillter = r'[@#]\S+|https?://\S+|pic\.twitter\.com/\S+'
    matches = re.findall(fillter,text)
    print(matches)
    text = re.sub(fillter,"",text)
    if matches:
        bads_add_to_json(matches)
        text = f"{text}\n-# 生成した文章から{matches}が検出されました"
    return text

def bads_add_to_json(words:list[str]):
    with open("bad_words.json","r",encoding="utf-8") as f:
        data = json.load(f)
    edit_matches = []
    for i in range(len(words)):
        if words[i] not in data["bad_words"]:
            before_word = f" {words[i]}" #前にスペースがあるパターン
            after_word = f"{words[i]} "  #後にスペースがあるパターン
            edit_matches.append(words[i])
            edit_matches.append(before_word)
            edit_matches.append(after_word)
    #print(edit_matches)
    data["bad_words"].extend(edit_matches)
    with open("bad_words.json","w",encoding="utf-8") as f:
        json.dump(data, f ,indent=4,ensure_ascii=False)
    load_bad_words()

def clear_voices():
    voices_dir = os.path.join(os.path.dirname(__file__),'voices')
    if not os.path.exists(voices_dir):
        return f'{voices_dir} not found'
    files = os.listdir(voices_dir)
    if not files:
        return 0

    for voice in files:
        voice_path = os.path.join(voices_dir,voice)
        if os.path.isfile(voice_path):
            try:
                os.remove(voice_path)
            except Exception as e:
                return f'Error has occured during deleting {voice_path}\nExcept:{e}'
    return 0
