import os
from twitchio.ext import commands
from twitchio import Message, Channel, Chatter, IRCCooldownError
import sqlite3
import time
import re


regex = r"(h[o0][s5]{2,}[o0]*[0-9]*.*)|(h[o0][s5]t[0o]+[0-9]*.*)"
# normally it's 100 per 30 seconds but to be certain and since we are sending a "Running..." command
# we lower this by 2
msg_per_sec = (98)/30


class Bot(commands.Bot):
    channels_busy: list = []

    def __init__(self):
        super().__init__(
            token=os.getenv("ACCESS_TOKEN"),
            prefix=os.getenv("BOT_PREFIX"),
            initial_channels=os.getenv("CHANNELS").split(" ")
        )

        db_path = os.getenv("DB_PATH")

        self.con = sqlite3.connect(db_path)

        if not os.path.isfile(db_path):
            print(f"[ WARN ] File {db_path} doesn't exist, creating a new one")
            cur = self.con.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS bans
                        (nickname TEXT UNIQUE)''')
            self.con.commit()


    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'Functioning in channels: {os.getenv("CHANNELS").split(" ")}')


    async def event_message(self, message: Message):
        if message.echo:
            return
        
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)


    @commands.command(aliases=["test", "world"])
    async def hello(self, ctx: commands.Context):
        await ctx.send(f'Hello {ctx.author.name}!')
    

    @commands.command(aliases=["init"])
    async def run_bans(self, ctx: commands.Context):
        bot = ctx.get_user(self.nick)
        if not bot.is_mod:
            ctx.send("Cannot run ban commands as not a mod")
            return

        if not ctx.author.is_mod:
            return
        
        await ctx.send("Running...")

        cur = self.con.cursor()

        bans_fetch = cur.execute('SELECT nickname FROM bans').fetchall()
        await self.ban_users([row[0] for row in bans_fetch], ctx.channel)
        
        await ctx.send(f'Users banned')
    
    async def ban_users(self, users: list, channel: Channel):
        if channel.name in self.channels_busy:
            await channel.send("A command is already running in this channel. Please wait for that command to finish")
        
        # Yes, this is not thread safe
        # No, I will not change it
        self.channels_busy.append(channel.name)

        for nickname in users:
            try:
                await channel.send(f"/ban {nickname}")
                time.sleep(1 / msg_per_sec)
            except IRCCooldownError:
                await channel.send("Sorry, the bot somehow reached the Rate Limit (is another command running?). I tried my best to avoid it but I was wrong... Feel free to report this")
            except Exception:
                # Yes this is avoidable atm, but in case I add something I dont want to forget about it
                self.channels_busy.remove(channel.name)
                return
        
        self.channels_busy.remove(channel.name)
    

    @commands.command(aliases=["ban"])
    async def add_ban(self, ctx: commands.Context):
        curr_bot = ctx.get_user(self.nick)
        if not curr_bot.is_mod:
            ctx.send("Cannot run ban commands as not a mod")
            return
        
        if not ctx.author.is_mod:
            return
        
        await ctx.send("Running...")
        
        cur = self.con.cursor()

        content: str = ctx.message.content
        nicknames = content.split(" ")[1:]

        if len(nicknames) < 1:
            await ctx.send(f"Usage: {ctx.prefix} <user> [<user>, ...]")
            return

        for nickname in nicknames:
            try:
                cur.execute('INSERT INTO bans VALUES (?)', (nickname,))
            except sqlite3.IntegrityError as e:
                print(f"{e} | {nickname}")

            self.con.commit()

        await self.ban_users(nicknames, ctx.channel)

        await ctx.send(f"User/Users banned")
    

    @commands.command()
    async def check(self, ctx: commands.Context):
        curr_bot = ctx.get_user(self.nick)
        if not curr_bot.is_mod:
            ctx.send("Cannot run ban commands as not a mod")
            return
        
        if not ctx.author.is_mod:
            return
        
        users: set = ctx.users
        res: str = ""
        for user in users:
            if re.match(regex, user.name, re.MULTILINE | re.IGNORECASE):
                res += f"{user.name} "
        
        await ctx.send(f"Run {ctx.prefix}please to ban: {res}")

    

    @commands.command()
    async def please(self, ctx: commands.Context):
        curr_bot = ctx.get_user(self.nick)
        if not curr_bot.is_mod:
            ctx.send("Cannot run ban commands as not a mod")
            return
        
        if not ctx.author.is_mod:
            return
        
        await ctx.send("Running...")
        
        users: set = ctx.users
        to_ban: list = []
        user: Chatter
        for user in users:
            if re.match(regex, user.name, re.MULTILINE | re.IGNORECASE):
                to_ban.append(user.name)
        
        await self.ban_users(to_ban, ctx.channel)
        
        await ctx.send(f"Banned {len(to_ban)} users")


bot = Bot()

if __name__ == "__main__":
    bot.run()