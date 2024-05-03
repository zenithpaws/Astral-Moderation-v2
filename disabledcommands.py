# Command: Get leave message
@bot.slash_command(description="Get the leave message.")
async def getleavemessage(ctx):
    """Get the leave message."""
    if await permission_check(ctx):
        leave_message = await get_leave_message()
        if leave_message:
            await ctx.send(f"Current leave message:\n{leave_message}")
        else:
            await ctx.send("Leave message is not set.")

# Command: Get join message
@bot.slash_command(description="Get the join message.")
async def getjoinmessage(ctx):
    """Get the join message."""
    if await permission_check(ctx):
        join_message = await get_join_message()
        if join_message:
            await ctx.send(f"Current join message:\n{join_message}")
        else:
            await ctx.send("Join message is not set.")