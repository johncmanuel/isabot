def get_invite_url(app_id: str):
    return f"https://discord.com/api/oauth2/authorize?client_id={app_id}&scope=applications.commands"
