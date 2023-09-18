import os
import discord
import time
import asyncio
import youtube_dl
from discord.utils import get
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands

''' Ticket System'''
bot = commands.Bot(command_prefix= 'moo.', intents= discord.Intents.all())

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
        print("Channel", channel)

        welcome_message = f"Welcome to your private ticket, {interaction.user.mention} !"
        print(welcome_message)
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


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Online")

    @commands.command()
    async def ticket(self, ctx):
        embed = discord.Embed(title = "Click here to open a support ticket!\nOnly Mods and Admins can see your ticket!", color= discord.Colour.blue())
        view = button_view()
        await ctx.send(embed = embed, view= view)

        
async def setup(bot):
    await bot.add_cog(Ticket(bot))