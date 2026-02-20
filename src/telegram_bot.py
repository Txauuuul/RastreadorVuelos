"""
telegram_bot.py - Bot de Telegram para gestionar Flight Tracker

CONCEPTO EDUCATIVO - Bots:
Un bot es una aplicación que responde a mensajes automáticamente.
Telegram tiene una API que nos permite:
- Recibir mensajes del usuario
- Procesar comandos
- Enviar alertas automáticamente
- Todo de forma asincrónica (sin bloquear)

USO:
    python -c "from src.telegram_bot import iniciar_bot; iniciar_bot()"
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from datetime import datetime, timedelta
from src.logger import logger
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from src.database import (
    crear_ruta, obtener_rutas_activas, SessionLocal, Ruta,
    guardar_precio
)
from src.airport_utils import traducir_ciudad_a_iata, mostrar_ciudades_disponibles
from src.api import AmadeusAPI
from src.alert_calculator import CalculadorAlertasInteligentes
import traceback


# ==================== ESTADOS DE CONVERSACIÓN ====================
# Estos estados definen qué espera el bot en cada momento en la conversación
ORIGEN, DESTINO, FECHA_INICIO, FECHA_FIN, REGRESO, RANGO_REGRESO, REBAJA = range(7)


class FlightTrackerBot:
    """
    Bot de Telegram para Flight Tracker
    
    CONCEPTO EDUCATIVO - Máquina de estados:
    Una conversación es una "máquina de estados" - el bot espera
    diferentes inputs dependiendo del estado actual.
    
    Ejemplo:
    Estado 1: "¿De dónde?" → Usuario: "Madrid" → Estado 2
    Estado 2: "¿A dónde?" → Usuario: "Barcelona" → Estado 3
    ...
    """
    
    def __init__(self, token: str):
        self.token = token
        self.api = AmadeusAPI()
        self.chat_id = TELEGRAM_CHAT_ID
        logger.info("🤖 Bot de Telegram inicializado")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando: /start - Menú principal"""
        mensaje = (
            "🛫 *Flight Tracker*\n"
            "Rastreador inteligente de vuelos\n\n"
            "📋 *Comandos disponibles:*\n"
            "/agregar - Agregar nueva ruta a monitorear\n"
            "/buscar - Buscar vuelos ahora mismo\n"
            "/listar - Ver rutas activas\n"
            "/ayuda - Ver información\n\n"
            "¿Qué deseas hacer?"
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    
    async def add_flight(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Comando: /agregar
        Inicia conversación para agregar nueva ruta
        
        CONCEPTO EDUCATIVO - Conversación multi-paso:
        Usamos ConversationHandler para una conversación fluida
        """
        await update.message.reply_text(
            "🛫 *Agregar nueva ruta*\n\n"
            "Comenzaremos una búsqueda en rango de fechas.\n"
            "Puedes escribir ciudades (Madrid) o IATA (MAD)\n\n"
            "¿De dónde deseas viajar?",
            parse_mode="Markdown"
        )
        return ORIGEN
    
    async def get_origen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar origen"""
        try:
            origen_texto = update.message.text.strip()
            origen_iata = traducir_ciudad_a_iata(origen_texto)
            context.user_data['origen'] = origen_iata
            
            await update.message.reply_text(
                f"✅ Origen: {origen_iata}\n\n"
                f"¿A dónde deseas viajar?",
                parse_mode="Markdown"
            )
            return DESTINO
        
        except ValueError as e:
            await update.message.reply_text(f"❌ {e}\nIntenta de nuevo")
            return ORIGEN
    
    async def get_destino(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar destino"""
        try:
            destino_texto = update.message.text.strip()
            destino_iata = traducir_ciudad_a_iata(destino_texto)
            
            if destino_iata == context.user_data['origen']:
                await update.message.reply_text(
                    "❌ El destino debe ser diferente al origen\nIntenta de nuevo"
                )
                return DESTINO
            
            context.user_data['destino'] = destino_iata
            
            await update.message.reply_text(
                f"✅ Destino: {destino_iata}\n\n"
                f"¿Desde qué fecha? (DD-MM-YYYY)\n"
                f"Ej: 01-03-2026",
                parse_mode="Markdown"
            )
            return FECHA_INICIO
        
        except ValueError as e:
            await update.message.reply_text(f"❌ {e}\nIntenta de nuevo")
            return DESTINO
    
    async def get_fecha_inicio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar fecha inicio"""
        try:
            fecha_str = update.message.text.strip()
            fecha_obj = datetime.strptime(fecha_str, "%d-%m-%Y")
            
            if fecha_obj < datetime.now():
                await update.message.reply_text(
                    "❌ La fecha debe ser hoy o posterior\nIntenta de nuevo"
                )
                return FECHA_INICIO
            
            context.user_data['fecha_inicio'] = fecha_str
            
            await update.message.reply_text(
                f"✅ Desde: {fecha_str}\n\n"
                f"¿Hasta qué fecha? (DD-MM-YYYY)\n"
                f"Ej: 30-06-2026",
                parse_mode="Markdown"
            )
            return FECHA_FIN
        
        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido. Usa DD-MM-YYYY\n"
                "Ej: 15-03-2026"
            )
            return FECHA_INICIO
    
    async def get_fecha_fin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar fecha fin"""
        try:
            fecha_str = update.message.text.strip()
            fecha_obj = datetime.strptime(fecha_str, "%d-%m-%Y")
            fecha_inicio = datetime.strptime(context.user_data['fecha_inicio'], "%d-%m-%Y")
            
            if fecha_obj <= fecha_inicio:
                await update.message.reply_text(
                    "❌ La fecha fin debe ser posterior a la fecha inicio\nIntenta de nuevo"
                )
                return FECHA_FIN
            
            context.user_data['fecha_fin'] = fecha_str
            
            keyboard = [
                [InlineKeyboardButton("Sí", callback_data='si'),
                 InlineKeyboardButton("No", callback_data='no')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ Hasta: {fecha_str}\n\n"
                f"¿Deseas vuelo de *regreso* también?",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            return REGRESO
        
        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido. Usa DD-MM-YYYY"
            )
            return FECHA_FIN
    
    async def button_regreso(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar decisión de regreso (botones)"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'si':
            context.user_data['es_ida_vuelta'] = True
            await query.edit_message_text(
                text="✅ Vuelo de regreso: SÍ\n\n"
                "¿Cuántos días después de la llegada quieres regresar?\n"
                "Formato: MIN-MAX (Ej: 7-14)"
            )
            return RANGO_REGRESO
        else:
            context.user_data['es_ida_vuelta'] = False
            await query.edit_message_text(
                text="✅ Vuelo de regreso: NO\n\n"
                "¿A qué porcentaje de rebaja quieres alerta?\n"
                "Ej: 20 (para 20% de descuento)"
            )
            return REBAJA
    
    async def get_rango_regreso(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar rango de días para regreso"""
        try:
            rango_str = update.message.text.strip()
            min_d, max_d = map(int, rango_str.split('-'))
            
            if min_d < 1 or max_d < min_d:
                raise ValueError("Rango inválido")
            
            context.user_data['dias_regreso_min'] = min_d
            context.user_data['dias_regreso_max'] = max_d
            
            await update.message.reply_text(
                f"✅ Regreso: {min_d}-{max_d} días después\n\n"
                f"¿A qué porcentaje de rebaja quieres alerta?\n"
                f"Ej: 20 (para 20% de descuento)"
            )
            return REBAJA
        
        except ValueError:
            await update.message.reply_text(
                "❌ Formato inválido. Usa MIN-MAX\n"
                "Ej: 7-14"
            )
            return RANGO_REGRESO
    
    async def get_rebaja(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar porcentaje de rebaja"""
        try:
            rebaja_str = update.message.text.strip()
            rebaja = float(rebaja_str)
            
            if rebaja < 1 or rebaja > 100:
                raise ValueError("Debe estar entre 1 y 100")
            
            context.user_data['rebaja'] = rebaja
            
            # Crear la ruta
            ruta = crear_ruta(
                origen=context.user_data['origen'],
                destino=context.user_data['destino'],
                fecha_inicio=datetime.strptime(context.user_data['fecha_inicio'], "%d-%m-%Y"),
                fecha_fin=datetime.strptime(context.user_data['fecha_fin'], "%d-%m-%Y"),
                es_ida_vuelta=context.user_data.get('es_ida_vuelta', False),
                dias_regreso_min=context.user_data.get('dias_regreso_min'),
                dias_regreso_max=context.user_data.get('dias_regreso_max'),
                porcentaje_rebaja=rebaja,
                precio_min_automatico=True
            )
            
            mensaje_exito = (
                f"✅ *Ruta creada exitosamente!*\n\n"
                f"📍 {context.user_data['origen']} → {context.user_data['destino']}\n"
                f"📅 {context.user_data['fecha_inicio']} a {context.user_data['fecha_fin']}\n"
                f"💰 Alerta cuando baje {rebaja}%\n"
                f"💵 Precio mínimo: {ruta.precio_minimo_alerta}€\n\n"
                f"El rastreador comenzará a buscar automáticamente cada 5 horas."
            )
            
            await update.message.reply_text(
                mensaje_exito,
                parse_mode="Markdown"
            )
            
            return ConversationHandler.END
        
        except ValueError as e:
            await update.message.reply_text(
                f"❌ Error: {e}\nIntenta de nuevo (número entre 1 y 100)"
            )
            return REBAJA
    
    async def listar_rutas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando: /listar"""
        rutas = obtener_rutas_activas()
        
        if not rutas:
            await update.message.reply_text("❌ No hay rutas en monitoreo")
            return
        
        mensaje = "*📋 Rutas Activas:*\n\n"
        
        for idx, ruta in enumerate(rutas, 1):
            mensaje += (
                f"{idx}. {ruta.origen} → {ruta.destino}\n"
                f"   📅 {ruta.fecha_inicio.strftime('%d-%m-%Y')} a {ruta.fecha_fin.strftime('%d-%m-%Y')}\n"
                f"   💰 Alerta: {ruta.porcentaje_rebaja_alerta}% (mínimo {ruta.precio_minimo_alerta}€)\n\n"
            )
        
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    
    async def buscar_ahora(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando: /buscar - Buscar vuelos ahora"""
        rutas = obtener_rutas_activas()
        
        if not rutas:
            await update.message.reply_text("❌ Primero debes agregar rutas con /agregar")
            return
        
        mensaje = "🔍 *Buscando en todas las rutas...*\n\n"
        await update.message.reply_text(mensaje, parse_mode="Markdown")
        
        for ruta in rutas[:3]:  # Limitar a 3 para no abrumar
            try:
                logger.info(f"🔍 Buscando: {ruta.origen}→{ruta.destino}")
                
                resultado = self.api.search_flights_date_range(
                    ruta.origen,
                    ruta.destino,
                    ruta.fecha_inicio.strftime("%d-%m-%Y"),
                    ruta.fecha_fin.strftime("%d-%m-%Y")
                )
                
                if resultado['success']:
                    msg = (
                        f"✅ *{ruta.origen} → {ruta.destino}*\n"
                        f"💰 Más barato: {resultado['best_date']} por {resultado['best_price']}€\n"
                        f"✈️ {resultado['flight']['airline']}\n\n"
                    )
                    await update.message.reply_text(msg, parse_mode="Markdown")
                    
                    # Guardar precio
                    guardar_precio(
                        ruta_id=ruta.id,
                        origen=ruta.origen,
                        destino=ruta.destino,
                        fecha_vuelo=datetime.strptime(resultado['best_date'], "%d-%m-%Y"),
                        precio=resultado['best_price'],
                        aerolinea=resultado['flight']['airline'],
                        escalas=resultado['flight']['stops'],
                        fuente='amadeus'
                    )
            
            except Exception as e:
                logger.error(f"❌ Error buscando: {e}")
                await update.message.reply_text(
                    f"❌ Error buscando {ruta.origen}→{ruta.destino}: {str(e)[:50]}"
                )
    
    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancelar conversación"""
        await update.message.reply_text(
            "❌ Operación cancelada. Usa /agregar para empezar de nuevo."
        )
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar errores"""
        logger.error(f"Error en update: {context.error}")
        logger.error(traceback.format_exc())


async def iniciar_bot():
    """Iniciar el bot de Telegram"""
    logger.info("🤖 Iniciando Bot de Telegram...")
    
    bot = FlightTrackerBot(TELEGRAM_BOT_TOKEN)
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Conversation handler para agregar rutas
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('agregar', bot.add_flight)],
        states={
            ORIGEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_origen)],
            DESTINO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_destino)],
            FECHA_INICIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_fecha_inicio)],
            FECHA_FIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_fecha_fin)],
            REGRESO: [CallbackQueryHandler(bot.button_regreso)],
            RANGO_REGRESO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_rango_regreso)],
            REBAJA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.get_rebaja)],
        },
        fallbacks=[CommandHandler('cancelar', bot.cancelar)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('start', bot.start))
    app.add_handler(CommandHandler('listar', bot.listar_rutas))
    app.add_handler(CommandHandler('buscar', bot.buscar_ahora))
    app.add_handler(CommandHandler('ayuda', bot.start))
    app.add_error_handler(bot.error_handler)
    
    logger.info("✅ Bot de Telegram iniciado. Escuchando mensajes...")
    
    try:
        await app.run_polling(allowed_updates=None)
    except Exception as e:
        logger.error(f"❌ Error en bot: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(iniciar_bot())
