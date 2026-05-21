import discord
from discord.ext import commands
from discord.ui import View, Select
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

# ==================================================
#                     ID
# ==================================================

FAMILY_CHANNEL_ID = 1505334814377644152
VZP_CHANNEL_ID = 1506987521253441556
LOG_CHANNEL_ID = 1506999446125154455

FRIEND_ROLE_ID = 1268120589122666558

FAMILY_PING_ROLE_ID = 1505334164659114055
VZP_PING_ROLE_ID = 1506999793048621228

# ==================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

cooldowns = {}

# ==================================================
#                   COOLDOWN
# ==================================================

def check_cooldown(user_id):

    now = datetime.now()

    if user_id in cooldowns:

        if now < cooldowns[user_id]:
            return False

    cooldowns[user_id] = now + timedelta(minutes=1440)

    return True

# ==================================================
#                 REVIEW BUTTONS
# ==================================================

class ReviewView(View):

    def __init__(self, user, category):

        super().__init__(timeout=None)

        self.user = user
        self.category = category

    @discord.ui.button(
        label="Принять",
        style=discord.ButtonStyle.success,
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = interaction.message.embeds[0]

        embed.color = 0x2B2D31

        embed.add_field(
            name="Заявка принята",
            value=f"Принял: {interaction.user.mention}",
            inline=False
        )

        embed.set_footer(
            text=f"Принял {interaction.user}",
            icon_url=interaction.user.display_avatar.url        
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        await log_channel.send(
            f"{interaction.user.mention} принял заявку {self.user.mention}"
        )

        await interaction.response.send_message(
            "Заявка принята.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Отклонить",
        style=discord.ButtonStyle.danger,
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        embed = interaction.message.embeds[0]

        embed.color = 0x2B2D31

        embed.add_field(
            name="Заявка отклонена",
            value=f"Отклонил: {interaction.user.mention}",
            inline=False
        )

        embed.set_footer(
            text=f"Отклонил {interaction.user}",
            icon_url=interaction.user.display_avatar.url        
        )

        await interaction.message.edit(
            embed=embed,
            view=None
        )

        if self.category == "family":
            ping = f"<@&{FAMILY_PING_ROLE_ID}>"
        else:
            ping = f"<@&{VZP_PING_ROLE_ID}>"

        await interaction.channel.send(
            f"{ping} заявка была отклонена."
        )

        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        await log_channel.send(
            f"{interaction.user.mention} отклонил заявку {self.user.mention}"
        )

        await interaction.response.send_message(
            "Заявка отклонена.",
            ephemeral=True
        )

# ==================================================
#                МОДАЛКА СЕМЬИ
# ==================================================

class FamilyModal(discord.ui.Modal, title="Заявка в семью"):

    name = discord.ui.TextInput(
        label="Ваше имя и возраст",
        placeholder="Пример: Владислав, 18"
    )

    about = discord.ui.TextInput(
        label="Расскажите о себе и почему именно Вы",
        placeholder="Пример: Адекватный, активный, люблю RP и общение",
        style=discord.TextStyle.paragraph
    )

    online = discord.ui.TextInput(
        label="Ваш часовой пояс и онлайн",
        placeholder="Пример: GMT+3 | 16:00-02:00"
    )

    families = discord.ui.TextInput(
        label="В каких семьях состояли ранее",
        placeholder="Пример: Kastelotti, Mihizaki"
    )

    expectation = discord.ui.TextInput(
        label="Что вы ждете от нашей семьи",
        placeholder="Пример: Актив, общение, совместные мероприятия",
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction):

        if not check_cooldown(interaction.user.id):

            await interaction.response.send_message(
                "Повторно подать заявку можно через сутки.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="НОВАЯ ЗАЯВКА",
            color=0x0f0f0f
        )

        embed.add_field(
            name="Пользователь",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="ID",
            value=interaction.user.id,
            inline=False
        )

        embed.add_field(
            name="Ваше имя и возраст",
            value=self.name.value,
            inline=False
        )

        embed.add_field(
            name="Расскажите о себе и почему именно Вы",
            value=self.about.value,
            inline=False
        )

        embed.add_field(
            name="Ваш часовой пояс и онлайн",
            value=self.online.value,
            inline=False
        )

        embed.add_field(
            name="В каких семьях состояли ранее",
            value=self.families.value,
            inline=False
        )

        embed.add_field(
            name="Что вы ждете от нашей семьи",
            value=self.expectation.value,
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text=f"• {interaction.user}"
        )

        channel = bot.get_channel(FAMILY_CHANNEL_ID)

        await channel.send(
            content=f"<@&{FAMILY_PING_ROLE_ID}>",
            embed=embed,
            view=ReviewView(interaction.user, "family")
        )

        await interaction.response.send_message(
            "Заявка в семью отправлена.",
            ephemeral=True
        )

# ==================================================
#                 МОДАЛКА VZP
# ==================================================

class VZPModal(discord.ui.Modal, title="Заявка на VZP"):

    name = discord.ui.TextInput(
        label="Ваше имя и возраст",
        placeholder="Пример: Владислав, 18"
    )

    activity = discord.ui.TextInput(
        label="Ваша активность и сколько было банов",
        placeholder="Пример: 5ч в день | 3 бана"
    )

    families = discord.ui.TextInput(
        label="В каких семьях были",
        placeholder="Пример: Kastelotti, Mihizaki"
    )

    online = discord.ui.TextInput(
        label="Ваш часовой пояс и онлайн",
        placeholder="Пример: GMT+3 | 16:00-02:00"
    )

    rollback = discord.ui.TextInput(
        label="Откат с общего DM и с любого мероприятия",
        placeholder="Пример: Ссылка"
    )

    async def on_submit(self, interaction):

        if not check_cooldown(interaction.user.id):

            await interaction.response.send_message(
                "Повторно подать заявку можно через сутки.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="НОВАЯ ЗАЯВКА",
            color=0x0f0f0f
        )

        embed.add_field(
            name="Пользователь",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="ID",
            value=interaction.user.id,
            inline=False
        )

        embed.add_field(
            name="Ваше имя и возраст",
            value=self.name.value,
            inline=False
        )

        embed.add_field(
            name="Ваша активность и сколько было банов",
            value=self.activity.value,
            inline=False
        )

        embed.add_field(
            name="В каких семьях были",
            value=self.families.value,
            inline=False
        )

        embed.add_field(
            name="Ваш часовой пояс и онлайн",
            value=self.online.value,
            inline=False
        )
        
        embed.add_field(
            name="Откат с общего DM и с любого мероприятия",
            value=self.rollback.value,
            inline=False
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        embed.set_footer(
            text=f" • {interaction.user}"
        )

        channel = bot.get_channel(VZP_CHANNEL_ID)

        await channel.send(
            content=f"<@&{VZP_PING_ROLE_ID}>",
            embed=embed,
            view=ReviewView(interaction.user, "vzp")
        )

        await interaction.response.send_message(
            "Заявка на VZP отправлена.",
            ephemeral=True
        )

# ==================================================
#                 SELECT MENU
# ==================================================

class ApplySelect(Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Подать заявку в семью",
                description="Стать частью семьи",
            ),

            discord.SelectOption(
                label="Подать заявку на VZP",
                description="Участвовать на VZP",
            ),

            discord.SelectOption(
                label="Получить роль FRIEND",
                description="Доступ к серверу",
            )

        ]

        super().__init__(
            placeholder="Нажмите, чтобы оставить заявку",
            options=options
        )

    async def callback(self, interaction):

        value = self.values[0]

        if value == "Подать заявку в семью":

            await interaction.response.send_modal(
                FamilyModal()
            )

        elif value == "Подать заявку на VZP":

            await interaction.response.send_modal(
                VZPModal()
            )

        elif value == "Получить роль FRIEND":

            role = interaction.guild.get_role(
                FRIEND_ROLE_ID
            )

            if role in interaction.user.roles:

                await interaction.response.send_message(
                    "У вас уже есть роль FRIEND.",
                    ephemeral=True
                )
                return

            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                "Роль FRIEND успешно выдана.",
                ephemeral=True
            )

# ==================================================
#                     VIEW
# ==================================================

class ApplyView(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(ApplySelect())

# ==================================================
#                    READY
# ==================================================

@bot.event
async def on_ready():

    bot.add_view(ApplyView())

    print(f"Бот онлайн: {bot.user}")

# ==================================================
#                    PANEL
# ==================================================

@bot.command()
async def panel(ctx):

    embed = discord.Embed(
        color=0x0f0f0f
    )

    embed.set_image(
        url="https://media.discordapp.net/attachments/1464306006019276861/1506985339615711252/IMG_4955.png"
    )

    await ctx.send(
        embed=embed,
        view=ApplyView()
    )

# ==================================================

bot.run(TOKEN)