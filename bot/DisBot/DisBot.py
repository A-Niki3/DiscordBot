import discord
from discord import app_commands as dac
import asyncio
import os

# user
import DisBotModule as dbm

TOKEN = 'Your TOKEN here' #それぞれのTOKENを貼り付ける

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True
bot = discord.Client(intents = intents)
tree = dac.CommandTree(bot)

rdch = {}
join_ch = {}
vc_cl = {}

@bot.event
async def on_ready():
    print('Bot 起動') #デバッグ用メッセージ
    activity = 'activity' #アクティビティメッセージ 「○○をプレイ中」の○○に当たる
    await bot.change_presence(activity = discord.Game(activity)) #アクティビティを変更
    
    await tree.sync() #コマンドのツリーを有効化する
    

#--------------
# bot command
#--------------

#@tree.command(name = 'hello',description='Hello World!を出力するよ')
#async def hello(ctx: discord.Interaction):
#    await ctx.response.send_message('Hello World!')

@tree.command(name = 'hello',description='コマンドの使用者に挨拶をするよ')
async def hello(ctx: discord.Interaction):
    user = ctx.user.display_name
    await ctx.response.send_message(f'Hello {user}!')

@tree.command(name = 'stop',description='botのプログラムを終了します')
@dac.default_permissions(administrator=True)
async def stop(ctx: discord.Interaction):
    await ctx.response.send_message('停止します')
    await bot.close()

@tree.command(name = 'omikuji',description = 'おみくじ')
async def omikuji(ctx: discord.Interaction):
    user = ctx.user.display_name
    await ctx.response.send_message(f'{user} さんの運勢は{dbm.get_mikuji()}')

@tree.command(name = 'echo',description = 'オウム返しするコマンド')
async def echo(ctx: discord.Interaction, message: str):
    user = ctx.user.display_name
    await ctx.response.send_message(f'{user}:「{message}」')

@tree.command(name = 'simpledice',description = '六面ダイスを一回振ります')
async def simple_dice(ctx: discord.Interaction):
    await ctx.response.send_message(f'{dbm.get_simple_dice()}')

@tree.command(name = 'ndice',description = 'n面ダイスを一回振ります')
async def n_dice(ctx: discord.Interaction, roll: int):
    await ctx.response.send_message(f'{dbm.get_n_dice(roll)}')

@tree.command(name = 'dices',description = 'n面ダイスをm回振ります')
async def dices(ctx: discord.Interaction, dice: int, roll: int):
    results = []
    for i in range(dice):
        results.append(dbm.get_n_dice(roll))
    await ctx.response.send_message(f'{results}')

@tree.command(name = 'dicechoice',description = 'よく使われるダイスのコマンド')
@dac.choices(
    dice = [
        dac.Choice(name = '1D', value = 1),
        dac.Choice(name = '2D', value = 2),
        dac.Choice(name = '3D', value = 3)
        # 選択肢の上限はあるため基本的に10個を目途にした方がよい
        # dac.Choice(name = 'nD', value = n),
    ],
    roll = [
        dac.Choice(name = '6', value = 6),
        dac.Choice(name = '20', value = 20),
        dac.Choice(name = '100', value = 100)
    ]
)
async def dice_choice(ctx: discord.Interaction, dice: int, roll: int):
    results = []
    for i in range(dice):
        results.append(dbm.get_n_dice(roll))
    await ctx.response.send_message(f'{results}')

@tree.command(name = 'embedice',description = '埋め込みで少し装飾した百面ダイス')
async def embedice(ctx: discord.Interaction):
    result = dbm.get_n_dice(100)
    user = ctx.user.display_name
    
    emb = discord.Embed(title = f'{user}のダイス結果', description = f'{user}が振った1D100の結果は...')
    emb.add_field(name = '出目', value = f'__**{result}**__', inline = False)
    emb.set_image(url = 'https://illustkun.com/wp-content/uploads/illustkun-03419-dice.png')
    
    await ctx.response.send_message(embed = emb)

# vc commands

@tree.command(name = 'join',description = '使用者のいるvcに参加')
async def join(ctx: discord.Interaction):
    if ctx.user.voice is None or ctx.user.voice.channel is None:
        await ctx.response.send_message('vcに参加してください')
        
    join_ch[ctx.guild_id] = ctx.user.voice.channel
    rdch[ctx.guild_id] = ctx.channel.id
    #print(rdch)
    vc_cl[ctx.guild_id] = await join_ch[ctx.guild_id].connect()
    await ctx.response.send_message(f'{join_ch[ctx.guild_id].name}に参加しました')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    guild_id = message.guild.id
    ch_id = message.channel.id
    
    if (guild_id in rdch and ch_id == rdch[guild_id]) and (guild_id in join_ch):
        #print(message.content)
        #await message.channel.send(message.content)
        try:
            text = message.content
            text = dbm.replace_mentions(text)
            
            if len(text) > 30:
                text = f'{text[:30]},以下略'
            output = await asyncio.to_thread(dbm.gen_voice,888753760, text)
            #print(output)
            if output == 0:
                #print('return:success')
                file_path = os.path.join(os.path.dirname(__file__), 'voices', 'output.wav')
                audio = discord.FFmpegPCMAudio(file_path) #ffmpegのインストール&環境パス設定必須
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
    if member.bot:
        return
    
    guild_id = member.guild.id
    if guild_id in join_ch:
        if(before.channel is None and after.channel is not None):
            text = f'{member.display_name}が参加しました'
            #print('join')
        elif(before.channel != after.channel):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
                await member.guild.voice_client.disconnect()
                return
            #else:
                #print('move')
        elif(before.channel is not None and after.channel is None):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
                await member.guild.voice_client.disconnect()
                return
            else:
                text = f'{member.display_name}が退出しました'
                #print('leave')
        try:
            output = await asyncio.to_thread(dbm.gen_voice,888753760, text)
            #print(output)
            if output == 0:
                #print('return:success')
                file_path = os.path.join(os.path.dirname(__file__), 'voices', 'output.wav')
                audio = discord.FFmpegPCMAudio(file_path) 
                vc_cl[guild_id].play(audio)
                while vc_cl[guild_id].is_playing():
                    await asyncio.sleep(1)
                os.remove(file_path)
            else:
                print('return: failed')
        except Exception as e:
            print(e)

@tree.command(name = 'leave',description = 'vcから退出')
async def leave(ctx: discord.Interaction):
    vc_client = discord.utils.get(bot.voice_clients, guild = ctx.guild)
    if vc_client is None:
        await ctx.response.send_message('入ってないよ')
        return
    
    del join_ch[ctx.guild_id]
    del rdch[ctx.guild_id]
    del vc_cl[ctx.guild_id]
    
    await vc_client.disconnect()
    await ctx.response.send_message('ばいばい')

#pipでPyNaClが必要

bot.run(TOKEN) #botを起動
