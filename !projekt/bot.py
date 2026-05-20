import discord
import random
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.command()
async def gra_smieciowa(ctx):
    await ctx.send("Wybierz poziom trudności: 1=łatwy, 2=średni, 3=trudny")

    def check(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content in ['1', '2', '3']
        )

    msg = await bot.wait_for("message", check=check)
    wybor = msg.content

    # LISTY
    latwy = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie1.png", "tak"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie2.png", "nie"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie3.png", "tak")
    ]

    sredni = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie4.png", "nie"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie5.png", "tak"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie6.png", "nie")
    ]

    trudny = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie7.png", "tak"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie8.png", "nie"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie9.png", "tak")
    ]

    # WYBÓR LISTY
    if wybor == "1":
        lista = latwy
        poziom = "łatwy"
    elif wybor == "2":
        lista = sredni
        poziom = "średni"
    else:
        lista = trudny
        poziom = "trudny"

    while True:
        obrazek, poprawna = random.choice(lista)

        await ctx.send(f"Wybrałeś poziom **{poziom}**.")
        await ctx.send(file=discord.File(obrazek))
        await ctx.send("Czy można to wrzucić do plastiku? (tak/nie)")

        
        def check2(m):
            return (
                m.author == ctx.author and
                m.channel == ctx.channel and
                m.content.lower() in ['tak', 'nie']
            )

        odp = await bot.wait_for("message", check=check2)
        odpowiedz = odp.content.lower()

        # SPRAWDZENIE
        if odpowiedz == poprawna:
            await ctx.send("Dobrze!")
        else:
            await ctx.send(f"Źle! Poprawna odpowiedź to: {poprawna}")


bot.run("MTQ5NDAwOTE2NjUzMTEzNzY4Ng.G-YhKl.pI6cxMjH4o827-JqON_D3jTFKb9coYGKFflkTg")
