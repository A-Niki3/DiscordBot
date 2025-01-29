#import
import asyncio
import configparser
import csv
import discord
from discord import app_commands
import json
import mcrcon
import os
import random
from random import randint
import re
import requests
from transformers import pipeline as pipe
from transformers import T5Tokenizer as t5t


#user
import aivis_mod as aimod
import aranma_ai_module as aim

#Path of config
config_file = 'token.ini'
sconfig_file = 'rconpass.ini'

#read config
config = configparser.ConfigParser()
sconfig = configparser.ConfigParser()
config.read(config_file)
sconfig.read(sconfig_file)

#read server information
SERVER_HOST = 'server ip'
SERVER_PORT = int(sconfig.get('Server', 'port'))
RCON_PASSWORD = sconfig.get('Server', 'pass')

#mc server join request user id csvfile path
csvfilename = 'request.csv'

# ai generator set
generator = pipe("text-generation", model="rinna/japanese-gpt2-medium", tokenizer=t5t.from_pretrained("rinna/japanese-gpt2-medium"))

#read bot information
BT = config.get('BOT', 'TOKEN')

#setup bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# for vc dict
rd_ch = {} #read channel dict
join_ch = {} #join channel dict
vc_cl = {} # VoiceChannel Client dict

#mcrcon send function
def serverrcon(cmd,need_response):
   try:
      with mcrcon.MCRcon(SERVER_HOST,RCON_PASSWORD,SERVER_PORT) as rcon:
         response = rcon.command(cmd)
         if need_response == True:
            return response
         else:
            return 0
   except Exception as e:
      print("An error occurred:",str(e))
      return str(e)

#Search prefecture from json
def search_prefecture(prefecture):
   with open('pre.json','r',encoding='utf-8') as pre_f:
      pre_data = json.load(pre_f)

      return pre_data.get(prefecture)

#Get weather information
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

#Generate dice roll
def dice_roll(dice,roll):
   gen_num = []
   for i in range(dice):
      gen_num.append(randint(1,roll))
   return gen_num

#Generate mikujiresult
def get_mikuji():
   results = ["大吉","吉","中吉","小吉","アルティメット極凡","末吉","凶","大凶","極凶","家野吉"]
   weight = [5,10,20,25,1,10,8,6,3,2]

   result = random.choices(results, weights=weight)[0]
   return result

#add mcid to csv
def addcsv(id):
   file_exists = False
   try:
      with open(csvfilename,'r',newline='') as csvfile:
            file_exists = True
   except FileNotFoundError :
      pass

   with open(csvfilename,'a',newline='') as csvfile:
      fieldname = ['mcids']
      writer = csv.DictWriter(csvfile, fieldnames=fieldname)

      if not file_exists:
            writer.writeheader()

      writer.writerow({'mcids': id})

