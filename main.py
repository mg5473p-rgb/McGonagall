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
intents.message_content = True

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

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError:
        return {}

def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_state = load_data()

# =====================
# 寮メッセージ
# =====================
HOUSE_MESSAGES = {
    "グリフィンドール": "勇敢な判断ですね。よくぞその寮を選びました。",
    "スリザリン": "慎重で、目的意識のある選択です。結構です。",
    "レイブンクロー": "よく考えられた選択ですね。知性が感じられます。",
    "ハッフルパフ": "誠実で落ち着いた選択ですね。安心しました。"
}

# =====================
# 進捗表示
# =====================
def get_progress(uid):

    state = user_state.get(
        uid,
        {
            "health": False,
            "sorting": False,
            "intro": False
        }
    )

    return (
        "📖 現在の進行状況です\n\n"
        f"🏥 健康診断：{'✔' if state['health'] else '未完了'}\n"
        f"🎩 組み分け：{'✔' if state['sorting'] else '未完了'}\n"
        f"🪶 自己紹介：{'✔' if state['intro'] else '未完了'}"
    )

# =====================
# 寮確認
# =====================
def check_house(member):

    for role in member.roles:

        if role.name in HOUSE_MESSAGES:
            return HOUSE_MESSAGES[role.name]

    return (
        "まだ組み分けが済んでいないようですね。\n"
        "後でちゃんと組み分け帽子のところへ行くのですよ。"
    )

# =====================
# ステップ送信
# =====================
async def send_step(interaction, step):

    uid = str(interaction.user.id)

    if uid not in user_state:
        user_state[uid] = {
            "health": False,
            "sorting": False,
            "intro": False
        }

    state = user_state[uid]

    # =====================
    # Step 1
    # =====================
    if step == 1:

        await interaction.response.edit_message(
            content=(
                "🏥 健康診断（ロール付与）はお済みですか？"
            ),
            view=NextButton(2)
        )

    # =====================
    # Step 2
    # =====================
    elif step == 2:

        if not state["health"]:
            state["health"] = True
            save_data(user_state)

        await interaction.response.edit_message(
            content=(
                f"よろしいです。\n\n"
                f"🏥 健康診断はこちら\n"
                f"<#{HEALTH_CHANNEL_ID}>\n\n"
                f"🎩 組み分けはお済みですか？"
            ),
            view=NextButton(3)
        )

    # =====================
    # Step 3
    # =====================
    elif step == 3:

        if not state["sorting"]:
            state["sorting"] = True
            save_data(user_state)

        msg = check_house(interaction.user)

        await interaction.response.edit_message(
            content=(
                f"{msg}\n\n"
                f"🎩 組み分けはこちら\n"
                f"<#{SORT_CHANNEL_ID}>\n\n"
                f"🪶 自己紹介はお済みですか？"
            ),
            view=NextButton(4)
        )

    # =====================
    # Step 4
    # =====================
    elif step == 4:

        if not state["intro"]:
            state["intro"] = True
            save_data(user_state)

        await interaction.response.edit_message(
            content=(
                f"よろしい。\n\n"
                f"🪶 自己紹介はこちら\n"
                f"<#{INTRO_CHANNEL_ID}>\n\n"
                f"あなたはとても優秀です。"
            ),
            view=None
        )

# =====================
# ボタン
# =====================
class NextButton(discord.ui.View):

    def __init__(self, next_step):

        super().__init__(timeout=None)
        self.next_step = next_step

    @discord.ui.button(
        label="はい",
        style=discord.ButtonStyle.success
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await send_step(interaction, self.next_step)

# =====================
# progress コマンド
# =====================
@bot.command()
async def progress(ctx):

    uid = str(ctx.author.id)

    await ctx.send(get_progress(uid))

# =====================
# 起動時
# =====================
@bot.event
async def on_ready():

    print(f"{bot.user} として起動")

    # Persistent View
    bot.add_view(NextButton(1))
    bot.add_view(NextButton(2))
    bot.add_view(NextButton(3))
    bot.add_view(NextButton(4))

    try:

        # チャンネル取得
        channel = await bot.fetch_channel(GUIDE_CHANNEL_ID)

        # 既に案内があるか確認
        async for msg in channel.history(limit=20):

            if (
                msg.author == bot.user
                and "ホグワーツ" in msg.content
            ):
                print("既に案内メッセージがあります")
                return

        # 初期メッセージ送信
        await channel.send(
            "ようこそ、ホグワーツへ。\n"
            "あなたはホグワーツの新入生で間違いないですね？",
            view=NextButton(1)
        )

        print("案内メッセージ送信完了")

    except Exception as e:

        print(f"エラー: {e}")

# =====================
# 起動
# =====================
bot.run(os.getenv("DISCORD_TOKEN"))
