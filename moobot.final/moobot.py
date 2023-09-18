def main():
    import os
    import discord
    import time
    import asyncio
    import youtube_dl
    import discord
    import random
    import json
    import shelve
    from discord.utils import get
    from datetime import datetime
    from dotenv import load_dotenv
    from discord.ext import commands
    from discord.ext import tasks

    load_dotenv()
    TOKEN = os.getenv('TEST_TOKEN')
    CHANNEL_ID = 1070627601607053342
    WELCOMING_ID = 1070627601607053342
    MOO_CITY_ID = 1070627601607053342

    # Command-Prefix:
    bot = commands.Bot(command_prefix= 'm.', intents= discord.Intents.all())

    
        

    # Help command:
    bot.remove_command("help")
    @bot.command(name= "help")
    async def help_commands(ctx):
        await ctx.send("*Music Bot*:\nmoo.music.play <Youtube URL>:      Play music\nmoo.music.add <Youtube URL>:      Add music to the queue\nmoo.music.next:     Skip to the next song\nmoo.music.back:      Go back to the previous song\nmoo.music.pause:      Pause the currently playing song\nmoo.music.resume:      Resume the currently playing song\nmoo.music.leave:      Disconnect the bot and stop playing music")

    # Greet new member:
    @bot.event
    async def on_member_join(member):
        channel = bot.get_channel(WELCOMING_ID)
        await channel.send(f'MoOoOoOoOoO {member.mention} !!!')
        await member.send(f'Welcome to MOO!')
        


    ''' Ticket System '''
    class button_view(discord.ui.View):
         def __init__(self):
            super().__init__(timeout= None)
            self.value = None

    # Create a Ticket button:
         @discord.ui.button(label= "🎫 Create a ticket", style = discord.ButtonStyle.blurple, custom_id= "createticket")
         async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
            overwrites = {
            interaction.guild.get_role(1074538286833475625): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)}

            now = datetime.now()
            exact_time = now.strftime("%m %d %Y %Hh %Mm %Ss")
            category = interaction.guild.get_channel_or_thread(1070491639925198939)
            channel = await interaction.guild.create_text_channel(name=f"ticket-{exact_time}", overwrites=overwrites, category = category)
            # Send a welcome message to the user
            welcome_message = f"Welcome to your private ticket, {interaction.user.mention} !"
            await channel.send(welcome_message, view= close())

    class close(discord.ui.View):
        def __init__(self):
            super().__init__(timeout= None)
            self.value = None

            # Close ticket button:
        @discord.ui.button(label= "❌ Close ticket", style = discord.ButtonStyle.red, custom_id= "closeticket")
        async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.button):
            try: await interaction.channel.delete()
            except: await interaction.response.send_message("Deleted!", ephemeral= True)

    @bot.command()
    async def ticket(ctx):
        embed = discord.Embed(title = "Click here to open a support ticket!\nOnly Mods and Admins can see your ticket!", color=discord.Colour.blue())
        view = button_view()
        await ctx.send(embed = embed, view= view)

    ''' Voice-chat Channel Generator '''
    voice_channels = {}

    async def create_channel(member):
        guild = member.guild
        overwrites = {
            guild.get_role(1070888138454618133): discord.PermissionOverwrite(read_messages=True, connect=True), #MOOBot Role
            guild.get_role(1071585203195232266): discord.PermissionOverwrite(read_messages=True, connect=True, move_members=True), #MOOer Role
            guild.get_role(1071579671717756982): discord.PermissionOverwrite(read_messages=True, connect=True, move_members=True), #Subscriber Role
            guild.default_role: discord.PermissionOverwrite(read_messages=True, connect=False), #Everyone Role
            member: discord.PermissionOverwrite(read_messages=True, connect=True)} #User create the room
        category = guild.get_channel_or_thread(1080442931590217808)
        new_channel = await guild.create_voice_channel(name=f"{member.name}'s Channel", overwrites = overwrites, category = category)
        await member.move_to(new_channel)
        voice_channels[new_channel.id] = new_channel
        await new_channel.set_permissions(member, manage_channels=True)

    async def delete_channel(channel):
        if channel.id in voice_channels:
            await channel.delete()
            del voice_channels[channel.id]

    @bot.event
    async def on_voice_state_update(member, before, after):
        if before.channel is not None and before.channel.id in voice_channels:
            if len(before.channel.members) == 0:
                await delete_channel(before.channel)
        if after.channel.id == 1074897833636925451: #MOO Join To Create
            await create_channel(member)

    ''' Music Bot '''
    voice_clients = {}
    queue = []
    list = []
    yt_dl_opts = {'format': 'bestaudio/best',
                  'ffmpeg_location': '/home/container/ffmpeg/bin/ffmpeg.exe',
                  'postprocessors': [{
                      'key': 'FFmpegExtractAudio',
                      'preferredcodec': 'mp3'}]}
    ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

    ffmpeg_options = {"options": "-vn -b:a 96k -bufsize 64k","before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"}

    @bot.event
    async def on_message(msg):
        await bot.process_commands(msg)
        if msg.content.startswith("m.music.play"):
            try:
                voice_client = await msg.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client   

            except:
                print("error")

            try:
                url = msg.content.split()[1]
                queue.append(url)

                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                voice_clients[msg.guild.id].play(player)

            except Exception as err:
                print(err)


        if msg.content.startswith("m.music.pause"):
            try:
                voice_clients[msg.guild.id].pause()
            except Exception as err:
                print(err)

        # This resumes the current song playing if it's been paused
        if msg.content.startswith("m.music.resume"):
            try:
                voice_clients[msg.guild.id].resume()
            except Exception as err:
                print(err)

        # This stops the current playing song
        if msg.content.startswith("m.music.leave"):
            try:
                voice_clients[msg.guild.id].stop()
                await voice_clients[msg.guild.id].disconnect()
            except Exception as err:
                print(err)

        if msg.content.startswith("m.music.add"):
            url = msg.content.split()[1]
            queue.append(url)

        if msg.content.startswith("m.music.next"):
            x = queue[0]
            list.append(x)
            if len(queue) > 0:
                voice_clients[msg.guild.id].stop()
                queue.pop(0)
                queue.append(x)
                url = queue[0]
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                song = data['url']
                player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                if len(queue) > 0:
                    voice_clients[msg.guild.id].play(player)

        if msg.content.startswith("m.music.back"):
            queue.insert(0, list[-1])
            list.pop(-1)
            queue.pop(-1)
            if len(queue) > 0:
                voice_clients[msg.guild.id].stop()
                if len(queue) > 1:
                    url = queue[0]
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                    song = data['url']
                    player = discord.FFmpegPCMAudio(song, **ffmpeg_options)
                    voice_clients[msg.guild.id].play(player)
                    print("Back",queue)
    
    ''' Announcement '''

    #On ready:
    @bot.event
    async def on_ready():
        print("Ready!")
        check.start()
        check2.start()

    # Pin 1:
    @bot.command()
    async def pin(ctx, message):
        global msg
        global pin_channel
        channel = ctx.channel
        author_channel = discord.utils.get(ctx.guild.channels, id= channel.id)
        pin_channel = author_channel.id
        print(pin_channel)
        msg = message

    @tasks.loop(seconds=1)
    async def check(): 
        try:
            pinned = bot.get_channel(pin_channel)
            print(pinned)
            message = await discord.utils.get(pinned.history(limit=10))
            print(message)
            if not message.author.bot and message.content != '':
                await pinned.send(f'{msg}')
            else:
                pass
        except (NameError, discord.errors.HTTPException):
            pass

    

    # Pin 2:
    @bot.command()
    @commands.has_any_role(1079964169568272524)
    async def pin2(ctx, message):
        global msg2
        global pin_channel_2
        channel = ctx.channel
        author_channel = discord.utils.get(ctx.guild.channels, id= channel.id)
        pin_channel_2 = author_channel.id
        print(pin_channel_2)
        msg2 = message


    @tasks.loop(seconds=1)
    async def check2():
        try:
            pinned = bot.get_channel(pin_channel_2)
            message = await discord.utils.get(pinned.history(limit=1))
            if not message.author.bot and message.content != '':
                await pinned.send(f'{msg2}')
            else:
                pass
        except (NameError, discord.errors.HTTPException):
            pass
        
  

    ''' Moo City '''

    # User Profile:
    @bot.command()
    async def info(ctx, member: discord.Member = None):
        if member==None:
            await ctx.send("Bạn chưa nhập ID của người muốn tìm")

        role_list = []
        for role in member.roles:
            if role.name != "@everyone":
                role_list.append(role.mention)

        r = ','.join(role_list)

        pfp = member.display_avatar
        embed = discord.Embed(title = f"Profile của {member}")

        embed.set_thumbnail(url = f"{pfp}")
        embed.set_footer(text = f"Tìm bởi {ctx.author}")

        embed.add_field(name = "ID:", value = member.id, inline = False)
        embed.add_field(name = "Tên:", value = member, inline = False)
        embed.add_field(name = "Ngày tham gia 🐮 MOO:", value = member.joined_at, inline = False)
        embed.add_field(name = f"Roles: ({len(role_list)})", value = ''.join([r]), inline = False)

        users = await get_bank_data()
        bal_checking = users[str(ctx.author.id)]["Checking Account"]
        bal_saving = users[str(ctx.author.id)]["Saving Account"]

        embed.add_field(name = "🏙 Moo City:\n---------------------", value = '', inline = False)
        embed.add_field(name = "💵 Checking Account:", value = f"M$ {bal_checking:.2f}", inline = True)
        embed.add_field(name = "🏦 Saving Account:", value = f"M$ {bal_saving:.2f}", inline = True)
        

        await ctx.send(embed=embed)

    # Check balance:
    @bot.command()
    async def balance(ctx):   
        await register_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        checking = users[str(user.id)]["Checking Account"]
        saving = users[str(user.id)]["Saving Account"]

        # Embed:
        embed = discord.Embed(title= f"{ctx.author.name}'s balance:", color = discord.Colour.orange())
        embed.add_field(name = "💵 Checking Account", value = f"M$ {checking:.2f}")
        embed.add_field(name = "🏦 Saving Account", value = f"M$ {saving:.2f}")
        await ctx.send(embed = embed)
    
    # Register bank account:
    async def register_account(user):  
        users = await get_bank_data()

        if str(user.id) in users:
            return False
        else:
            users[str(user.id)] = {}
            users[str(user.id)]["Checking Account"] = 0
            users[str(user.id)]["Saving Account"] = 0
        
        with open("moo-bank.json","w") as f:
            json.dump(users, f)
        return True

    # Get Bank Data:
    async def get_bank_data():
        with open("moo-bank.json","r") as f:
            users = json.load(f)
        return users
    
    # Account change:
    async def update_bank(user, change = 0,mode = "Checking Account"):
        users = await get_bank_data()

        users[str(user.id)][mode] += change

        with open("moo-bank.json","w") as f:
            json.dump(users, f)

        bal = [users[str(user.id)]["Checking Account"], users[str(user.id)]["Saving Account"]]
        return bal
    
    # Manually add money(only for admin):
    @bot.command()
    @commands.has_any_role("new role")
    async def add_money(ctx, member: discord.Member,amount = None):
        await register_account(ctx.author)
        
        users = await get_bank_data()

        if amount == None:
            await ctx.send("Bạn chưa nhập số tiền bạn muốn chuyển! Hãy thử lại!")
            return

        amount = int(amount)
        
        if amount < 0:
            await ctx.send("Hãy nhập số không phải số âm!")
            return
        
        users[str(ctx.author.id)]["Checking Account"] += amount

        await ctx.send(f"Admin đã chuyển khoản cho **{member}** M$ {amount:.2f}")

        with open("moo-bank.json", "w") as f:
            json.dump(users, f)
    
    # Deposit (From Checking to Saving Account):
    @bot.command()
    async def deposit(ctx, amount = None):
        await register_account(ctx.author)

        if amount == None:
            await ctx.send("Bạn chưa nhập số tiền bạn muốn chuyển! Hãy thử lại!")
            return
        
        bal = await update_bank(ctx.author)

        amount = int(amount)
        
        if amount > bal[0]:
            await ctx.send("Số dư không đủ để thực hiện giao dịch!")
            return

        if amount < 0:
            await ctx.send("Hãy nhập số không phải số âm!")
            return
        
        await update_bank(ctx.author,-1*amount)
        await update_bank(ctx.author,amount,"Saving Account")

        await ctx.send(f"Bạn đã gửi M$ {amount:.2f} vào tài khoản tiết kiệm")

    # Withdraw (From Saving to Checking Account):
    @bot.command()
    async def withdraw(ctx, amount = None):
        await register_account(ctx.author)

        if amount == None:
            await ctx.send("Bạn chưa nhập số tiền bạn muốn chuyển! Hãy thử lại!")
            return
        
        bal = await update_bank(ctx.author)

        amount = int(amount)
        
        if amount>bal[1]:
            await ctx.send("Số dư không đủ để thực hiện giao dịch!")
            return

        if amount < 0:
            await ctx.send("Hãy nhập số không phải số âm!")
            return
        
        await update_bank(ctx.author, amount)
        await update_bank(ctx.author,-1* amount,"Saving Account")

        await ctx.send(f"Bạn đã rút M$ {amount:.2f} từ tài khoản tiết kiệm")

    # Zelle Transfer:
    @bot.command()
    async def transfer(ctx, member: discord.Member,amount = None):
        await register_account(ctx.author)
        await register_account(member)

        if amount == None:
            await ctx.send("Bạn chưa nhập số tiền bạn muốn chuyển! Hãy thử lại!")
            return
        
        bal = await update_bank(ctx.author)

        amount = int(amount)
        
        if amount > bal[0]:
            await ctx.send("Số dư không đủ để thực hiện giao dịch!")
            return

        if amount < 0:
            await ctx.send("Hãy nhập số không phải số âm!")
            return
        
        await update_bank(ctx.author,-1*amount, "Checking Account")
        await update_bank(member,amount,"Checking Account")

        await ctx.send(f"Bạn đã chuyển khoản cho **{member}** M$ {amount:.2f}")

    # Daily check-in:
    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = '**Bạn đã check-in cho ngày hôm nay. Hãy thử lại vào ngày mai! Thời gian phải chờ: {:.0f} giây**'.format(error.retry_after)
            await ctx.send(msg)

    @bot.command()
    @commands.cooldown(1,86400, commands.BucketType.user)
    async def daily(ctx):
        await register_account(ctx.author)
        
        users = await get_bank_data()

        daily = random.randrange(100, 200)

        await ctx.send(f"Check in thành công! Bạn đã nhận được M$ {daily}. Hãy quay lại vào ngày mai!")

        users[str(ctx.author.id)]["Checking Account"] += daily

        with open("moo-bank.json", "w") as f:
            json.dump(users, f)

    # Join To Earn Method:
    @bot.event 
    async def on_voice_state_update(member, before, after) -> None:
        await register_account(member)

        users = await get_bank_data()

        channel = bot.get_channel(MOO_CITY_ID)
        if before.channel is None and after.channel is not None:
            with shelve.open("moo_timejoin") as db:
                db[f"{member.id}_join_time"] = datetime.now() # store the time that the user joined the voice channel

        if before.channel is not None and after.channel is None:
            # User left a voice channel
            with shelve.open("moo_timejoin") as db:
                join_time = db.get(f"{member.id}_join_time")
                if join_time is None:
                    return # if we can't find the join time, we can't calculate the duration
                duration = (datetime.now() - join_time).seconds
                if duration >= 1: # award money for staying in the voice chat for at least 1 minute
                    award = duration * 0.02777777777777777
                    users[str(member.id)]["Checking Account"] += award
                    await channel.send(f"{member} đã kiếm được M$ {award:.2f} vì đã join Voice Chat trong {duration} giây")
                db[f"{member.id}_join_time"] = None # clear the join time from the database

        with open("moo-bank.json", "w") as f:
            json.dump(users, f)

    # Games:
    ## Coin Flip:



    ## Roulette:



    ## Blackjack:



    ## Poker:

            
    bot.run(TOKEN)
main()