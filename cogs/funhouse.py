from discord.ext import commands
from .utils import checks
import discord
import io

GUILD_ID = 81883016288276480
VOICE_ROOM_ID = 633466718035116052
GENERAL_VOICE_ID = 81883016309248000

class Funhouse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_outside_voice(self, state):
        return state.channel is None or state.channel.id != GENERAL_VOICE_ID

    def is_inside_voice(self, state):
        return state.channel is not None and state.channel.id == GENERAL_VOICE_ID

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != GUILD_ID:
            return

        voice_room = member.guild.get_channel(VOICE_ROOM_ID)
        if self.is_outside_voice(before) and self.is_inside_voice(after):
            # joined a channel
            await voice_room.set_permissions(member, read_messages=True)
        elif self.is_outside_voice(after) and self.is_inside_voice(before):
            # left the channel
            await voice_room.set_permissions(member, read_messages=None)

    @commands.command(hidden=True)
    async def cat(self, ctx):
        """Gives you a random cat."""
        async with ctx.session.get('https://aws.random.cat/meow') as resp:
            if resp.status != 200:
                return await ctx.send('No cat found :(')
            js = await resp.json()
            await ctx.send(embed=discord.Embed(title='Random Cat').set_image(url=js['file']))

    @commands.command(hidden=True)
    async def dog(self, ctx):
        """Gives you a random dog."""
        async with ctx.session.get('https://random.dog/woof') as resp:
            if resp.status != 200:
                return await ctx.send('No dog found :(')

            filename = await resp.text()
            url = f'https://random.dog/{filename}'
            filesize = ctx.guild.filesize_limit if ctx.guild else 8388608
            if filename.endswith(('.mp4', '.webm')):
                async with ctx.typing():
                    async with ctx.session.get(url) as other:
                        if other.status != 200:
                            return await ctx.send('Could not download dog video :(')

                        if int(other.headers['Content-Length']) >= filesize:
                            return await ctx.send(f'Video was too big to upload... See it here: {url} instead.')

                        fp = io.BytesIO(await other.read())
                        await ctx.send(file=discord.File(fp, filename=filename))
            else:
                await ctx.send(embed=discord.Embed(title='Random Dog').set_image(url=url))

def setup(bot):
    bot.add_cog(Funhouse(bot))
