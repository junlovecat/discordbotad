import discord,requests,json,urllib,re,wikipedia,time
from discord.ext import commands
from pytube import YouTube
from googlesearch import search as searcher
from flask import Flask
from threading import Thread
app=Flask('')
app.route('/')
client=commands.Bot(command_prefix='!',help_command=None,description='An ADOFAI.GG API USING BOT')
lang=dict()
korfile=open('kor.json','r',encoding='UTF8')
kor=json.loads(korfile.read())
korfile.close()
engfile=open('eng.json','r',encoding='UTF8')
eng=json.loads(engfile.read())
engfile.close()
warned=[]
def nolang(ctx):
    if(lang.get(ctx.channel.guild.id)==None):
        lang[int(ctx.channel.guild.id)]='eng'
    return lang[int(ctx.channel.guild.id)]

def wiki_summary(arg):
    definition=wikipedia.summary(arg,sentences=3,chars=1000,
    auto_suggest=False,redirect=True)
    return definition

def format_number(number):
    return '{:,d}'.format(number)

def checkwarn(member):
    f=open('blacklist.txt','r',encoding='UTF8')
    for x in f.readlines():
        if int(x[:-1])==int(member):
            return True
    f.close()
    return False

def writewarn(member):
    f=open('blacklist.txt','w',encoding='UTF8')
    f.write(f'{member}\n')
    f.close()

@client.event
async def on_ready():
    print('online and Ready')

@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('The Language is automatically set to English.\nAnybody may change the language by !setlang.')
        break
    lang[int(channel.guild.id)]='eng'

@client.event
async def on_command_error(ctx,error):
    if(nolang(ctx)=='eng'):erroroccur=eng["error_occur"]
    elif(nolang(ctx)=='kor'):erroroccur=kor["error_occur"]
    await ctx.send(erroroccur)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('`Error: Missing required arguments`')
    elif isinstance(error,commands.CommandNotFound):
        await ctx.send('`Error: Command not found`')
    elif isinstance(error,commands.MemberNotFound):
        await ctx.send('`Error: Member not found`')
    else:
        await ctx.send(str(error))

@client.command()
@commands.has_permissions(manage_messages=True)
async def setlang(ctx,language):
    if language=='list':
        await ctx.send('eng // kor\nWill be updated soon.')
        return
    if language=='eng':lang[int(ctx.channel.guild.id)]='eng'
    elif language=='kor':lang[int(ctx.channel.guild.id)]='kor'
    else:lang[int(ctx.channel.guild.id)]='eng'
    await ctx.send(f'Language Set To: English' if lang[int(ctx.channel.guild.id)]=='eng' else 'Language Set To: Korean')

@client.command()
async def find(ctx,query):
    if(nolang(ctx)=='eng'):
        await ctx.send(eng["wait"])
        notfound=eng["levelnotfound"]
        manykind=eng["manykindoflevel"]
    elif(nolang(ctx)=='kor'):
        await ctx.send(kor["wait"])
        notfound=kor["levelnotfound"]
        manykind=kor["manykindoflevel"]
    params={'offset':'0','amount':'25','query':query}
    response=requests.get(
        "https://api.adofai.gg:9200/api/v1/levels",
        params=params,
        verify=False
    ).text
    e=json.loads(str(response))
    if(len(e['results'])==0):
        await ctx.send(notfound)
    elif(len(e['results'])==1):
        info=e['results'][0]
        embed=discord.Embed(
            title=f"{', '.join(list(info['artists']))} - {info['title']}",
            url='https://adofai.gg/levels/'+str(info['id']),
            description=f"Level by {', '.join(list(info['creators']))}",
            color=discord.Color.blue()
        )
        embed.add_field(name='Level',value=info['difficulty'],inline=True)
        embed.add_field(name='BPM',value=str((int(info['minBpm'])+int(info['maxBpm']))/2),inline=True)
        embed.add_field(name='Tiles',value=str(info['tiles']),inline=True)
        embed.add_field(name='EpilepsyWarning',value=info['epilepsyWarning'],inline=True)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)
        download=str(info['download'])
        video=str(info['video'])
        workshop=str(info['workshop'])
        download=download if download else 'Not Found'
        video=video if video else 'Not Found'
        workshop=workshop if workshop else 'Not Found'
        embed=discord.Embed(
            title='',
            description='',
            color=discord.Color.gold()
        )
        embed.add_field(name='Video',value=video,inline=False)
        embed.add_field(name='Download',value=download,inline=False)
        embed.add_field(name='Workshop',value=workshop,inline=False)
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(
            title=manykind,
            description='',
            color=discord.Color.red()
        )
        for x in range(len(e['results']) if len(e['results'])<=10 else 10):
            embed.add_field(name=e['results'][x]['id'],value=e['results'][x]['title'],inline=True)
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)

