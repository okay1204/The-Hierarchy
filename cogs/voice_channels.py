import nextcord
from nextcord.ext import commands


class VoiceChannels(commands.Cog):

    def __init__(self, client):
        self.client = client


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
    
        # if went from one channel to another
        if before.channel != after.channel:


            # if left voice channel
            if before.channel:

                category = self.client.get_channel(757374291028213852)

                if before.channel in category.voice_channels and before.channel.id not in (692954226401214565, 757375643368423556, 757374658172551198):
                
                    if not before.channel.members:

                        try: # in case channel was deleted instead of people leaving, use try except
                            await before.channel.delete()
                        except:
                            pass

            # if joined voice channel
            if after.channel:
                if after.channel.id == 757375643368423556: # create room

                    category = self.client.get_channel(757374291028213852)

                    channel = await category.create_voice_channel(f"{member.name}'s room", overwrites= {member: nextcord.PermissionOverwrite(manage_channels=True)})
                    await member.move_to(channel)

                elif after.channel.id == 757374658172551198: # create 1-1

                    category = self.client.get_channel(757374291028213852)

                    channel = await category.create_voice_channel(f"{member.name}'s 1-1", user_limit=2, overwrites= {member: nextcord.PermissionOverwrite(manage_channels=True)})
                    await member.move_to(channel)


def setup(client):
    client.add_cog(VoiceChannels(client))