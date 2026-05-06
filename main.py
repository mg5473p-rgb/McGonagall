import discord
from discord.ext import commands
import json
import os

# =====================
# Intents
# =====================
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# チャンネルID
# =====================
GUIDE_CHANNEL_ID = 1501544588937269349
HEALTH_CHANNEL_ID = 1492747771206176840
SORT_CHANNEL_ID = 1500520708974051498
INTRO_CHANNEL_ID = 1492739600253456414

# =====================
# データ保存
# =====================
DATA_FILE = "mcgonagall.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_state = load_data()

# =====================
# 進捗表示
# =====================
def get_progress(uid):
    state = user_state.get(uid, {"health": False, "sorting": False, "intro": False})

    return (
        "現在の進行状況です\n\n"
        f"🏥 健康診断：{'✔' if state['health'] else '未完了'}\n"
        f"🎩 組み分け：{'✔' if state['sorting'] else '未完了'}\n"
        f"🪶 自己紹介：{'✔' if state['intro'] else '未完了'}"
    )

# =====================
# 寮判定
# =====================
def check_house(member):
    roles = [r.name for r in member.roles]

    if "グリフィンドール" in roles:
        return "勇敢な判断ですね。よくぞその寮を選びました。"
    elif "スリザリン" in roles:
        return "慎重で、目的意識のある選択です。結構です。"
    elif "レイブンクロー" in roles:
        return "よく考えられた選択ですね。知性が感じられます。"
    elif "ハッフルパフ" in roles:
        return "誠実で落ち着いた選択ですね。安心しました。"
    else:
        return "まだ組み分けが済んでいないようですね。\n後でちゃんと組み分け帽子のところへ行くのですよ。"

# =====================
# ボタンビュー
# =====================
class NextButton(discord.ui.View):
    def __init__(self, step):
        super().__init__(timeout=None)
        self.step = step

    @discord.ui.button(label="はい", style=discord.ButtonStyle.success)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        uid = str(interaction.user.id)

        if uid not in user_state:
            user_state[uid] = {"health": False, "sorting": False, "intro": False}

        state = user_state[uid]

        # =====================
        # Step分岐
        # =====================

        # 0 → 健康診断
        if self.step == 0:
            await interaction.response.send_message(
                f"よろしいです。\n\n🏥 健康診断はこちら\n<#{HEALTH_CHANNEL_ID}>",
                ephemeral=True
            )
            state["health"] = True

        # 1 → 組み分け
        elif self.step == 1:
            msg = check_house(interaction.user)

            await interaction.response.send_message(
                f"{msg}\n\n🎩 組み分けはこちら\n<#{SORT_CHANNEL_ID}>",
                ephemeral=True
            )
            state["sorting"] = True

        # 2 → 自己紹介
        elif self.step == 2:
            await interaction.response.send_message(
                f"よろしい。\n\n🪶 自己紹介はこちら\n<#{INTRO_CHANNEL_ID}>",
                ephemeral=True
            )
            state["intro"] = True

        # 3 → 完了
        elif self.step == 3:
            await interaction.response.send_message(
                "あなたはとても優秀です。",
                ephemeral=True
            )

        save_data(user_state)

# =====================
# メイン案内
# =====================
async def send_guide(channel):

    await channel.send(
        "ようこそ、ホグワーツへ。\n"
        "あなたはホグワーツの新入生で間違いないですね？",
        view=NextButton(0)
    )

    await channel.send(
        "🏥 健康診断（ロール付与）はお済みですか？",
        view=NextButton(1)
    )

    await channel.send(
        "🎩 組み分けはお済みですか？",
        view=NextButton(2)
    )

    await channel.send(
        "🪶 自己紹介はお済みですか？",
        view=NextButton(3)
    )

# =====================
# 起動
# =====================
@bot.event
async def on_ready():
    print("Bot起動")

    channel = bot.get_channel(GUIDE_CHANNEL_ID)
    if channel:
        await send_guide(channel)

# =====================
# 起動
# =====================
bot.run("discordtoken")