@client.command()
async def id(ctx,query):
    if(nolang(ctx)=='eng'):
        await ctx.send(eng["wait"])
    elif(nolang(ctx)=='kor'):
        await ctx.send(kor["wait"])
    response=requests.get(
        f"https://api.adofai.gg:9200/api/v1/levels/{query}",
        verify=False
    ).text
    info=json.loads(str(response))
    embed=discord.Embed(
        title=f"{', '.join(list(info['artists']))} - {info['title']}",
        url='https://adofai.gg/levels/'+str(info['id']),
        description=f"Level by {', '.join(list(info['creators']))}",
        color=discord.Color.blue()
    )
    embed.add_field(name='Level',value=info['difficulty'],inline=True)
    embed.add_field(name='BPM',value=str((int(info['minBpm'])+int(info['maxBpm']))/2),inline=True)
    embed.add_field(name='Tiles',value=str(info['tiles']),inline=True)
    embed.add_field(name='EpilepsyWarning',value=info['epilepsyWarning'],inline=True)
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)
    download=str(info['download'])
    video=str(info['video'])
    workshop=str(info['workshop'])
    download=download if download else 'Not Found'
    video=video if video else 'Not Found'
    workshop=workshop if workshop else 'Not Found'
    embed=discord.Embed(
        title='',
        description='',
        color=discord.Color.gold()
    )
    embed.add_field(name='Video',value=video,inline=False)
    embed.add_field(name='Download',value=download,inline=False)
    embed.add_field(name='Workshop',value=workshop,inline=False)
    await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx,amount:int):
    await ctx.channel.purge(limit=amount)
    await ctx.channel.purge(limit=1)

