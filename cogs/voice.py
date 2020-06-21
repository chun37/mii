from discord.ext import commands
import os
import discord

# consts
CH_VOICE = int(os.getenv("CH_VOICE", "655319117691355166"))
CH_VOICE_TEXT = int(os.getenv("CH_VOICE_TEXT", "655319030428598303"))

def get_vc_channel(before, after):
    if after.channel:
        return after.channel
    elif before.channel:
        return before.channel

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def vc(self, ctx, named):
        if ctx.channel.id != CH_VOICE_TEXT:
            await ctx.send(f"{ctx.author.mention} ここでは実行できません。")
            return
        state = ctx.author.voice
        if not state:
            await ctx.send(f"{ctx.author.mention} VCに参加していないため実行できません。")
            return
        if state.channel.id != CH_VOICE:
            await ctx.send(f"{ctx.author.mention} AFKチャンネルに接続中は実行できません。")
            return
        channel = self.bot.get_channel(CH_VOICE)
        await channel.edit(name=named)
        channel = self.bot.get_channel(CH_VOICE_TEXT)
        await channel.edit(name=named + "-text")
        await ctx.send(f"{ctx.author.mention} チャンネル名を {named} に上書きしました。")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return
        channel = get_vc_channel(before, after)
        if channel.id != CH_VOICE:
            return
        i = len(channel.members)
        if after.channel and i >= 2:
            embed = discord.Embed(
                description=f"{member.display_name}が入室しました。",
                colour=0x000000
            )
            await self.bot.get_channel(CH_VOICE_TEXT).send(embed=embed, delete_after=60)
        elif before.channel and i >= 1:
            embed = discord.Embed(
                description=f"{member.display_name}が退室しました。",
                colour=0x000000
            )
            await self.bot.get_channel(CH_VOICE_TEXT).send(embed=embed, delete_after=60)
        elif i == 0 and channel.name != "vc":
            channel = self.bot.get_channel(CH_VOICE)
            await channel.edit(name="vc")
            channel = self.bot.get_channel(CH_VOICE_TEXT)
            await channel.edit(name="vc-text")
            embed = discord.Embed(
                description=f"接続人数が0になったのでチャンネル名をリセットしました。",
                colour=0x000000
            )
            await channel.send(embed=embed, delete_after=60)

def setup(bot):
    bot.add_cog(VoiceCog(bot))