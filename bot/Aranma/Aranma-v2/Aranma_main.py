import discord
from discord import app_commands as dac
import os
from dotenv import load_dotenv
import asyncio

#user modules
import Aranma_Modules as amod

# get env
load_dotenv()

# bot token
TOKEN = os.getenv("TOKEN")

# mcrcon
server_info = [os.getenv("HOST"),os.getenv("PASS"),os.getenv("PORT")]

# guild id
myserver_ids = [int(os.getenv("V_SERVER_ID")),int(os.getenv("D_SERVER_ID"))]

# dev id (niki & kazuki)
dev_user_id = [int(os.getenv("NIKI_ID")),int(os.getenv("KAZUKI_ID"))]

# set AI model
async_loop = asyncio.get_event_loop()
generator = async_loop.run_until_complete(amod.set_generator())
generator.model.config.seed = None

# bot setup
intents = amod.set_intents(discord.Intents.default())
bot = discord.Client(intents = intents)
tree = dac.CommandTree(bot)

# for vc dict
rdch = {} # read channel
joch = {} # join channel
vccl = {} # VC Client
gque = {} # guild queue

# failed mesage
failed = 'このコマンドの実行権限がありません'

# bot boot
@bot.event
async def on_ready():
    print('アランマbot起動')
    activity = '森林の浄化'
    await bot.change_presence(activity = discord.Game(activity))

    await tree.sync()

#---------------
# bot commands
#---------------

@tree.command(name='hello',description='アランマが返事をしてくれるよ！')
async def test(ctx: discord.Interaction):
    await ctx.response.send_message(f"ナラ{ctx.user.display_name}元気か?")

@tree.command(name='mcmsg',description='開いているマイクラ鯖にメッセージを送れるよ！')
async def rcon_message(ctx: discord.Interaction, message: str):
    msg = f"msg @a from §9Discord:§a{ctx.user.display_name}§f：{message}"
    result = amod.server_rcon(msg,False,server_info)
    if result == 0:
        text = f"from Discord:{ctx.user.display_name}:{message}"
    else:
        text = result
    await ctx.response.send_message(text)

@tree.command(name='list',description='鯖にログインしている人数を調べるよ！')
async def plcnt(ctx: discord.Interaction):
    result = amod.server_rcon("list",True,server_info)
    await ctx.response.send_message(result)

@tree.command(name='ggrks',description='Google検索できるよ!')
async def ggrks(ctx: discord.Interaction,word: str):
    await ctx.response.send_message(f'https://www.google.com/search?q={word}')

@tree.command(name='seed',description='起動しているマイクラサーバーのワールドseedを調べます')
async def getseed(ctx: discord.Interaction):
    result = amod.server_rcon("seed",True,server_info)
    await ctx.response.send_message(f"{result}")

@tree.command(name='slimech',description='slimefinderで検索できるよ')
async def ggrks(ctx: discord.Interaction,seed: str,x: int,z: int):
    url = f'https://www.chunkbase.com/apps/slime-finder#seed={seed}&platform=java&x={x}&z={z}&zoom=1'
    await ctx.response.send_message(url)

@tree.command(name='reqjoin',description='マイクラ鯖への参加申請')
async def reqjoin(ctx: discord.Interaction,mcid: str):
    if ctx.guild_id in myserver_ids:
        dev_id = await bot.fetch_user(dev_user_id[0])
        amod.addcsv(mcid)
        await dev_id.send(f'New join request add request.csv\nServer name:{ctx.user.display_name}\nmcid:{mcid}')
        await ctx.response.send_message(f'mcid:{mcid}で申請しました。')
    else:
        await ctx.response.send_message(failed)

@tree.command(name='bks',description='みんなで踊ろう')
async def bks(ctx: discord.Interaction):
    await ctx.response.send_message(f'ナラ{ctx.user.display_name}、大人しく課金した方がいいぞ\nhttps://tenor.com/view/genshin-impact-furina-focalors-hydro-archon-fortnite-gif-6682083727853727725')

