"""
telegram_commands.py - Comandos interactivos del bot de Telegram

CONCEPTO EDUCATIVO - Telegram Bot Commands:
Los bots de Telegram pueden responder a comandos (/comando) enviados
por el usuario. Es una forma elegante de interactuar sin interfaz web.

Comandos soportados:
/start - Mensaje de bienvenida
/lista - Ver vuelos monitoreados
/agregar - Agregar nuevo vuelo
/modificar - Cambiar parámetros
/eliminar - Dejar de monitorear
/historial - Ver precios históricos
/estadisticas - Ver resumen
"""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes, CallbackQueryHandler
)
from telegram.error import TelegramError
from src.logger import logger
from src.database import Database
from src.config import TELEGRAM_BOT_TOKEN


class TelegramBotCommands:
    """
    Manejador de comandos de Telegram para gestionar vuelos
    
    CONCEPTO EDUCATIVO - Conversational Handler:
    Los ConversationHandler permiten flujos multi-paso (ej: preguntar
    origen, luego destino, luego fecha, etc.)
    """
    
    # Estados para conversaciones
    (AGREGAR_ORIGEN, AGREGAR_DESTINO, AGREGAR_FECHA, 
     AGREGAR_MIN_PRECIO, AGREGAR_REDUCCION) = range(5)
    
    (MODIFICAR_VUELO_ID, MODIFICAR_PRECIO, MODIFICAR_REDUCCION) = range(5, 8)
    
    (ELIMINAR_VUELO_ID,) = range(8, 9)
    
    (HISTORIAL_VUELO_ID,) = range(9, 10)
    
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN):
        """Inicializar el bot de Telegram"""
        self.token = token
        self.db = Database()
        logger.info("✅ Telegram Bot Commands inicializado")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        message = (
            "🛫 <b>Bienvenido al Flight Tracker</b>\n\n"
            "Puedo ayudarte a monitorear vuelos y avisarte cuando bajen de precio.\n\n"
            "<b>Comandos disponibles:</b>\n"
            "📋 /lista - Ver vuelos monitoreados\n"
            "➕ /agregar - Agregar nuevo vuelo\n"
            "✏️ /modificar - Cambiar parámetros\n"
            "🗑️ /eliminar - Dejar de monitorear\n"
            "📊 /historial - Ver precios históricos\n"
            "📈 /estadisticas - Ver resumen global\n\n"
            "<i>¿Por dónde quieres empezar?</i>"
        )
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def lista_vuelos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /lista - Ver vuelos monitoreados"""
        try:
            flights = self.db.get_all_watched_flights()
            
            if not flights:
                await update.message.reply_text(
                    "❌ No hay vuelos monitoreados.\n"
                    "Usa /agregar para añadir uno."
                )
                return
            
            message = "📋 <b>Vuelos Monitoreados:</b>\n\n"
            
            for flight in flights:
                message += (
                    f"ID: {flight['id']}\n"
                    f"✈️ {flight['origin']} → {flight['destination']}\n"
                    f"📅 {flight['departure_date']}\n"
                    f"💰 Min: {flight['min_price']}€ | "
                    f"📉 Reducción: {flight['price_reduction_percent']}%\n"
                    f"{'─' * 40}\n"
                )
            
            message += f"\n<i>Total: {len(flights)} vuelo(s)</i>"
            await update.message.reply_text(message, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error en /lista: {e}")
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def agregar_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /agregar - Iniciar flujo para agregar vuelo"""
        await update.message.reply_text(
            "➕ <b>Agregar nuevo vuelo</b>\n\n"
            "¿Cuál es el <b>código IATA del origen?</b>\n"
            "<i>Ejemplo: MAD, CDG, BCN, LHR</i>",
            parse_mode='HTML'
        )
        return self.AGREGAR_ORIGEN
    
    async def agregar_origen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar origen"""
        origin = update.message.text.strip().upper()
        
        if len(origin) != 3 or not origin.isalpha():
            await update.message.reply_text(
                "❌ Código IATA inválido.\n"
                "Debe ser 3 letras (ej: MAD)"
            )
            return self.AGREGAR_ORIGEN
        
        context.user_data['origin'] = origin
        
        await update.message.reply_text(
            f"✅ Origen: {origin}\n\n"
            "¿Cuál es el <b>código IATA del destino?</b>",
            parse_mode='HTML'
        )
        return self.AGREGAR_DESTINO
    
    async def agregar_destino(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar destino"""
        destination = update.message.text.strip().upper()
        
        if len(destination) != 3 or not destination.isalpha():
            await update.message.reply_text(
                "❌ Código IATA inválido.\n"
                "Debe ser 3 letras (ej: CDG)"
            )
            return self.AGREGAR_DESTINO
        
        context.user_data['destination'] = destination
        
        await update.message.reply_text(
            f"✅ Destino: {destination}\n\n"
            "¿Cuál es la <b>fecha de salida?</b>\n"
            "<i>Formato: DD-MM-YYYY (ej: 25-02-2025)</i>",
            parse_mode='HTML'
        )
        return self.AGREGAR_FECHA
    
    async def agregar_fecha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar fecha"""
        fecha = update.message.text.strip()
        
        if len(fecha) != 10 or fecha[2] != '-' or fecha[5] != '-':
            await update.message.reply_text(
                "❌ Formato incorrecto.\n"
                "Usa DD-MM-YYYY (ej: 25-02-2025)"
            )
            return self.AGREGAR_FECHA
        
        context.user_data['departure_date'] = fecha
        
        await update.message.reply_text(
            f"✅ Fecha: {fecha}\n\n"
            "¿Cuál es el <b>precio mínimo</b> que buscas? (€)\n"
            "<i>Ejemplo: 50</i>",
            parse_mode='HTML'
        )
        return self.AGREGAR_MIN_PRECIO
    
    async def agregar_min_precio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar precio mínimo"""
        try:
            min_price = float(update.message.text.strip())
            
            if min_price < 0:
                await update.message.reply_text("❌ El precio no puede ser negativo.")
                return self.AGREGAR_MIN_PRECIO
            
            context.user_data['min_price'] = min_price
            
            await update.message.reply_text(
                f"✅ Precio mínimo: {min_price}€\n\n"
                "¿Qué <b>reducción porcentual</b> de la media histórica te avise? (%)\n"
                "<i>Ejemplo: 15 (para bajar 15% respecto al promedio)</i>",
                parse_mode='HTML'
            )
            return self.AGREGAR_REDUCCION
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.AGREGAR_MIN_PRECIO
    
    async def agregar_reduccion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar reducción porcentual y guardar"""
        try:
            reduction = float(update.message.text.strip())
            
            if reduction < 0 or reduction > 100:
                await update.message.reply_text("❌ El porcentaje debe estar entre 0 y 100.")
                return self.AGREGAR_REDUCCION
            
            # Guardar en BD
            success = self.db.add_watched_flight(
                origin=context.user_data['origin'],
                destination=context.user_data['destination'],
                departure_date=context.user_data['departure_date'],
                min_price=context.user_data['min_price'],
                price_reduction_percent=reduction
            )
            
            if success:
                message = (
                    f"✅ <b>Vuelo agregado correctamente</b>\n\n"
                    f"✈️ {context.user_data['origin']} → {context.user_data['destination']}\n"
                    f"📅 {context.user_data['departure_date']}\n"
                    f"💰 Precio mínimo: {context.user_data['min_price']}€\n"
                    f"📉 Reducción: {reduction}%\n\n"
                    f"<i>Empezaré a monitorear este vuelo cada 2 horas</i>"
                )
            else:
                message = (
                    f"⚠️ Este vuelo ya estaba en monitoreo.\n"
                    f"Usa /modificar para cambiar parámetros."
                )
            
            await update.message.reply_text(message, parse_mode='HTML')
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.AGREGAR_REDUCCION
    
    async def modificar_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /modificar - Iniciar cambios"""
        flights = self.db.get_all_watched_flights()
        
        if not flights:
            await update.message.reply_text("❌ No hay vuelos para modificar.")
            return ConversationHandler.END
        
        message = "✏️ <b>Modificar vuelo</b>\n\n¿Cuál es el <b>ID del vuelo?</b>\n\n"
        
        for flight in flights:
            message += f"ID {flight['id']}: {flight['origin']}→{flight['destination']} ({flight['departure_date']})\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
        return self.MODIFICAR_VUELO_ID
    
    async def modificar_vuelo_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar ID del vuelo a modificar"""
        try:
            flight_id = int(update.message.text.strip())
            flight = self.db.get_watched_flight(flight_id)
            
            if not flight:
                await update.message.reply_text("❌ Vuelo no encontrado.")
                return self.MODIFICAR_VUELO_ID
            
            context.user_data['modify_flight_id'] = flight_id
            context.user_data['modify_flight'] = flight
            
            message = (
                f"✅ Vuelo seleccionado: {flight['origin']}→{flight['destination']}\n\n"
                f"Valores actuales:\n"
                f"💰 Precio mínimo: {flight['min_price']}€\n"
                f"📉 Reducción: {flight['price_reduction_percent']}%\n\n"
                f"¿Nuevo <b>precio mínimo</b>? (pulsa 0 para mantener el actual)"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            return self.MODIFICAR_PRECIO
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.MODIFICAR_VUELO_ID
    
    async def modificar_precio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar nuevo precio"""
        try:
            new_price_input = update.message.text.strip()
            
            if new_price_input == '0':
                new_price = context.user_data['modify_flight']['min_price']
            else:
                new_price = float(new_price_input)
                if new_price < 0:
                    await update.message.reply_text("❌ El precio no puede ser negativo.")
                    return self.MODIFICAR_PRECIO
            
            context.user_data['new_min_price'] = new_price
            
            flight = context.user_data['modify_flight']
            
            await update.message.reply_text(
                f"✅ Nuevo precio mínimo: {new_price}€\n\n"
                f"¿Nuevo <b>porcentaje de reducción</b>? (pulsa 0 para mantener {flight['price_reduction_percent']}%)"
            )
            return self.MODIFICAR_REDUCCION
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.MODIFICAR_PRECIO
    
    async def modificar_reduccion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar nueva reducción y guardar"""
        try:
            reduction_input = update.message.text.strip()
            
            if reduction_input == '0':
                new_reduction = context.user_data['modify_flight']['price_reduction_percent']
            else:
                new_reduction = float(reduction_input)
                if new_reduction < 0 or new_reduction > 100:
                    await update.message.reply_text("❌ El porcentaje debe estar entre 0 y 100.")
                    return self.MODIFICAR_REDUCCION
            
            # Actualizar en BD
            import sqlite3
            db_path = self.db.db_path
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE watched_flights 
                       SET min_price = ?, price_reduction_percent = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ?""",
                    (context.user_data['new_min_price'], new_reduction, context.user_data['modify_flight_id'])
                )
                conn.commit()
            
            message = (
                f"✅ <b>Vuelo modificado</b>\n\n"
                f"💰 Nuevo precio mínimo: {context.user_data['new_min_price']}€\n"
                f"📉 Nueva reducción: {new_reduction}%"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.MODIFICAR_REDUCCION
    
    async def eliminar_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /eliminar"""
        flights = self.db.get_all_watched_flights()
        
        if not flights:
            await update.message.reply_text("❌ No hay vuelos para eliminar.")
            return ConversationHandler.END
        
        message = "🗑️ <b>Eliminar vuelo</b>\n\n¿Cuál es el <b>ID del vuelo?</b>\n\n"
        
        for flight in flights:
            message += f"ID {flight['id']}: {flight['origin']}→{flight['destination']} ({flight['departure_date']})\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
        return self.ELIMINAR_VUELO_ID
    
    async def eliminar_vuelo_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar eliminación"""
        try:
            flight_id = int(update.message.text.strip())
            flight = self.db.get_watched_flight(flight_id)
            
            if not flight:
                await update.message.reply_text("❌ Vuelo no encontrado.")
                return self.ELIMINAR_VUELO_ID
            
            # Eliminar
            self.db.deactivate_watched_flight(flight_id)
            
            message = (
                f"✅ <b>Vuelo eliminado</b>\n\n"
                f"Ya no monitorearé:\n"
                f"✈️ {flight['origin']} → {flight['destination']} ({flight['departure_date']})"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.ELIMINAR_VUELO_ID
    
    async def historial(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /historial"""
        flights = self.db.get_all_watched_flights()
        
        if not flights:
            await update.message.reply_text("❌ No hay vuelos monitoreados.")
            return ConversationHandler.END
        
        message = "📊 <b>Ver historial de precios</b>\n\n¿Cuál es el <b>ID del vuelo?</b>\n\n"
        
        for flight in flights:
            message += f"ID {flight['id']}: {flight['origin']}→{flight['destination']}\n"
        
        await update.message.reply_text(message, parse_mode='HTML')
        return self.HISTORIAL_VUELO_ID
    
    async def historial_vuelo_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostrar historial del vuelo"""
        try:
            flight_id = int(update.message.text.strip())
            flight = self.db.get_watched_flight(flight_id)
            
            if not flight:
                await update.message.reply_text("❌ Vuelo no encontrado.")
                return ConversationHandler.END
            
            history = self.db.get_price_history(flight_id, days=30)
            
            if not history:
                await update.message.reply_text(
                    f"❌ Sin historial de precios para {flight['origin']}→{flight['destination']}"
                )
                return ConversationHandler.END
            
            message = (
                f"📊 <b>Historial {flight['origin']}→{flight['destination']}</b>\n"
                f"<i>(Últimos 30 días)</i>\n\n"
            )
            
            # Mostrar últimos 5 precios
            for record in history[:5]:
                message += f"💰 {record['check_date']}: {record['price']}€\n"
            
            # Estadísticas
            avg = self.db.get_average_price(flight_id, days=30)
            min_price = self.db.get_min_price(flight_id, days=30)
            
            message += f"\n<b>Estadísticas:</b>\n"
            message += f"📈 Promedio: {avg:.2f}€\n"
            message += f"📉 Mínimo: {min_price:.2f}€"
            
            await update.message.reply_text(message, parse_mode='HTML')
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.HISTORIAL_VUELO_ID
    
    async def estadisticas(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /estadisticas"""
        try:
            stats = self.db.get_statistics()
            
            message = (
                f"📊 <b>Estadísticas Globales</b>\n\n"
                f"✈️ Vuelos activos: {stats['active_flights']}\n"
                f"💰 Registros de precio: {stats['price_records']}\n"
                f"🔔 Alertas enviadas: {stats['alerts_sent']}\n\n"
                f"<i>Los datos se actualizan cada 2 horas</i>"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
        
        except Exception as e:
            logger.error(f"Error en /estadisticas: {e}")
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancelar conversación"""
        await update.message.reply_text("❌ Operación cancelada.")
        return ConversationHandler.END
    
    def get_handlers(self):
        """Retornar los handlers para registrarlos en la aplicación"""
        return [
            CommandHandler("start", self.start),
            CommandHandler("lista", self.lista_vuelos),
            CommandHandler("estadisticas", self.estadisticas),
            
            ConversationHandler(
                entry_points=[CommandHandler("agregar", self.agregar_start)],
                states={
                    self.AGREGAR_ORIGEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.agregar_origen)],
                    self.AGREGAR_DESTINO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.agregar_destino)],
                    self.AGREGAR_FECHA: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.agregar_fecha)],
                    self.AGREGAR_MIN_PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.agregar_min_precio)],
                    self.AGREGAR_REDUCCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.agregar_reduccion)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            
            ConversationHandler(
                entry_points=[CommandHandler("modificar", self.modificar_start)],
                states={
                    self.MODIFICAR_VUELO_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.modificar_vuelo_id)],
                    self.MODIFICAR_PRECIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.modificar_precio)],
                    self.MODIFICAR_REDUCCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.modificar_reduccion)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            
            ConversationHandler(
                entry_points=[CommandHandler("eliminar", self.eliminar_start)],
                states={
                    self.ELIMINAR_VUELO_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.eliminar_vuelo_id)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
            
            ConversationHandler(
                entry_points=[CommandHandler("historial", self.historial)],
                states={
                    self.HISTORIAL_VUELO_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.historial_vuelo_id)],
                },
                fallbacks=[CommandHandler("cancel", self.cancel)],
            ),
        ]


async def run_telegram_bot():
    """Ejecutar el bot de Telegram de forma asincrónica"""
    try:
        # Crear aplicación
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Agregar handlers
        commands = TelegramBotCommands()
        for handler in commands.get_handlers():
            app.add_handler(handler)
        
        # Iniciar bot
        logger.info("🤖 Telegram Bot iniciado (escuchando comandos)")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
    except TelegramError as e:
        logger.error(f"❌ Error en Telegram Bot: {e}")
    except Exception as e:
        logger.error(f"❌ Error fatal en Telegram Bot: {e}")


if __name__ == "__main__":
    # Para ejecutar el bot localmente
    asyncio.run(run_telegram_bot())