#get mcid from csv
def readcsv():
   ids = []

   try:
      with open(csvfilename,'r',newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
               ids.append(row['mcids'])
   except FileNotFoundError :
      print("File is not found")
   except KeyError:
      print("\"mcids\" row is not found")

   return ids

#get mcid , add whitelist and remove mcid on csv
def operatecsv(target,permit):
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
      response = serverrcon(f'whitelist add {select_id}',True)
      if "Added" not in response:
         return response
   else:
      response = f'mcid:{select_id} refused'

   try:
      with open(csvfilename,'r',newline='') as csvfile:
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
   
   with open(csvfilename,'w',newline='') as csvfile:
      writer = csv.writer(csvfile)
      writer.writerow(header)
      writer.writerows(update)

   return response

#bot boot
@bot.event
async def on_ready():
   print("アランマbot 起動")
   activity = f"森林の浄化"
   await bot.change_presence(activity=discord.Game(activity))

   await tree.sync()

#------------
#bot commands
#------------
@tree.command(name='hello',description='アランマが返事をしてくれるよ！')
async def test(ctx: discord.Interaction):
   await ctx.response.send_message(f"ナラ{ctx.user.display_name}元気か?")

@tree.command(name='mcmsg',description='開いているマイクラ鯖にメッセージを送れるよ！')
async def rcon_message(ctx: discord.Interaction, message: str):
   result = serverrcon(f"msg @a from §9Discord:§a{ctx.user.display_name}§f：{message}",False)
   if result == 0:
      text = f"from Discord:{ctx.user.display_name}:{message}"
   else:
      text = result
   await ctx.response.send_message(text)

@tree.command(name='list',description='鯖にログインしている人数を調べるよ！')
async def plcnt(ctx: discord.Interaction):
   result = serverrcon("list",True)
   await ctx.response.send_message(result)

@tree.command(name='ggrks',description='Google検索できるよ!')
async def ggrks(ctx: discord.Interaction,word: str):
   await ctx.response.send_message(f'https://www.google.com/search?q={word}')

@tree.command(name='seed',description='起動しているマイクラサーバーのワールドseedを調べます')
async def getseed(ctx: discord.Interaction):
   result = serverrcon("seed",True)
   await ctx.response.send_message(f"{result}")

@tree.command(name='slimech',description='slimefinderで検索できるよ')
async def ggrks(ctx: discord.Interaction,seed: str):
   await ctx.response.send_message(f'https://www.chunkbase.com/apps/slime-finder#seed={seed}&platform=java&x=0&z=0&zoom=1')

@tree.command(name='reqjoin',description='マイクラ鯖への参加申請')
async def reqjoin(ctx: discord.Interaction,mcid: str):
   dev_id = await bot.fetch_user('作成者のID')
   addcsv(mcid)
   await dev_id.send(f'新しい参加申請を request.csv に追加しました\nServer name:{ctx.user.display_name}\nmcid:{mcid}')
   await ctx.response.send_message(f'mcid:{mcid}で申請しました。')

#--------------
#Embed commands
#--------------
@tree.command(name='genyt',description='原神のYouTubeチャンネルへアクセス')
async def GenYT(ctx: discord.Interaction):
   emb = discord.Embed(title='原神-Genshin-公式',url='https://www.youtube.com/@Genshin_JP/videos',description='原神の公式チャンネル')
   emb.set_image(url='https://cdn1.epicgames.com/offer/879b0d8776ab46a59a129983ba78f0ce/genshintall_1200x1600-4a5697be3925e8cb1f59725a9830cafc')
   await ctx.response.send_message(embed=emb)

@tree.command(name='tmap',description='Teyvat Mapの呼び出し')
async def tmap(ctx: discord.Interaction):
   emb = discord.Embed(title='テイワットマップ',url='https://act.hoyolab.com/ys/app/interactive-map/index.html',description='Teyvat Map')
   emb.set_image(url='https://raw.githubusercontent.com/Teyvat-Moe/teyvat.moe/master/assets/Social.png')
   await ctx.response.send_message(embed=emb)

@tree.command(name='fbos',description='フィールドボスルーレット')
async def fbos(ctx: discord.Interaction):
   emb = discord.Embed(title='フィールドボスルーレット',url='https://shindanmaker.com/1159377',description='最新版対応のフィールドボスを決めるためのルーレット')
   emb.set_image(url='https://pbs.twimg.com/profile_images/875575092146655233/LdRgE27i_400x400.jpg')
   await ctx.response.send_message(embed=emb)

@tree.command(name='wbos',description='週ボスルーレット')
async def wbos(ctx: discord.Interaction):
   emb = discord.Embed(title='週ボスルーレット',url='https://shindanmaker.com/1159445',description='最新版対応の週ボスに困った時のルーレット')
   emb.set_image(url='https://pbs.twimg.com/profile_images/875575092146655233/LdRgE27i_400x400.jpg')
   await ctx.response.send_message(embed=emb)

@tree.command(name='aks',description='Akasha Systemへのアクセス')
async def aks(ctx: discord.Interaction):
   emb = discord.Embed(title='Akasha System',url='https://akasha.cv/',description='Akasha Systemで能力をチェック')
   emb.set_image(url='https://static.wikia.nocookie.net/gensin-impact/images/a/a3/Akasha_Terminal_Interface.png/revision/latest/scale-to-width-down/250?cb=20221106063828')
   await ctx.response.send_message(embed=emb)

@tree.command(name='pmp',description='Paimon+を呼び出すよ')
async def pmp(ctx: discord.Interaction):
   emb = discord.Embed(title='Paimon+',url='https://paimon.plus/ja/',description='原神webツールPaimon+')
   emb.set_image(url='https://lh3.googleusercontent.com/RaBLdg6c2xIarhZrBRwLVSZIcZhU0JHnsv7Bl74fuHA0g7facemk3hw1D7KXHT6wi-zFRrRBRFSLTkKwSKpw-54XgkydZ4Wk-l9dQU6NjbFvYXfp0MOQA8tusgOSVtOjteZVUTNZCAQ=w800')
   await ctx.response.send_message(embed=emb)

@tree.command(name='gcode',description='配布コードの入力')
async def gcode(ctx: discord.Interaction):
   emb = discord.Embed(title='原神－原石に満ちた課金ニューワールド',url='https://genshin.hoyoverse.com/ja/gift',description='配布コードの入力ページはこちらから')
   emb.set_image(url='https://www.famitsu.com/images/000/318/634/y_6513b063bb4b3.jpg')
   await ctx.response.send_message(embed=emb)

@tree.command(name='gcdgen',description='原神配布コード入力済みURL発行')
async def gcdgen(ctx: discord.Interaction, code: str):
   URL = f'https://genshin.hoyoverse.com/ja/gift?code={code}'
   emb = discord.Embed(title='原神－原石に満ちた課金ニューワールド',url=URL,description='コード入力済みのページはこちらから')
   emb.add_field(name='Code',value=f'{code}')
   emb.set_image(url='https://www.famitsu.com/images/000/318/634/y_6513b063bb4b3.jpg')
   await ctx.response.send_message(embed=emb)

@tree.command(name='scode',description='配布コードの入力')
async def gcode(ctx: discord.Interaction):
   emb = discord.Embed(title='スタレ－原石が廃れた列車旅',url='https://hsr.hoyoverse.com/gift',description='配布コードの入力ページはこちらから')
   emb.set_image(url='https://th.bing.com/th/id/OIP.t5Viq2NQxsfA3zEKNjROJAHaD6?pid=ImgDet&rs=1')
   await ctx.response.send_message(embed=emb)

@tree.command(name='scdgen',description='スタレ配布コード入力済みURL発行')
async def gcdgen(ctx: discord.Interaction, code: str):
   URL = f'https://hsr.hoyoverse.com/gift?code={code}'
   emb = discord.Embed(title='スタレ－原石が廃れた列車旅',url=URL,description='コード入力済みのページはこちらから')
   emb.add_field(name='Code',value=f'{code}')
   emb.set_image(url='https://th.bing.com/th/id/OIP.t5Viq2NQxsfA3zEKNjROJAHaD6?pid=ImgDet&rs=1')
   await ctx.response.send_message(embed=emb)

@tree.command(name='weather',description='今日の天気を教えてくれるよ')
@app_commands.describe(prefecture = '都府県をつけずに入力してね(例：東京都→東京)')
async def weather(ctx: discord.Interaction, prefecture: str):
   number = search_prefecture(prefecture)
   if number is not None:
      today_weather = get_weather(number)
      emb = discord.Embed(title='アランマの天気予報☆',description=f'ナラに今日の{prefecture}の天気を教えるよ')
      emb.add_field(name=f'時間:{today_weather[0]}',value=f'今日の{prefecture}は、{today_weather[1]}だ',inline=False)
      emb.add_field(name=f'{prefecture}の最高気温',value=f'{today_weather[2]}℃だ',inline=True)
      emb.add_field(name=f'{prefecture}の最低気温',value=f'{today_weather[3]}℃だ',inline=True)
      await ctx.response.send_message(embed=emb)
   else:
      await ctx.response.send_message(f'{prefecture}は見つかりません。誤字、都道府県がついていないか確認してください。')

@tree.command(name='bks',description='みんなで踊ろう')
async def bks(ctx: discord.Interaction):
   await ctx.response.send_message(f'ナラ{ctx.user.display_name}、大人しく課金した方がいいぞ\nhttps://tenor.com/view/genshin-impact-furina-focalors-hydro-archon-fortnite-gif-6682083727853727725')

@tree.command(name='reboot',description='起動しているマイクラサーバーを再起動させます')
async def reboot(ctx: discord.Interaction):
   serverrcon("save-all",False)
   result = serverrcon("stop",False)
   if result == 0:
      text = "再起動を開始しました。しばらく後に確認してください。"
   else:
      text = result
   await ctx.response.send_message(f"停止プログラム実行結果\n{text}")

#----------------------
#Select choice commands
#----------------------
@tree.command(name='dice',description='TRPGのような乱数生成ができるよ')
@app_commands.choices(
   dice=[
   discord.app_commands.Choice(name='1',value=1),
   discord.app_commands.Choice(name='2',value=2),
   discord.app_commands.Choice(name='3',value=3),
   discord.app_commands.Choice(name='4',value=4),
   discord.app_commands.Choice(name='5',value=5),
   discord.app_commands.Choice(name='6',value=6),
   discord.app_commands.Choice(name='7',value=7),
   discord.app_commands.Choice(name='8',value=8),
   discord.app_commands.Choice(name='9',value=9),
   discord.app_commands.Choice(name='10',value=10)],
   roll=[
   discord.app_commands.Choice(name='2',value=2),
   discord.app_commands.Choice(name='4',value=4),
   discord.app_commands.Choice(name='6',value=6),
   discord.app_commands.Choice(name='8',value=8),
   discord.app_commands.Choice(name='10',value=10),
   discord.app_commands.Choice(name='12',value=12),
   discord.app_commands.Choice(name='20',value=20),
   discord.app_commands.Choice(name='100',value=100),])
async def sel(ctx: discord.Interaction, dice: int, roll: int):
   result = dice_roll(dice,roll)
   await ctx.response.send_message(f'{dice}D{roll}の結果、\n{result}')

#---------------
#random commands
#---------------
@tree.command(name='omikuji',description='おみくじが引けるよ')
async def mikuji(ctx: discord.Interaction):
   result = get_mikuji()
   await ctx.response.send_message(f'ナラ{ctx.user.display_name}の今日の運勢は{result}だ')

#-------------
#ai commands
#-------------
@tree.command(name='newomikuji',description='運勢に加えてコメントしてくれるよ！')
async def omikujineo(ctx: discord.Interaction):
   await ctx.response.defer()
   result = get_mikuji()
   user_name = ctx.user.display_name
   color_list = [[128,0,128],[25,25,112],[230,230,250],[255,215,0],[192,192,192],[80,200,120],[75,0,130]]
   choice_color = randint(0,6)
   emb = discord.Embed(title='アランマの~~よく当たる~~カオスな占い☆',description=f'ナラ{user_name}の今日の運勢を占う',color=discord.Colour.from_rgb(color_list[choice_color][0],color_list[choice_color][1],color_list[choice_color][2]))
   emb.add_field(name=f'ナラ{user_name}の占い結果',value= f'今日の運勢は「||{result}||」だ！ラッキーカラーは{await aim.generate_mikuji(result,generator)}')
   await ctx.followup.send(embed = emb)

#--------------
#admin commands
#--------------

@tree.command(name='wlist',description='開いているサーバーのホワイトリストにユーザーを追加します(admin)')
@app_commands.default_permissions(administrator=True)
async def wlist(ctx: discord.Interaction, mc_id: str):
   result = serverrcon(f"/whitelist add {mc_id}",False)
   if result == 0:
      text = f"ユーザー：{mc_id}をホワイトリストに追加しました"
   else:
      text = result
   await ctx.response.send_message(text)

@tree.command(name='timeset',description='開いているサーバーの時間を変更します(admin)')
@app_commands.default_permissions(administrator=True)
async def timeset(ctx: discord.Interaction, time: str):
   result = serverrcon(f"time set {time}",False)
   if result == 0:
      text = f"サーバー内時間を{time}に変更しました"
   else:
      text = result
   await ctx.response.send_message(text)

@tree.command(name='reqlist',description='check list of requests(admin)')
@app_commands.default_permissions(administrator=True)
async def reqlist(ctx: discord.Interaction):
   ids = readcsv()
   await ctx.response.send_message(f'現在リクエスト処理待ちのリストです\n{ids}')

@tree.command(name='opereq',description='operation requests(admin)')
@app_commands.default_permissions(administrator=True)
async def opereq(ctx:discord.Interaction, target: int, permit: bool):
   response = operatecsv(target,permit)
   await ctx.response.send_message(response)

@tree.command(name='stopbot',description='aranmabot will stop')
@app_commands.default_permissions(administrator=True)
async def stopbot(ctx: discord.Interaction):
   await ctx.response.send_message("アランマbotを停止します")
   await bot.close()

#---------------
#voice commands
#---------------
@tree.command(name = 'join',description = '使用者のいるvcに参加するぞ')
async def join(ctx: discord.Interaction, mention: bool):
   if ctx.user.voice is None or ctx.user.voice.channel is None:
      await ctx.response.send_message(f'ナラ{ctx.user.display_name}、まずvcに参加するんだ')
      
   join_ch[ctx.guild_id] = ctx.user.voice.channel
   rd_ch[ctx.guild_id] = ctx.channel.id
   #print(rdch)
   vc_cl[ctx.guild_id] = await join_ch[ctx.guild_id].connect()
   if mention:
      await ctx.response.send_message(f'<@&[mention id]> ナラ{ctx.user.display_name}が始めたぞ')
   else:
      await ctx.response.send_message(f'ナラ{ctx.user.display_name}が始めたぞ')

# reading

@bot.event
async def on_message(message):
   if message.author.bot:
      return
   
   guild_id = message.guild.id
   ch_id = message.channel.id
   
   if (guild_id in rd_ch and ch_id == rd_ch[guild_id]) and (guild_id in join_ch):
      #print(message.content)
      #await message.channel.send(message.content)
      try:
            text = aimod.replace(message.content)
            
            if len(text) > 30:
               text = f'{text[:30]},以下略'
            output = await asyncio.to_thread(aimod.gen_voice,888753760, text)
            #print(output)
            if output == 0:
               #print('return:success')
               file_path = os.path.join(os.path.dirname(__file__), 'voices', 'output.wav')
               audio = discord.FFmpegPCMAudio(file_path) #ffmpegのインストール必須
               vc_cl[guild_id].play(audio)
               while vc_cl[guild_id].is_playing():
                  await asyncio.sleep(1)
               os.remove(file_path)
            else:
               #print('return: failed')
               await message.channel.send(output)
      except Exception as e:
            await message.channel.send(e)

@bot.event
async def on_voice_state_update(member,before,after):
   guild_id = member.guild.id
   if member.bot or guild_id not in join_ch:
      return
   
   
   if guild_id in join_ch:
      if(before.channel is None and after.channel is not None):
            text = f'{member.display_name}が参加しました'
            #print('join')
      elif(before.channel is not None and after.channel is None):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
               del join_ch[guild_id]
               del rd_ch[guild_id]
               del vc_cl[guild_id]
               await member.guild.voice_client.disconnect()
               return
            else:
               text = f'{member.display_name}が退出しました'
               print('leave')
      elif(before.channel != after.channel):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
               del join_ch[guild_id]
               del rd_ch[guild_id]
               del vc_cl[guild_id]
               await member.guild.voice_client.disconnect()
               return
            else:
               text = f'{member.display_name}が退出しました'
               print('move')
      try:
            output = await asyncio.to_thread(aimod.gen_voice,888753760, text)
            #print(output)
            if output == 0:
               #print('return:success')
               file_path = os.path.join(os.path.dirname(__file__), 'voices', 'output.wav')
               audio = discord.FFmpegPCMAudio(file_path) #ffmpegのインストール必須
               vc_cl[guild_id].play(audio)
               while vc_cl[guild_id].is_playing():
                  await asyncio.sleep(1)
               os.remove(file_path)
            else:
               print('return: failed')
      except Exception as e:
            print(e)

@tree.command(name = 'leave',description = 'vcから退出するぞ')
async def leave(ctx: discord.Interaction):
   vc_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)
   if vc_client is None:
      await ctx.response.send_message(f'ナラ{ctx.user.display_name}、アランマは入ってない')
      return
   
   del join_ch[ctx.guild_id]
   del rd_ch[ctx.guild_id]
   del vc_cl[ctx.guild_id]

   await vc_client.disconnect()
   await ctx.response.send_message('ばいばい')

#-------------
#test commands
#-------------



#bot run
bot.run(BT)