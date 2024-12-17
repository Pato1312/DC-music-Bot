from Youtube import playlist


async def lista(ctx):
    if playlist:
        mensaje = "🎵 **Lista de reproducción:**\n"
        mensaje += "\n".join(
            [f"{i + 1}. **{titulo}**" for i, (titulo, _) in enumerate(playlist)]
        )
    else:
        mensaje = "🎶 La lista de reproducción está vacía."
    await ctx.send(mensaje)


async def pausar(ctx, voz):
    if voz and voz.is_playing():
        voz.pause()
        await ctx.send("⏸️ Reproducción pausada.")
    else:
        await ctx.send("⚠️ No hay música reproduciéndose.")


async def reanudar(ctx, voz):
    if voz and voz.is_paused():
        voz.resume()
        await ctx.send("▶️ Reproducción reanudada.")
    else:
        await ctx.send("⚠️ No hay música pausada.")


async def saltar(ctx, voz):
    if voz and voz.is_playing():
        voz.stop()
        await ctx.send("⏭️ Canción saltada.")
    else:
        await ctx.send("⚠️ No hay música reproduciéndose.")
