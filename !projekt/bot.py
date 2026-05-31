import discord
from tensorflow import keras
from tensorflow.keras.models import load_model
from discord.ext import commands
import random
import numpy as np
from PIL import Image, ImageOps 
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class FixedDepthwiseConv2D(keras.layers.DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)

def get_class(model_path, labels_path, image_path):
    model = load_model(
        model_path, 
        compile=False,
        custom_objects={'DepthwiseConv2D': FixedDepthwiseConv2D}
    )
    class_names = open(labels_path, "r", encoding="utf-8").readlines()
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = Image.open(image_path).convert("RGB")
    image = ImageOps.fit(image, (224, 224), Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index] 
    confidence = prediction[0][index]
    clean_name = class_name.strip().split(" ", 1)[-1]
    return f"{clean_name} ({confidence:.2f})"



bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    assert bot.user is not None
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

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

    latwy = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie1.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie2.png", "elektroodpady"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie3.png", "plastik")
    ]
    sredni = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie4.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie5.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie6.png", "zmieszane")
    ]
    trudny = [
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie7.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie8.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\kdl\\!projekt\\zdjecia\\zdjecie9.png", "plastik")
    ]

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
        await ctx.send("Do jakiego kosza to wrzucić? (papier/szklo/plastik/bio/metal/zmieszane/elektroodpady)")

        def check2(m):
            return (
                m.author == ctx.author and
                m.channel == ctx.channel and
                m.content.lower() in ['papier', 'szklo', 'plastik', 'bio', 'metal', 'zmieszane', 'elektroodpady']
            )

        odp = await bot.wait_for("message", check=check2)
        odpowiedz = odp.content.lower()

        if odpowiedz == poprawna:
            await ctx.send("Dobrze!")
        else:
            await ctx.send(f"Źle! Poprawna odpowiedź to: **{poprawna}**")

@bot.command()
async def zapisz_obraz(ctx):
    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        await ctx.send(f"Nazwa: {attachment.filename}")
        await ctx.send(f"Link: {attachment.url}")
        await ctx.send(f"Rozmiar: {attachment.size} bajtów")
        await attachment.save(f"./{attachment.filename}")
        await ctx.send(f"Zapisano obraz w ./{attachment.filename}")
    else:
        await ctx.send("Zapomniałeś załadować obraz :(")

@bot.command()
async def check(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            await attachment.save(f"./{attachment.filename}")
            await ctx.send(get_class(
                model_path="C:\\Users\\Wojtek\\Desktop\\projekt kdl\\keras_model.h5",
                labels_path="C:\\Users\\Wojtek\\Desktop\\projekt kdl\\labels.txt",
                image_path=f"./{attachment.filename}"
            ))
    else:
        await ctx.send("Zapomniałeś załadować obraz :(")



bot.run("tokenik")
