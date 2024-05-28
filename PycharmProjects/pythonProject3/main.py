import datetime

import nextcord
from nextcord.ext import commands
import json
import random as rand
import os
import cooldowns

intents = nextcord.Intents.all()
client = commands.Bot(intents=intents, help_command=None)
Guild_ids = [1045342942400892968]

shop = {"name":"", "price": 1, "description": "", },

@client.slash_command(guild_ids=Guild_ids)
async def testing(interaction: nextcord.Interaction):
    view = intershit()
    await interaction.response.send_message("Halo!", view=view, ephemeral=True)
    await view.wait()

# @client.command(aliases=["Balance", "Bal"])
@client.slash_command(guild_ids=Guild_ids, name="balance", description="Check how many dabloons you have!")
async def balance(interaction: nextcord.Interaction):
    user = interaction.user
    users = await get_bank_data(user)

    wallet_amt = users[str(user.id)]['wallet']
    bank_amt = users[str(user.id)]['bank']
    hasInsurance = users[str(user.id)]['insurance']
    embed = nextcord.Embed(title=f'{user.name}`s balance!', color=0xFFC0CB)
    embed.add_field(name="Your wallet balance:", value=f"have have {wallet_amt} dabloons in your wallet!",
                    inline=False)
    embed.add_field(name="Your bank balance:", value=f"You have {bank_amt} dabloons in your bank!", inline=False)
    if (hasInsurance == True):
        embed.add_field(name="Insurance", value="You have insurance! Your money is safe from Pirates.")
    else:
        embed.add_field(name="Insurance", value="You dont have any insurance! Pirates can rob you!")
    # await ctx.send(embed=embed)
    await interaction.response.send_message(embed=embed)


@client.slash_command(guild_ids=Guild_ids, name="Deposit", description="Deposit dabloons from your wallet into your bank!")
async def deposit(interaction: nextcord.Interaction, amount):

    # bal = await update_bank(interaction.user)
    users = await get_bank_data(interaction.user)
    if amount is None:
        await interaction.response.send_message('Please enter the amount of dabloons you want to withdraw!', ephemeral=True)
        return
    try:
        amount = int(amount)
    except:
        if amount == 'max' or amount == 'all':
            user = interaction.user
            max_amt = users[str(user.id)]['wallet']
            users = await get_bank_data(user)
            await update_bank(user, -1 * max_amt)
            await update_bank(user, max_amt, 'bank')
            with open("databases/bank.json", "r")as f:
                users = json.load(f)
            embed = nextcord.Embed(title=f"You deposited {max_amt} dabloons!", color=0xFFC0CB)
            embed.add_field(name=f"Wallet:",
                            value=f"You now have {users[str(interaction.user.id)]['wallet']} dabloons in your wallet.",
                            inline=False)
            embed.add_field(name=f"Bank:",
                            value=f"You now have {users[str(interaction.user.id)]['bank']} dabloons in your bank.")
            await interaction.response.send_message(embed=embed)

    else:
        if amount > users[str(interaction.user.id)]['wallet']:
            await interaction.response.send_message("You don't have enough dabloons!", ephemeral=True)
            return
        if amount < 0:
            await interaction.response.send_message('Amount must be positive!', ephemeral=True)
            return

        user = interaction.user
        await update_bank(user, -1 * amount)
        await update_bank(user, amount, 'bank')
        users = await get_bank_data(interaction.user)
        embed = nextcord.Embed(title=f"You deposited {amount} dabloons!", color=0xFFC0CB)
        embed.add_field(name=f"Wallet:",
                        value=f"You now have {users[str(interaction.user.id)]['wallet']} dabloons in your wallet.", inline=False)
        embed.add_field(name=f"Bank:", value=f"You now have {users[str(interaction.user.id)]['bank']} dabloons in your bank.")
        await interaction.response.send_message(embed=embed)

