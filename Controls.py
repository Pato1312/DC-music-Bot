from Youtube import playlist


async def lista(ctx):
    global playlist
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


async def limpiar(ctx):
    playlist.clear()
    await ctx.send("🗑️ Lista de reproducción vaciada.")


async def mover(ctx, posicion_actual: int, nueva_posicion: int):
    if 1 <= posicion_actual <= len(playlist) and 1 <= nueva_posicion <= len(playlist):
        cancion = playlist[posicion_actual - 1]
        playlist.remove(cancion)
        playlist.insert(nueva_posicion - 1, cancion)
        await ctx.send(
            f"🎵 Canción **{cancion[0]}** movida a la posición {nueva_posicion}."
        )
    else:
        await ctx.send("⚠️ Posiciones inválidas.")


async def eliminar(ctx, posicion: int):
    global playlist  # Asegúrate de que 'playlist' es la lista global
    try:
        # Verifica si la lista de reproducción está vacía
        if not playlist:
            await ctx.send("⚠️ La lista de reproducción está vacía.")
            return

        # Verifica si la posición es válida
        if 1 <= posicion <= len(playlist):
            cancion = playlist[posicion - 1]
            del playlist[posicion - 1]  # Elimina el elemento en la posición específica
            await ctx.send(f"🗑️ Canción **{cancion[0]}** eliminada de la lista.")
        else:
            await ctx.send("⚠️ La posición proporcionada es inválida.")
    except ValueError:
        # Maneja casos en los que `posicion` no sea un entero válido
        await ctx.send("⚠️ La posición debe ser un número válido.")
    except Exception as e:
        # Maneja otros errores inesperados
        await ctx.send("❌ Ocurrió un error al intentar eliminar la canción.")
        print(f"Error en eliminar command: {e}")
