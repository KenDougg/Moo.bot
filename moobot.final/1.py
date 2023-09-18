def main():
    import os
    import discord
    import time
    import asyncio
    import youtube_dl
    import discord
    from discord.utils import get
    from datetime import datetime
    from dotenv import load_dotenv
    from discord.ext import commands

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    CHANNEL_ID = 1076746450295341126
    WELCOMING_ID = 748526029076693074

    # Command-Prefix:
    bot = commands.Bot(command_prefix= 'moo.', intents= discord.Intents.all())

    # Help command:
    bot.remove_command("help")
    @bot.command(name= "help")
    async def help_commands(ctx):
        await ctx.send("Music Bot:\nmoo.music.play <Youtube URL>:      Play music\nmoo.music.add <Youtube URL>:      Add music to the queue\nmoo.music.next:     Skip to the next song\nmoo.music.back:      Go back to the previous song\nmoo.music.pause:      Pause the currently playing song\nmoo.music.resume:      Resume the currently playing song\nmoo.music.leave:      Disconnect the bot and stop playing music")

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

    ''' Voice-chat Channel Generator'''
    voice_channels = {}

    async def create_channel(member):
        guild = member.guild
        overwrites = {
            guild.get_role(1070888138454618133): discord.PermissionOverwrite(read_messages=True, connect=True), #MOOBot Role
            guild.get_role(1071585203195232266): discord.PermissionOverwrite(read_messages=True, connect=True, move_members=True), #MOOer Role
            guild.get_role(1071579671717756982): discord.PermissionOverwrite(read_messages=True, connect=True, move_members=True), #Subscriber Role
            guild.default_role: discord.PermissionOverwrite(read_messages=True, connect=False), #Everyone Role
            member: discord.PermissionOverwrite(read_messages=True, connect=True)} #User create the room
        category = guild.get_channel_or_thread(1072456719353008148)
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
                      'preferredcodec': 'mp3',
                      'preferredquality': '192'}]}
    ytdl = youtube_dl.YoutubeDL(yt_dl_opts)

    ffmpeg_options = {'options': "-vn"}

    @bot.event
    async def on_message(msg):
        await bot.process_commands(msg)
        if msg.content.startswith("moo.music.play"):
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


        if msg.content.startswith("moo.music.pause"):
            try:
                voice_clients[msg.guild.id].pause()
            except Exception as err:
                print(err)

        # This resumes the current song playing if it's been paused
        if msg.content.startswith("moo.music.resume"):
            try:
                voice_clients[msg.guild.id].resume()
            except Exception as err:
                print(err)

        # This stops the current playing song
        if msg.content.startswith("moo.music.leave"):
            try:
                voice_clients[msg.guild.id].stop()
                await voice_clients[msg.guild.id].disconnect()
            except Exception as err:
                print(err)

        if msg.content.startswith("moo.music.add"):
            url = msg.content.split()[1]
            queue.append(url)

        if msg.content.startswith("moo.music.next"):
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

        if msg.content.startswith("moo.music.back"):
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
    bot.run(TOKEN)
main()