@client.slash_command(guild_ids=Guild_ids, name="Withdraw", description="Withdraw dabloons from your bank into your wallet!")
async def withdraw(interaction: nextcord.Interaction, amount=None):
    users = await get_bank_data(interaction.user)
    # bal = await update_bank(interaction.user)
    if (amount == None):
        await interaction.response.send_message("Please enter the amount you would like to withdraw!", ephemeral=True)
        return
    try:
        amount = int(amount)
    except:
        if amount == 'max' or amount == 'all':
            user = interaction.user
            max_amt = users[str(user.id)]['bank']
            users = await get_bank_data(interaction.user)
            await update_bank(user, max_amt)
            await update_bank(user, -1 * max_amt, 'bank')
            with open("databases/bank.json", "r")as f:
                users = json.load(f)
            embed = nextcord.Embed(title=f"You deposited {max_amt} dabloons!", color=nextcord.Color.green())
            embed.add_field(name=f"Wallet:",
                            value=f"You now have {users[str(interaction.user.id)]['wallet']} dabloons in your wallet.",
                            inline=False)
            embed.add_field(name=f"Bank:",
                            value=f"You now have {users[str(interaction.user.id)]['bank']} dabloons in your bank.")
            await interaction.response.send_message(embed=embed)


    else:
        if amount > users[str(interaction.user.id)]['bank']:
            await interaction.response.send_message("You don't have enough dabloons!", ephemeral=True)
            return
        if amount < 0:
            await interaction.response.send_message("Amount must be positive!", ephemeral=True)
            return
    user = interaction.user
    await update_bank(user, amount)
    await update_bank(user, -1 * amount, 'bank')
    with open("databases/bank.json", "r")as f:
        users = json.load(f)
    embed = nextcord.Embed(title=f"You withdrew {amount} dabloons!", color=nextcord.Color.green())
    embed.add_field(name=f"Wallet:",
                    value=f"You now have {users[str(interaction.user.id)]['wallet']} dabloons in your wallet.",
                    inline=False)
    embed.add_field(name=f"Bank:",
                    value=f"You now have {users[str(interaction.user.id)]['bank']} dabloons in your bank.")
    await interaction.response.send_message(embed=embed)


async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data(user)
    users[str(user.id)][mode] += change
    with open('databases/bank.json', 'w')as f:
        json.dump(users, f)
    bal = [users[str(user.id)]['wallet'], users[str(user.id)]['bank']]
    return bal

@client.slash_command(guild_ids=Guild_ids, name="Insurance", description="You can guy, renew, or cancel your insurance here!")
async def insurance(interaction: nextcord.Interaction):
    users = await get_bank_data(interaction.user)
    view = insuremydickinurballs()
    embed=nextcord.Embed(title=":desktop: Insurance office :desktop:", color=0xFFC0CB)
    embed.set_thumbnail("https://media.tenor.com/cSZp25bpjjoAAAAM/work-cat.gif")
    embed.set_footer(text=interaction.user.name + " interacted with miguel the insurance cat")
    if (users[str(interaction.user.id)]['hadInsurance'] == True):
        embed.add_field(name="Oh, your insurance expired...", value="Would you like to renew it?")
    elif (users[str(interaction.user.id)]['insurance'] == True):
        embed.add_field(name="Great!", value="You have insurance!")
    elif (users[str(interaction.user.id)]['insurance'] == False):
        embed.add_field(name="Oh no!", value="You dont have insurance! Would you like to buy it?")
    await interaction.response.send_message(embed=embed, view=view)
    await view.wait()


