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

# 管理チャンネル
ADMIN_CHANNEL_ID = 1491010789560029244

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

    try:

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:

        print(f"JSON保存エラー: {e}")

user_state = load_data()

# =====================
# エラー通知
# =====================
async def send_error(title, description):

    try:

        channel = await bot.fetch_channel(ADMIN_CHANNEL_ID)

        embed = discord.Embed(
            title=f"⚠️ {title}",
            description=description,
            color=discord.Color.red()
        )

        await channel.send(embed=embed)

    except Exception as e:

        print(f"管理チャンネル通知失敗: {e}")

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

        await interaction.response.send_message(
            "🏥 健康診断（ロール付与）はお済みですか？",
            view=NextButton(2),
            ephemeral=True
        )

    # =====================
    # Step 2
    # =====================
    elif step == 2:

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

        state["sorting"] = True
        save_data(user_state)

        msg = check_house(interaction.user)

        await interaction.response.edit_message(
            content=(
                f"よろしい。\n\n"
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

        button = discord.ui.Button(
            label="はい",
            style=discord.ButtonStyle.success,
            custom_id=f"next_button_{next_step}"
        )

        button.callback = self.next_button

        self.add_item(button)

    async def next_button(
        self,
        interaction: discord.Interaction
    ):

        try:

            await send_step(interaction, self.next_step)

        except Exception as e:

            error_message = (
                f"ボタン処理中にエラーが発生しました。\n\n"
                f"ユーザー: {interaction.user}\n"
                f"ステップ: {self.next_step}\n\n"
                f"エラー内容:\n{e}"
            )

            print(error_message)

            await send_error(
                "ボタン処理エラー",
                error_message
            )

            if not interaction.response.is_done():

                await interaction.response.send_message(
                    "⚠️ エラーが発生しました。\n"
                    "管理者へ通知しています。",
                    ephemeral=True
                )

# =====================
# progress コマンド
# =====================
@bot.command()
async def progress(ctx):

    uid = str(ctx.author.id)

    state = user_state.get(
        uid,
        {
            "health": False,
            "sorting": False,
            "intro": False
        }
    )

    await ctx.send(
        "📖 現在の進行状況です\n\n"
        f"🏥 健康診断：{'✔' if state['health'] else '未完了'}\n"
        f"🎩 組み分け：{'✔' if state['sorting'] else '未完了'}\n"
        f"🪶 自己紹介：{'✔' if state['intro'] else '未完了'}"
    )

# =====================
# コマンドエラー
# =====================
@bot.event
async def on_command_error(ctx, error):

    error_message = (
        f"コマンドエラーが発生しました。\n\n"
        f"ユーザー: {ctx.author}\n"
        f"コマンド: {ctx.message.content}\n\n"
        f"エラー内容:\n{error}"
    )

    print(error_message)

    await send_error(
        "コマンドエラー",
        error_message
    )

# =====================
# 起動時
# =====================
@bot.event
async def on_ready():

    print(f"{bot.user} として起動")

    try:

        # Persistent View
        bot.add_view(NextButton(1))
        bot.add_view(NextButton(2))
        bot.add_view(NextButton(3))
        bot.add_view(NextButton(4))

        # チャンネル取得
        channel = await bot.fetch_channel(GUIDE_CHANNEL_ID)

        # 初期メッセージ送信
        await channel.send(
            "ようこそ、ホグワーツへ。\n"
            "あなたはホグワーツ新入生で間違いないですね？",
            view=NextButton(1)
        )

        print("案内メッセージ送信成功")

        # 起動通知
        await send_error(
            "Bot起動",
            "マクゴナガルBotが正常に起動しました。"
        )

    except Exception as e:

        error_message = (
            f"初期メッセージ送信に失敗しました。\n\n"
            f"エラー内容:\n{e}"
        )

        print(error_message)

        await send_error(
            "初期メッセージ送信エラー",
            error_message
        )

# =====================
# Discordイベントエラー
# =====================
@bot.event
async def on_error(event, *args, **kwargs):

    error_message = (
        f"Discordイベントエラーが発生しました。\n\n"
        f"イベント名: {event}"
    )

    print(error_message)

    await send_error(
        "Discordイベントエラー",
        error_message
    )

# =====================
# 起動
# =====================
bot.run(os.getenv("DISCORD_TOKEN"))
