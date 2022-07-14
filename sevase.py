import discord

from discord.ext import commands
import datetime
from discord.utils import get


PREFIX = '.'
bad_words=['THIS TYPE BAD WORDS FOR U DISCORD']

client = commands.Bot(command_prefix='.')
client.remove_command('help')

@client.event

async def on_ready():
    print('BOT connected...')

    await client.change_presence(status=discord.Status.online, activity=discord.Game('.help'))

@client.event
async def on_command_error(ctx, error):
    pass

# Filter
@client.event
async def on_message(message):
    await client.process_commands(message)

    msg = message.content.lower()

    if msg in bad_words:
        await message.delete()
        await message.author.send(f'{message.author.name}, не стоит такое писать, прочитайте правила, а то получите бан!')

# Clear message
@client.command(pass_context=True)
@commands.has_permissions(administrator=True)

async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)

    await ctx.send(embed=discord.Embed(description=f':white_check_mark: Удалено {amount} сообщений', color=0x0))

# Kick диз
@client.command(pass_context = True)
@commands.has_permissions(administrator=True)

async def kick(ctx, member: discord.Member, *, reason = None):
    await ctx.channel.purge(limit=1)
    await member.kick(reason=reason)

    emb = discord.Embed(title='Информация об изгнании', description=f'{member.name.title()}, был выгнан')

    emb.set_author(name='member', icon_url=member.avatar_url)
    emb.set_footer(text=f'Был изгнан администратором {ctx.message.author.name}', icon_url=ctx.avatar_url)

    await ctx.send(embed=emb)

# Ban СДЕЛАТЬ ПРИЧИНУ
@client.command(pass_context = True)
@commands.has_permissions(administrator=True)

async def ban(ctx, member: discord.Member, *, reason = None):
    emb = discord.Embed(title='Ban', colour=discord.Colour.red())
    await ctx.channel.purge(limit=1)

    await member.ban(reason=reason)

    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name='Ban user', value='Baned user : {}'.format(member.mention))
    emb.set_footer(text='Был забанен администратором {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb)

# Unban диз
@client.command(pass_context = True)
@commands.has_permissions(administrator=True)

async def unban(ctx, *, member):
    await ctx.channel.purge(limit=1)

    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user

        await ctx.guild.unban(user)
        await ctx.send(f'Unbanned user {user.mention}')

        return

# Command help
@client.command(pass_context = True)

async def help(ctx):
    await ctx.channel.purge(limit=1)
    emb = discord.Embed(title='Навигация по командам')

    emb.add_field(name='{}clear'.format(PREFIX), value='Очистка чата')
    emb.add_field(name='{}kick'.format(PREFIX), value='Удаление участника с сервера')
    emb.add_field(name='{}ban'.format(PREFIX), value='Ограничение доступа к серверу (БАН)')
    emb.add_field(name='{}unban'.format(PREFIX), value='Убирает из бана человека')
    emb.add_field(name='{}time'.format(PREFIX), value='Узнать время')
    emb.add_field(name='{}mute'.format(PREFIX), value='Замутить человека. Не сможет писать в чатах')

    await ctx.send(embed=emb)

#time
@client.command(pass_context = True)

async def time(ctx):
    emb = discord.Embed(title='Время по МСК', description='Вы сможете узнать текущее время', colour=discord.Color.random(), url='https://www.timeserver.ru/cities/ru/moscow')

    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    emb.set_footer(text='Спасибо за использование бота-"sevase"', icon_url=ctx.author.avatar_url)
    #emb.set_image(url='https://klike.net/uploads/posts/2021-11/1635926535_2.jpg')
    emb.set_thumbnail(url='https://klike.net/uploads/posts/2021-11/1635926535_2.jpg')

    now_date = datetime.datetime.now()

    emb.add_field(name='Time', value='Time : {}'.format(now_date))

    await ctx.send(embed=emb)


#mute диз
@client.command()
@commands.has_permissions(administrator=True)

async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)

    mute = discord.utils.get(ctx.message.guild.roles, name='mute')

    await member.add_roles(mute)
    await ctx.send(f'У{member.mention}, ограничение чата, за нарушение прав!' )


# Micro
@client.command()
async def join(ctx):
    global voice
    channel=ctx.message.author.voice.channel
    voice=get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice=await channel.connect()
        await ctx.send(f'Бот присоеденился к каналу:{channel}')
@client.command()
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f'Бот отключился от канала:{channel}')


#errors
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите аргумент!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')
@kick.error
async def kick(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, вам стоило бы указать персону, которую вы хотите кикнуть')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')
@ban.error
async def ban(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, вам стоило бы указать персону, которую вы хотите забанить')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас не достаточно прав')
@unban.error
async def unban(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, вам стоило бы указать персону, которую вы хотите разбанить')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас не достаточно прав')
@mute.error
async def mute(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, вам стоило бы указать персону, которую вы хотите замутить')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас не достаточно прав')

# Connect
token = open('token.txt', 'r').readline()

client.run(token)