@client.slash_command(guild_ids=Guild_ids, name="Beg",description="A chance to get a small amount of dabloons (cooldown: 5m)")
# @cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.author)
async def beg(interaction: nextcord.Interaction):
    users = await get_bank_data(interaction.user)
    earnings = rand.randint(1, 100)
    if (earnings == 1):
        print("king")
        earnings += 100
        embed=nextcord.Embed(title="OMG!", color=0xFFD700)
        embed.add_field(name="The king gave you 100 dabloons :crown:!!!!", value="This is a 1 in 100 chance!")
        embed.set_thumbnail(url="https://s3-eu-west-1.amazonaws.com/media.unbound.co/p/images/11097/medium/King_cat.png?1554890802")
        embed.set_footer(text=interaction.user.name + " interacted with King Cat the III")
        await interaction.response.send_message(embed=embed)
        users[str(interaction.user.id)]['wallet'] += earnings
    elif (earnings > 1 and earnings <= 80):
        print("normal")
        earnings = rand.randint(1, 10)
        embed=nextcord.Embed(title=f"Lucky! A bypassing traveler gave you {earnings} dabloon(s)!", color=nextcord.Color.green())
        embed.add_field(name="Wallet:", value=f"You know have {users[str(interaction.user.id)]['wallet'] + earnings} in your wallet!")
        randomname = rand.randint(1,10)
        if (randomname == 1):
            embed.set_footer(text=interaction.user.name + " interacted with micheal the traveller cat")
            embed.set_thumbnail("https://img-9gag-fun.9cache.com/photo/a0NvAEz_460s.jpg")
        elif randomname == 2:
            embed.set_footer(text=interaction.user.name + " interacted with Katie the warrior cat")
            embed.set_thumbnail(url="https://th-thumbnailer.cdn-si-edu.com/bZAar59Bdm95b057iESytYmmAjI=/1400x1050/filters:focal(594x274:595x275)/https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/95/db/95db799b-fddf-4fde-91f3-77024442b92d/egypt_kitty_social.jpg")
        elif randomname == 3:
            embed.set_footer(text=interaction.user.name + " interacted with Elias the nerd cat")
            embed.set_thumbnail("https://i.imgflip.com/6on18t.png")
        elif randomname == 4:
            embed.set_footer(text=interaction.user.name + " interacted with Gael the convict cat")
            embed.set_thumbnail("https://i.ibb.co/Wk7SCTK/convictcat-transformed.jpg")
        elif randomname == 5:
            embed.set_footer(text=interaction.user.name + " interacted with Rowan the sailor cat")
            embed.set_thumbnail("https://i.pinimg.com/originals/96/bc/b2/96bcb2668c866f4d40b8310468839239.jpg")
        elif randomname == 6:
            embed.set_footer(text=interaction.user.name + " interacted with Dante the gangster cat")
            embed.set_thumbnail("https://cdn.shopify.com/s/files/1/0235/1965/8061/products/gangster_cat_costumer_for_halloween2_530x@2x.jpg?v=1569758115")
        elif randomname == 7:
            embed.set_footer(text=interaction.user.name + " interacted with Jaylen the lazy cat")
            embed.set_thumbnail("https://kittentoob.com/wp-content/uploads/2017/12/Exotic-Shorthair-13-750x469.jpg")
        elif randomname == 8:
            embed.set_footer(text=interaction.user.name + " interacted with Treyton the realtor cat")
            embed.set_thumbnail("https://preview.redd.it/esj6kphagqpy.jpg?auto=webp&s=18f8af60a8eaa1114b90b38a0fd209dfe99cda32")
        elif randomname == 9:
            embed.set_footer(text=interaction.user.name + " interacted with Lazlo the angry cat")
            embed.set_thumbnail("https://i.pinimg.com/564x/d6/63/e9/d663e9bdf0eb0ab8642bd0e15c434a53.jpg")
        elif randomname == 10:
            embed.set_footer(text=interaction.user.name + " interacted with Callibre the nice cat")
            embed.set_thumbnail("hhttps://images.unsplash.com/photo-1611267254323-4db7b39c732c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8Y3V0ZSUyMGNhdHxlbnwwfHwwfHw%3D&w=1000&q=80")
        await interaction.response.send_message(embed=embed)
        users[str(interaction.user.id)]['wallet'] += earnings
    elif (earnings > 80 and users[str(interaction.user.id)]['insurance'] == False):
        print("pirate un-insured")
        earnings = rand.randint(3,15)
        embed=nextcord.Embed(title=f"Oh no!", color=nextcord.Color.red())
        embed.add_field(name=f"You asked pirates for money and they took away {earnings} dabloons!", value="You dont have insurance!")
        embed.set_thumbnail(url="https://m.media-amazon.com/images/I/51yL023V6kL._AC_SY780_.jpg")
        embed.set_footer(text=interaction.user.name + " interacted with Big Jones the pirate cat")
        await interaction.response.send_message(embed=embed)
        users[str(interaction.user.id)]['wallet'] -= earnings
    elif (earnings > 80 and users[str(interaction.user.id)]['insurance'] == True):
        print("pirate insured")
        embed=nextcord.Embed(title="Close call!", color=nextcord.Color.orange())
        embed.add_field(name=f"You asked pirates for money, and they took away {earnings} dabloons!", value="but your insurance covered it!")
        embed.set_thumbnail("https://m.media-amazon.com/images/I/51yL023V6kL._AC_SY780_.jpg")
        embed.set_footer(text=interaction.user.name + " interacted with Big Jones the pirate cat")
        await interaction.response.send_message(embed=embed)

    with open('databases/bank.json', 'w')as f:
        json.dump(users, f)


async def open_account(user):
    users = await get_bank_data(user)
    if (str(user.id)) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0
        users[str(user.id)]['insurance'] = False
        users[str(user.id)]['last_insurance'] = ""
        with open('databases/Bank.json', 'w')as f:
            json.dump(users, f)
        return True


async def get_bank_data(user):
    with open('databases/bank.json', 'r')as f:
        users = json.load(f)
    if (users[str(user.id)]['insurance'] == True):
        last_cooldown = datetime.datetime.fromisoformat(users[str(user.id)]['last_insurance'])
        print((datetime.datetime.utcnow() - last_cooldown).seconds)
        if (datetime.datetime.utcnow() - last_cooldown).seconds > 86400:
            users[str(user.id)]['hadInsurance'] = True
            users[str(user.id)]['insurance'] = False
            with open('databases/bank.json', 'w')as f:
                json.dump(users, f)
    return users