@client.command()
async def invite(ctx):
    if(nolang(ctx)=='eng'):
        clicker=eng["clickthislink"]
    elif(nolang(ctx)=='kor'):
        clicker=kor["clickthislink"]
    embed = discord.Embed(
        title="Link",
        url="https://discord.com/oauth2/authorize?client_id=916542890627440650&scope=bot&permissions=1099511627775", 
        description=clicker, 
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@client.command() 
async def ping(ctx):
    if(nolang(ctx)=='eng'):
        pingresult=eng["pingresult"]
        pingms=eng["pingms"]
        pings=eng["pings"]
    elif(nolang(ctx)=='kor'):
        pingresult=kor["pingresult"]
        pingms=kor["pingms"]
        pings=kor["pings"]
    embed=discord.Embed(
        title=pingresult,
        description=None,
        color=discord.Color.dark_gray()
    )
    embed.add_field(name=pingms,value=round(client.latency*1000),inline=False)
    embed.add_field(name=pings,value=round(client.latency),inline=False)
    await ctx.send(embed=embed)

@client.command()
async def video(ctx,*,code):
    if(nolang(ctx)=='eng'):
        author=eng["youtubeauthor"]
        views=eng["youtubeviews"]
        length=eng["youtubelength"]
        rating=eng["youtuberating"]
    elif(nolang(ctx)=='kor'):
        author=kor["youtubeauthor"]
        views=kor["youtubeviews"]
        length=kor["youtubelength"]
        rating=kor["youtuberating"]
    link='https://youtu.be/'+code
    yt=YouTube(link)
    embed=discord.Embed(
        title=yt.title,
        description=yt.description[:60]+'...',
        color=discord.Color.red()
    )
    minsec=str(int(yt.length/60))+" MIN "+str(int(yt.length%60))+' SEC'
    embed.set_thumbnail(url=yt.thumbnail_url)
    embed.add_field(name=author,value=yt.author,inline=True)
    embed.add_field(name=views, value=yt.views, inline=True)
    embed.add_field(name=length,value=minsec,inline=True)
    embed.add_field(name=rating,value=yt.rating*2,inline=True)
    await ctx.send(embed=embed)

@client.command()
async def youtube(ctx, *, search):
    if(nolang(ctx)=='eng'):
        author=eng["youtubeauthor"]
        views=eng["youtubeviews"]
        length=eng["youtubelength"]
        rating=eng["youtuberating"]
    elif(nolang(ctx)=='kor'):
        author=kor["youtubeauthor"]
        views=kor["youtubeviews"]
        length=kor["youtubelength"]
        rating=kor["youtuberating"]
    query_string=urllib.parse.urlencode({'search_query':search})
    htm_content = urllib.request.urlopen('http://www.youtube.com/results?'+query_string)
    search_results=re.findall( r"watch\?v=(\S{11})", htm_content.read().decode())
    for x in range(0,3):
        link='https://youtu.be/'+search_results[x]
        yt = YouTube(link)
        embed=discord.Embed(
            title=yt.title,
            description=yt.description[:60]+'...',
            color=discord.Color.red()
        )
        minsec=str(int(yt.length/60))+' MIN '+str(int(yt.length%60))+' SEC'
        embed.set_thumbnail(url=yt.thumbnail_url)
        embed.add_field(name=author,value=yt.author,inline=True)
        embed.add_field(name=views, value=yt.views, inline=True)
        embed.add_field(name=length,value=minsec,inline=True)
        embed.add_field(name=rating,value=yt.rating*2,inline=True)
        await ctx.send(embed=embed)

@client.command()
async def wiki(ctx, question):
    search=discord.Embed(
        title='Searching...',
        description=wiki_summary(question),
        color=discord.Color.dark_gray()
    )
    await ctx.send(content=None,embed=search)

@client.command()
async def google(ctx,*,query):
    if(nolang(ctx)=='eng'):
        googlefrom=eng["googlefrom"]
    elif(nolang(ctx)=='kor'):
        googlefrom=kor["googlefrom"]
    embed=discord.Embed(
        title=str(query),
        description=googlefrom,
        color=discord.Color.blue()
    )
    i=1
    for j in searcher(query,tld="co.kr",num=5,stop=5,pause=2):
        embed.add_field(name=str(i),value=str(j),inline=False)
        i=i+1
    await ctx.send(embed=embed)

@client.command()
async def corona(ctx):
    if(nolang(ctx)=='eng'):
        coronaglobalcoronadata=eng["coronaglobalcoronadata"]
        coronacases=eng["coronacases"]
        coronatodaycases=eng["coronatodaycases"]
        coronadeaths=eng["coronadeaths"]
        coronarecovered=eng["coronarecovered"]
        coronaactive=eng["coronanotrecovered"]
        coronacountry=eng["coronacountry"]
    elif(nolang(ctx)=='kor'):
        coronaglobalcoronadata=kor["coronaglobalcoronadata"]
        coronacases=kor["coronacases"]
        coronatodaycases=kor["coronatodaycases"]
        coronadeaths=kor["coronadeaths"]
        coronarecovered=kor["coronarecovered"]
        coronaactive=kor["coronanotrecovered"]
        coronacountry=kor["coronacountry"]
    global_data_url="https://corona.lmao.ninja/v3/covid-19/all"
    res=requests.get(global_data_url).text
    country_corona_info=json.loads(res)
    embed=discord.Embed(
        title=coronaglobalcoronadata,
        description=str(time.strftime('%c', time.localtime(time.time()))),
        color=discord.Color.blue()
    )
    embed.add_field(name=coronacases,value=str(format_number(country_corona_info["cases"])),inline=True)
    embed.add_field(name=coronatodaycases,value=str(format_number(country_corona_info["todayCases"])),inline=True)
    embed.add_field(name=coronadeaths,value=str(format_number(country_corona_info["deaths"])),inline=True)
    embed.add_field(name=coronarecovered,value=str(format_number(country_corona_info["recovered"])),inline=True)
    embed.add_field(name=coronaactive,value=str(format_number(country_corona_info["active"])),inline=True)
    embed.add_field(name=coronacountry,value=str(format_number(country_corona_info["affectedCountries"])),inline=True)
    await ctx.send(embed=embed)

@client.command()
async def nation(ctx,*,nara):
    if(nolang(ctx)=='eng'):
        coronanationdata=eng["coronaglobalcoronadata"]
        nationnation=eng["nationnation"]
        coronatodaycases=eng["coronatodaycases"]
        coronadeaths=eng["coronadeaths"]
        coronarecovered=eng["coronarecovered"]
        coronaactive=eng["coronanotrecovered"]
        nationtodaydeaths=eng["nationtodaydeaths"]
        coronacases=eng["coronacases"]
    elif(nolang(ctx)=='kor'):
        coronanationdata=kor["coronaglobalcoronadata"]
        nationnation=kor["nationnation"]
        coronatodaycases=kor["coronatodaycases"]
        coronadeaths=kor["coronadeaths"]
        coronarecovered=kor["coronarecovered"]
        coronaactive=kor["coronanotrecovered"]
        nationtodaydeaths=kor["nationtodaydeaths"]
        coronacases=kor["coronacases"]
    try:
        country_data_url = "https://corona.lmao.ninja/v3/covid-19/countries/"+nara
        res = requests.get(country_data_url).text
        country_corona_info = json.loads(res)
        embed=discord.Embed(
            title=f'{nara} {coronanationdata}',
            description=str(time.strftime('%c', time.localtime(time.time()))),
            color=discord.Color.blue()
        )
        embed.add_field(name=nationnation,value=nara,inline=True)
        embed.add_field(name=coronatodaycases, value=str(format_number(country_corona_info["todayCases"])), inline=True)
        embed.add_field(name=nationtodaydeaths,value=str(format_number(country_corona_info["todayDeaths"])),inline=True)
        embed.add_field(name=coronacases,value=str(format_number(country_corona_info["cases"])),inline=True)
        embed.add_field(name=coronadeaths,value=str(format_number(country_corona_info["deaths"])),inline=True)
        embed.add_field(name=coronarecovered,value=str(format_number(country_corona_info["recovered"])),inline=True)
        embed.add_field(name=coronaactive,value=str(format_number(country_corona_info["active"])),inline=True)
        await ctx.send(embed=embed)
    except:
        await ctx.send('오류 발생:')
        await ctx.send(f'`no such data found as {nara}`')

@client.command()
async def cbs(ctx):
    if(nolang(ctx)=='eng'):
        cbstitle=eng["cbstitle"]
        cbsdesc=eng["cbsdesc"]
    elif(nolang(ctx)=='kor'):
        cbstitle=kor["cbstitle"]
        cbsdesc=kor["cbsdesc"]
    cbslink="http://m.safekorea.go.kr/idsiSFK/neo/ext/json/disasterDataList/disasterDataList.json"
    res=requests.get(cbslink).text
    data=json.loads(res)
    embed=discord.Embed(
        title=cbstitle,
        description=cbsdesc,
        color=discord.Color.blue()
    )
    for i in data[:13]:
        embed.add_field(name=i["SJ"],value=i["CONT"],inline=False)
    await ctx.send(embed=embed)

@client.command()
async def hangang(ctx):
    data_url='http://hangang.dkserver.wo.tc/'
    res=requests.get(data_url).text
    info=json.loads(res)
    await ctx.send(f'{info["temp"]} °C')

@client.command()
async def kick(ctx,member:discord.Member,*,reason=None):
    await member.kick(reason=reason)
    await ctx.channel.purge(limit=1)

@client.command(pass_context=True)
async def warn(ctx,user_name:discord.Member):
    if(nolang(ctx)=='eng'):
        warnedtxt=eng["warnedtxt"]
    elif(nolang(ctx)=='kor'):
        warnedtxt=kor["warnedtxt"]
    if checkwarn(str(user_name)):
        await user_name.kick(reason='You have been warned before.')
    else:
        channel=await user_name.create_dm()
        await channel.send(warnedtxt)
        writewarn(str(user_name))

@client.command()
@commands.has_permissions(manage_messages=True)
async def send(ctx,*,arg):
    await ctx.channel.purge(limit=1)
    await ctx.send('@everyone '+arg)

@client.command()
async def help(ctx):
    if(nolang(ctx)=='eng'):
        helpmessage=eng["help"]
    elif(nolang(ctx)=='kor'):
        helpmessage=kor["help"]
    channel=await ctx.author.create_dm()
    await channel.send(helpmessage)

@client.command()
async def report(ctx):
    try:
        await ctx.send('What is the problem? Give us the specific problem about you experienced.')
        msg=await client.wait_for("message", timeout=30)
        f=open('report.txt','w')
        f.write(f'{str(ctx.author)} - {time.strftime("%c", time.localtime(time.time()))} : {msg.content}\n')
        f.close()
    except:
        pass
def main():
    return "Your bot is alive!"
def keep_alive():
    server = Thread(target=run)
    server.start()
def run():
    app.run(host="0.0.0.0", port=8080)
keep_alive()
client.run('wasans',bot=True,reconnect=True)