@tree.command(name='reboot',description='起動しているマイクラサーバーを再起動させます')
async def reboot(ctx: discord.Interaction):
    guild_id = ctx.guild_id
    if guild_id in myserver_ids:
        #amod.server_rcon("save-all",False,server_info)
        result = amod.server_rcon("stop",False,server_info)
        if result == 0:
            text = "再起動を開始しました。しばらく後に確認してください。"
        else:
            text = result
        await ctx.response.send_message(text)
    else:
        await ctx.response.send_message(failed)

#----------------
#Embed commands
#----------------
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
@dac.describe(prefecture = '都府県をつけずに入力してね(例：東京都→東京)')
async def weather(ctx: discord.Interaction, prefecture: str):
    number = amod.search_prefecture(prefecture)
    if number is not None:
        today_weather = amod.get_weather(number)
        emb = discord.Embed(title='アランマの天気予報☆',description=f'ナラに今日の{prefecture}の天気を教えるよ')
        emb.add_field(name=f'時間:{today_weather[0]}',value=f'今日の{prefecture}は、{today_weather[1]}だ',inline=False)
        emb.add_field(name=f'{prefecture}の最高気温',value=f'{today_weather[2]}℃だ',inline=True)
        emb.add_field(name=f'{prefecture}の最低気温',value=f'{today_weather[3]}℃だ',inline=True)
        await ctx.response.send_message(embed=emb)
    else:
        await ctx.response.send_message(f'{prefecture}は無い。誤字、都道府県がついていないか確認するんだ。')

#------------------------
#Select choice commands
#------------------------
@tree.command(name='dice',description='選択式ダイス')
@dac.choices(
    dice=[
    dac.Choice(name='1',value=1),
    dac.Choice(name='2',value=2),
    dac.Choice(name='3',value=3),
    dac.Choice(name='4',value=4),
    dac.Choice(name='5',value=5),
    dac.Choice(name='6',value=6),
    dac.Choice(name='7',value=7),
    dac.Choice(name='8',value=8),
    dac.Choice(name='9',value=9),
    dac.Choice(name='10',value=10)],
    roll=[
    dac.Choice(name='2',value=2),
    dac.Choice(name='4',value=4),
    dac.Choice(name='6',value=6),
    dac.Choice(name='8',value=8),
    dac.Choice(name='10',value=10),
    dac.Choice(name='12',value=12),
    dac.Choice(name='20',value=20),
    dac.Choice(name='100',value=100),])
async def sel(ctx: discord.Interaction, dice: int, roll: int):
    result = amod.dice_roll(dice,roll)
    await ctx.response.send_message(f'{dice}D{roll}の結果、\n{result}')

#-----------------
#random commands
#-----------------
@tree.command(name='omikuji',description='おみくじが引けるよ(旧式につき非推奨)')
async def mikuji(ctx: discord.Interaction):
    result = amod.get_mikuji()
    await ctx.response.send_message(f'ナラ{ctx.user.display_name}の今日の運勢は{result}だ')

@tree.command(name='freedice',description='自由なダイス(MAX 30D100まで)')
async def free_dice(ctx: discord.Interaction, dice: int, roll: int):
    if dice > 30 or roll > 100:
        await ctx.response.send_message('指定範囲外のダイスはダメだぞ')
    else:
        result = amod.dice_roll(dice,roll)
        await ctx.response.send_message(f'{dice}D{roll}の結果\n{result}')

#-------------
#ai commands
#-------------
@tree.command(name='newomikuji',description='運勢に加えてコメントしてくれるよ！')
async def omikujineo(ctx: discord.Interaction):
    await ctx.response.defer()
    fortune = amod.get_mikuji()
    user_name = ctx.user.display_name
    color_list = [[128,0,128],[25,25,112],[230,230,250],[255,215,0],[192,192,192],[80,200,120],[75,0,130]]
    choice_color = amod.dice_roll(1,7)[0] - 1
    gen_fortune:str = await amod.generate_mikuji(fortune,generator)
    gen_fortune = gen_fortune.replace(f"「{fortune}」",f'「||{fortune}||」')
    emb = discord.Embed(title='アランマの~~よく当たる~~カオスな占い☆',description=f'ナラ{user_name}の今日の運勢を占う',color=discord.Colour.from_rgb(color_list[choice_color][0],color_list[choice_color][1],color_list[choice_color][2]))
    emb.add_field(name=f'ナラ{user_name}の占い結果',value= gen_fortune)
    await ctx.followup.send(embed = emb)