@client.event
async def on_member_join(member: nextcord.member):
    await open_account(member)


@client.event
async def on_ready():
    for guild in client.guilds:
        for members in guild.members:
            await open_account(members)
            print(members)
    print(Guild_ids)
    print("bot is running")
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="Dabloons!"))


class intershit(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Nigger", style=nextcord.ButtonStyle.blurple)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("SuckADick", ephemeral=True)
        self.value = True
        self.stop()

class insuremydickinurballs(nextcord.ui.View):
    def __init__(self):
        super().__init__()



    @nextcord.ui.button(label="Buy insurance", style=nextcord.ButtonStyle.green)
    async def buyInsurance(self, button:nextcord.Button, interaction: nextcord.Interaction):
        users = await get_bank_data(interaction.user)

        if (users[str(interaction.user.id)]['bank'] >= 10 and users[str(interaction.user.id)]['insurance'] == False):
            users[str(interaction.user.id)]['last_insurance'] = str(datetime.datetime.utcnow())
            users[str(interaction.user.id)]['bank'] -= 10
            users[str(interaction.user.id)]['insurance'] = True

            await interaction.response.send_message(f"Insurance bought! it costs 10 dabloons per day (please come to renew everyday)!", ephemeral=True)

        elif (users[str(interaction.user.id)]['bank'] < 10):
            await interaction.response.send_message("You do not have enough dabloons for this!", ephemeral=True)

        elif (users[str(interaction.user.id)]['insurance'] == True):
            await interaction.response.send_message("You already have insurance :smile:", ephemeral=True)

        with open('databases/bank.json', 'w')as f:
            print("dumped")
            json.dump(users, f)

        self.stop()

    @nextcord.ui.button(label="Stop insurance", style=nextcord.ButtonStyle.red)
    async def stopInsurance(self, button:nextcord.Button, interaction: nextcord.Interaction):
        users = await get_bank_data(interaction.user)
        if (users[str(interaction.user.id)]['insurance'] == True and users[str(interaction.user.id)]['bank'] >= 10):
            users[str(interaction.user.id)]['bank'] -= 10
            users[str(interaction.user.id)]['insurance'] = False
            await interaction.response.send_message("You have canceled your insurance and taken away 10 dabloons; please come again!", ephemeral=True)
        else:
            await interaction.response.send_message("Sorry, but you dont have insurance!", ephemeral=True)
        with open('databases/bank.json', 'w')as f:
            json.dump(users, f)
        self.stop()

    @nextcord.ui.button(label="Renew insurance", style=nextcord.ButtonStyle.green)
    async def renewInsurance(self, button:nextcord.Button, interaction: nextcord.Interaction):
        users = await get_bank_data(interaction.user)
        if (users[str(interaction.user.id)]['hadInsurance'] == True and users[str(interaction.user.id)]['bank'] >= 10):
            users[str(interaction.user.id)]['insurance'] = True
            users[str(interaction.user.id)]['last_insurance'] = str(datetime.datetime.utcnow())
            users[str(interaction.user.id)]['hadInsurance'] = False
            users[str(interaction.user.id)]['bank'] -= 10
            await interaction.response.send_message("Your insurance has been renewed for another 24h! This has cost 10 dabloons.")
        else:
            await interaction.response.send_message("You can't do this!")
        with open('databases/bank.json', 'w')as f:
            json.dump(users, f)
        self.stop()




@client.event
async def on_application_command_error(interaction: nextcord.Interaction, error):
    error = getattr(error, "original", error)
    if isinstance(error, cooldowns.CallableOnCooldown):
        seconds = error.retry_after % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        await interaction.send(f'You are on cooldown! Try again in ' + "%d:%02d:%02d" % (hour, minutes, seconds) + ".", ephemeral=True)
    # raise error  # re-raise the error so all the errors will still show up in console



#################################################WORK###################################################################


@client.slash_command(guild_ids=Guild_ids, name="Work", description="Get a job to earn some extra dabloons!")
async def work(interaction: nextcord.Interaction):
    return



#################################################WORK###################################################################

client.run("MTA0NTMzODAxOTU0MjA4OTc5OQ.GxZ5Fq.rQ5DgKYj6Yz1WedI0Gxlxoog6H-iUq9Qq-05gg")
