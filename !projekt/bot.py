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

punkty_graczy = {} 

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

    def check_poziom(m):
        return (
            m.author == ctx.author and
            m.channel == ctx.channel and
            m.content in ['1', '2', '3']
        )

    msg = await bot.wait_for("message", check=check_poziom)
    wybor = msg.content

    latwy = [
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie1.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie2.png", "elektroodpady"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie3.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdj10.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdj11.png", "plastik")
    ]
    sredni = [
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie4.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie5.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie6.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdj12.png", "elektroodpady"),
    ]
    trudny = [
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie7.png", "plastik"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie8.png", "zmieszane"),
        ("C:\\Users\\Wojtek\\Desktop\\projekt kdl\\!projekt\\zdjecia\\zdjecie9.png", "plastik")
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

    await ctx.send(f"Rozpoczynamy poziom **{poziom}**! Napisz **koniec**, aby przerwać grę.")

    do_wylosowania = list(lista)

    while True:
        if len(do_wylosowania) == 0:
            do_wylosowania = list(lista)
            await ctx.send("♻️ Zobaczyłeś już wszystkie zdjęcia z tego poziomu! Resetuję pulę...")

        indeks = random.randint(0, len(do_wylosowania) - 1)
        obrazek, poprawna = do_wylosowania.pop(indeks)
        
        await ctx.send(file=discord.File(obrazek))
        await ctx.send("Do jakiego kosza to wrzucić? (papier/szklo/plastik/bio/metal/zmieszane/elektroodpady)")

        def check_odpowiedz(m):
            return (
                m.author == ctx.author and
                m.channel == ctx.channel and
                (m.content.lower() in ['papier', 'szklo', 'plastik', 'bio', 'metal', 'zmieszane', 'elektroodpady'] or m.content.lower() == 'koniec')
            )
            
        odp = await bot.wait_for("message", check=check_odpowiedz)
        odpowiedz = odp.content.lower()

        if odpowiedz == 'koniec':
            await ctx.send(f"Koniec gry! Twój ostateczny wynik to: **{punkty_graczy.get(ctx.author.id, 0)}** punktów.")
            break

        if odpowiedz == poprawna:
            punkty_graczy[ctx.author.id] = punkty_graczy.get(ctx.author.id, 0) + 1
            await ctx.send(f"Dobrze! Masz teraz {punkty_graczy[ctx.author.id]} punkt/y.\n---")
        else:
            punkty_graczy[ctx.author.id] = punkty_graczy.get(ctx.author.id, 0) - 1
            await ctx.send(f"Źle! Poprawna odpowiedź to: **{poprawna}**. Masz teraz {punkty_graczy[ctx.author.id]} punkt/y.\n---")

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
            await ctx.send("Analizuję zdjęcie, chwilka...")
            wynik = get_class(
                model_path="C:\\Users\\Wojtek\\Desktop\\projekt kdl\\keras_model.h5",
                labels_path="C:\\Users\\Wojtek\\Desktop\\projekt kdl\\labels.txt",
                image_path=f"./{attachment.filename}"
            )
            await ctx.send(f"Wynik analizy: **{wynik}**")
    else:
        await ctx.send("Zapomniałeś załadować obraz :(")

@bot.command(name='repozytorium')
async def repozytorium(ctx):
    await ctx.send("Tutaj jest repozytorium bota: https://github.com/Wojcio-tech/zmiany_klimatyczn")

@bot.command()
async def ciekawostka (ctx):
    ciekawostki = [
        "Plastikowa butelka rozkłada się w środowisku even do 500 lat! 🍼",
        "Szkło jest materiałem, który można przetwarzać w nieskończoność, nie tracąc jego jakości! 🫙",
        "Recykling jednej tony papieru pozwala uratować przed ścięciem około 17 drzew! 🌳",
        "Jedna bateryjka guzikowa może skazić aż 400 litrów wody! 🔋"
    ]
    await ctx.send(f"🌱 **Eko-Ciekawostka:** {random.choice(ciekawostki)}")

@bot.command()
async def punkty(ctx):
    stan_konta = punkty_graczy.get(ctx.author.id, 0)
    await ctx.send(f"👤 {ctx.author.name}, Twój obecny wynik to: **{stan_konta}** punktów.")

@bot.command(name='instrukcja')
async def instrukcja(ctx):
    tekst = (
        "♻️ **Instrukcja Bota – Pełna Lista Komend** ♻️\n\n"
        "🎮 **Gry i Edukacja:**\n"
        "• `?gra_smieciowa` - Uruchamia grę edukacyjną. Bot wysyła zdjęcie, a Ty dopasowujesz odpowiedni kosz.\n"
        "• `?ciekawostka` - Wyświetla losową, ekologiczną ciekawostkę.\n"
        "• `?punkty` - Pokazuje Twój aktualny stan konta punktowego w grze.\n\n"
        "🔍 **Analiza i Pliki:**\n"
        "• `?check` - Załącz zdjęcie do wiadomości z tą komendą, a sztuczna inteligencja bota spróbuje rozpoznać typ śmiecia.\n"
        "• `?zapisz_obraz` - Pobiera i zapisuje przesłane przez Ciebie zdjęcie na dysku bota.\n\n"
        "ℹ️ **Informacyjne:**\n"
        "• `?instrukcja` - Wyświetla tę listę komend.\n"
        "• `?o_mnie` - Pokazuje elegancką wizytówkę bota i informacje o projekcie Kodland.\n"
        "• `?repozytorium` - Wysyła link do kodu źródłowego bota na GitHubie."
    )
    await ctx.send(tekst)

@bot.command(name='o_mnie')
async def o_mnie(ctx):
    embed = discord.Embed(
        title="O mnie – EkoBot ♻️",
        description="Jestem zaawansowanym botem stworzonym przez Wojcio na projekt końcowy Kodland!",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Moja misja", 
        value="Edukacja ekologiczna i pomoc w segregacji śmieci za pomocą AI.", 
        inline=False
    )
    embed.add_field(
        name="Technologie", 
        value="Python, Discord.py, TensorFlow (Keras)", 
        inline=True
    )
    await ctx.send(embed=embed)
bot.run('swsw')