#------------------
# secret commands
#------------------
@tree.command(name='whotel',description='電話番号を調べます(コマンド使用者にしか見えないようになっています)')
async def who_tel(ctx: discord.Interaction, tel: str):
    url = f'https://www.telnavi.jp/phone/{tel}'
    await ctx.response.send_message(f'電話番号:{tel}\n{url}',ephemeral=True)

@tree.command(name='getid',description='ベータ参加時に必要なDiscord IDを取得します')
async def get_dis_user_id(ctx: discord.Interaction):
    await ctx.response.send_message(f'{ctx.user.display_name}のIDは\n```\n{ctx.user.id}```\n',ephemeral=True)


#--------------
#admin commands
#--------------
@tree.command(name='wlist',description='開いているサーバーのホワイトリストにユーザーを追加します(admin)')
@dac.default_permissions(administrator=True)
async def wlist(ctx: discord.Interaction, mc_id: str):
    if ctx.guild_id in myserver_ids:
        result = amod.server_rcon(f"/whitelist add {mc_id}",False,server_info)
        if result == 0:
            text = f"ユーザー：{mc_id}をホワイトリストに追加しました"
        else:
            text = result
        await ctx.response.send_message(text)
    else:
        await ctx.response.send_message(failed)

@tree.command(name='timeset',description='開いているサーバーの時間を変更します(admin)')
@dac.default_permissions(administrator=True)
async def timeset(ctx: discord.Interaction, time: str):
    if ctx.guild_id in myserver_ids:
        result = amod.server_rcon(f"time set {time}",False,server_info)
        if result == 0:
            text = f"サーバー内時間を{time}に変更しました"
        else:
            text = result
        await ctx.response.send_message(text)
    else:
        await ctx.response.send_message(failed)

@tree.command(name='reqlist',description='check list of requests(admin)')
@dac.default_permissions(administrator=True)
async def reqlist(ctx: discord.Interaction):
    if ctx.user.id in dev_user_id:
        ids = amod.readcsv()
        await ctx.response.send_message(f'現在リクエスト処理待ちのリストです\n{ids}')
    else:
        await ctx.response.send_message(failed)

@tree.command(name='opereq',description='operation requests(admin)')
@dac.default_permissions(administrator=True)
async def opereq(ctx:discord.Interaction, target: int, permit: bool):
    if ctx.user.id in dev_user_id:
        response = amod.operatecsv(target,permit,server_info)
        await ctx.response.send_message(response)
    else:
        await ctx.response.send_message(failed)

@tree.command(name='stopbot',description='aranmabot will stop')
@dac.default_permissions(administrator=True)
async def stopbot(ctx: discord.Interaction):
    if ctx.user.id in dev_user_id:
        result = amod.clear_voices()
        if result == 0:
            await ctx.response.send_message("アランマbotを停止します")
            await bot.close()
        else:
            await ctx.response.send_message(f"エラーがおきました\n{result}")
    else:
        await ctx.response.send_message(failed)

@tree.command(name='addbadwords',description='bad-word add to list')
@dac.default_permissions(administrator=True)
async def add_bad(ctx: discord.Interaction,bad_word: str):
    if ctx.user.id in dev_user_id:
        amod.bads_add_to_json([bad_word])
        await ctx.response.send_message(f'\"{bad_word}\"を追加しました')
    else:
        await ctx.response.send_message(failed)

@tree.command(name='delvoices',description='delete voices(admin)')
@dac.default_permissions(administrator=True)
async def delvoices(ctx: discord.Interaction):
    if ctx.user.id in dev_user_id:
        result = amod.clear_voices()
        if result == 0 or result == 1:
            text = ['wavのファイルを全て削除しました','ファイルがありません']
            await ctx.response.send_message(text[result])
        else:
            await ctx.response.send_message(f"エラーがおきました\n{result}")
    else:
        await ctx.response.send_message(failed)

#---------------
#voice commands
#---------------
@tree.command(name = 'join',description = '使用者のいるvcに参加するぞ')
async def join(ctx: discord.Interaction, mention: bool):
    if ctx.user.voice is None or ctx.user.voice.channel is None:
        await ctx.response.send_message(f'ナラ{ctx.user.display_name}、まずvcに参加するんだ')
        
    joch[ctx.guild_id] = ctx.user.voice.channel
    rdch[ctx.guild_id] = ctx.channel.id
    gque[ctx.guild_id] = asyncio.Queue()
    #print(rdch)
    try:
        vccl[ctx.guild_id] = await joch[ctx.guild_id].connect(timeout=60, self_deaf=True, reconnect=True)
    except Exception as e:
        await ctx.response.send_message(f'エラーが発生\n{type(e).__name__}:{e}')
        return
    if mention:
        await ctx.response.send_message(f'<@&1160612794597650444> ナラ{ctx.user.display_name}が始めたぞ')
    else:
        await ctx.response.send_message(f'ナラ{ctx.user.display_name}が始めたぞ')

# reading

@bot.event
async def on_message(message:discord.Message):
    if message.author.bot:
        return
    
    guild_id = message.guild.id
    ch_id = message.channel.id
    
    if (guild_id in rdch and ch_id == rdch[guild_id]) and (guild_id in joch):
        #print(message.content)
        #await message.channel.send(message.content)
        try:
            text = amod.replace(message.content)
            
            if len(text) > 30:
                text = f'{text[:30]},以下略'
            if not text:
                return
            output = await asyncio.to_thread(amod.gen_voice,888753760, text)
            #print(output)
            if output[0] == 0:
                #print('return:success')
                await amod.play_sound(vccl[guild_id],output[1],gque[guild_id])
            else:
                #print('return: failed')
                await message.channel.send(output)
        except Exception as e:
            await message.channel.send('error has occured:',e)
    
    if "おはよう" in message.content or "こんにちは" in message.content or "おやすみ" in message.content:
        if "おはよう" in message.content:
            greet = f"ナラ{message.author.display_name}、おはよう。今日は"
        elif "こんにちは" in message.content:
            greet = f"こんにちは、ナラ{message.author.display_name}。今日は"
        else:
            greet = f"おやすみ、ナラ{message.author.display_name}。今日は"
        greet = await amod.generate_text(greet,generator)
        await message.channel.send(greet)

@bot.event
async def on_voice_state_update(member:discord.Member,before,after):
    guild_id = member.guild.id
    if member.bot or guild_id not in joch:
        return
    
    
    if guild_id in joch and (joch[guild_id] == before.channel or before.channel is None):
        member_name = member.display_name
        if len(member_name) > 13:
            member_name = f'{member_name[:5]},略'
        if(before.channel is None and after.channel is not None):
            text = f'{member_name}が参加しました'
            #print('join')
        elif(before.channel is not None and after.channel is None):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
                del joch[guild_id]
                del rdch[guild_id]
                del vccl[guild_id]
                del gque[guild_id]
                await member.guild.voice_client.disconnect()
                return
            else:
                text = f'{member_name}が退出しました'
                #print('leave')
        elif(before.channel != after.channel):
            fumman = [m for m in member.guild.voice_client.channel.members if not m.bot]
            if len(fumman) == 0:
                del joch[guild_id]
                del rdch[guild_id]
                del vccl[guild_id]
                del gque[guild_id]
                await member.guild.voice_client.disconnect()
                return
            else:
                text = f'{member_name}が退出しました'
                #print('move')
        try:
            output = await asyncio.to_thread(amod.gen_voice,888753760, text)
            #print(output)
            if output[0] == 0:
                #print('return:success')
                await amod.play_sound(vccl[guild_id],output[1],gque[guild_id])
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
    
    del joch[ctx.guild_id]
    del rdch[ctx.guild_id]
    del vccl[ctx.guild_id]
    del gque[ctx.guild_id]

    await vc_client.disconnect()
    await ctx.response.send_message('ばいばい')

#-------------
#test commands
#-------------



# bot run
bot.run(TOKEN)