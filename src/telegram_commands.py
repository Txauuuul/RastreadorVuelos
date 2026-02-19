"""
telegram_commands.py - Comandos interactivos del bot de Telegram

CONCEPTO EDUCATIVO - Telegram Bot Commands:
Los bots de Telegram pueden responder a comandos (/comando) enviados
por el usuario. Es una forma elegante de interactuar sin interfaz web.

MEJORAS v2.0:
- Búsqueda por nombre de ciudad (no requiere saber códigos IATA)
- Búsqueda por rango de fechas (no fecha específica)
- Automáticamente elige el aeropuerto más barato
- Elige la fecha más barata dentro del mes

Comandos soportados:
/start - Mensaje de bienvenida
/lista - Ver vuelos monitoreados
/agregar - Agregar nuevo vuelo (CON MEJORAS)
/modificar - Cambiar parámetros
/eliminar - Dejar de monitorear
/historial - Ver precios históricos
/estadisticas - Ver resumen
"""

import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes, CallbackQueryHandler
)
from telegram.error import TelegramError
from src.logger import logger
from src.database import Database
from src.config import TELEGRAM_BOT_TOKEN
from src.city_mapper import get_iata_codes_for_city, find_cheapest_airport, format_city_name
from src.api import AmadeusAPI


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
        self.api = AmadeusAPI()
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
        """Comando /agregar - Iniciar flujo con NOMBRE DE CIUDAD (no código IATA)"""
        await update.message.reply_text(
            "➕ <b>Agregar nuevo vuelo</b>\n\n"
            "¿De qué <b>ciudad</b> quieres viajar?\n"
            "<i>Ejemplos: Madrid, Nueva York, Barcelona, Londres, París</i>",
            parse_mode='HTML'
        )
        return self.AGREGAR_ORIGEN
    
    async def agregar_origen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar nombre de ciudad (origen)"""
        origin_city = update.message.text.strip()
        
        # Validar que la ciudad exista en nuestro mapeo
        iata_codes = get_iata_codes_for_city(origin_city)
        
        if not iata_codes:
            await update.message.reply_text(
                f"❌ No reconozco la ciudad '{origin_city}'.\n"
                "Intenta con: Madrid, Barcelona, Londres, París, Nueva York, etc."
            )
            return self.AGREGAR_ORIGEN
        
        context.user_data['origin_city'] = origin_city
        context.user_data['origin_iata'] = iata_codes[0] if len(iata_codes) == 1 else iata_codes
        
        await update.message.reply_text(
            f"✅ Origen: {format_city_name(origin_city)}\n\n"
            "¿A qué <b>ciudad</b> quieres ir?",
            parse_mode='HTML'
        )
        return self.AGREGAR_DESTINO
    
    async def agregar_destino(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar nombre de ciudad (destino)"""
        destination_city = update.message.text.strip()
        
        # Validar que la ciudad exista en nuestro mapeo
        iata_codes = get_iata_codes_for_city(destination_city)
        
        if not iata_codes:
            await update.message.reply_text(
                f"❌ No reconozco la ciudad '{destination_city}'.\n"
                "Intenta con: Madrid, Barcelona, Londres, París, Nueva York, etc."
            )
            return self.AGREGAR_DESTINO
        
        context.user_data['destination_city'] = destination_city
        context.user_data['destination_iata'] = iata_codes[0] if len(iata_codes) == 1 else iata_codes
        
        await update.message.reply_text(
            f"✅ Destino: {format_city_name(destination_city)}\n\n"
            "¿En qué <b>mes o rango de fechas</b> quieres viajar?\n"
            "<i>Ejemplos: febrero, marzo, 01-03 a 31-03, etc.</i>",
            parse_mode='HTML'
        )
        return self.AGREGAR_FECHA
    
    async def agregar_fecha(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar mes/rango de fechas y buscar el vuelo más barato"""
        date_input = update.message.text.strip()
        
        # Parsear el input para obtener start_date y end_date
        
        try:
            # Intentar parsear diferentes formatos
            if "-" in date_input and len(date_input) > 5:
                # Formato: "01-03 a 31-03" o "1-3 to 31-3"
                parts = date_input.replace(" a ", "-").replace(" to ", "-").split("-")
                if len(parts) >= 4:
                    start_day, start_month = int(parts[0].strip()), int(parts[1].strip())
                    end_day, end_month = int(parts[2].strip()), int(parts[3].strip())
                else:
                    raise ValueError("Formato de rango inválido")
            else:
                # Asumir que es un nombre de mes
                month_names = {
                    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
                }
                month = month_names.get(date_input.lower())
                if not month:
                    raise ValueError(f"Mes no reconocido: {date_input}")
                
                start_day, start_month = 1, month
                end_day, end_month = 28, month  # Usar 28 para ser seguro
            
            # Asumir año actual o siguiente
            year = datetime.now().year
            if datetime(year, start_month, start_day) < datetime.now():
                year += 1
            
            start_date = datetime(year, start_month, start_day)
            end_date = datetime(year, end_month, end_day)
            
            # Formatear para la API
            start_date_str = start_date.strftime("%d-%m-%Y")
            end_date_str = end_date.strftime("%d-%m-%Y")
            
            context.user_data['start_date'] = start_date_str
            context.user_data['end_date'] = end_date_str
            
            # Mostrar que está buscando
            await update.message.reply_text(
                f"⏳ Buscando el vuelo más barato en el rango {start_date_str} → {end_date_str}...\n\n"
                "<i>Esto puede tardar 1-2 minutos (revisando múltiples fechas)</i>",
                parse_mode='HTML'
            )
            
            # Aquí es donde buscamos el vuelo más barato
            # Guardamos los datos antes de continuar
            context.user_data['searching'] = True
            
            await update.message.reply_text(
                f"✅ Rango de fechas: {date_input}\n\n"
                "¿Cuál es el <b>precio máximo</b> que aceptas? (€)\n"
                "<i>Ejemplo: 200</i>",
                parse_mode='HTML'
            )
            return self.AGREGAR_MIN_PRECIO
        
        except (ValueError, TypeError) as e:
            logger.error(f"Error parseando fecha: {e}")
            await update.message.reply_text(
                "❌ Formato no reconocido.\n"
                "Intenta: febrero, marzo, 01-02 a 28-02, etc."
            )
            return self.AGREGAR_FECHA
    
    async def agregar_min_precio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar precio mínimo"""
        try:
            min_price = float(update.message.text.strip())
            
            if min_price < 0:
                await update.message.reply_text("❌ El precio no puede ser negativo.")
                return self.AGREGAR_MIN_PRECIO
            
            context.user_data['min_price'] = min_price
            
            await update.message.reply_text(
                f"✅ Precio máximo: {min_price}€\n\n"
                "¿Qué <b>reducción porcentual</b> de la media histórica te avise? (%)\n"
                "<i>Ejemplo: 15 (para alertas si baja 15%)</i>",
                parse_mode='HTML'
            )
            return self.AGREGAR_REDUCCION
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.AGREGAR_MIN_PRECIO
    
    async def agregar_reduccion(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesar reducción porcentual y guardar al BD"""
        try:
            reduction = float(update.message.text.strip())
            
            if reduction < 0 or reduction > 100:
                await update.message.reply_text("❌ El porcentaje debe estar entre 0 y 100.")
                return self.AGREGAR_REDUCCION
            
            # Mostrar que está procesando
            await update.message.reply_text(
                "⏳ Buscando la mejor fecha en el rango...\n"
                "<i>Esto puede tardar 1-2 minutos</i>"
            )
            
            # Obtener datos del contexto
            origin_city = context.user_data.get('origin_city')
            destination_city = context.user_data.get('destination_city')
            start_date = context.user_data.get('start_date')
            end_date = context.user_data.get('end_date')
            origin_iata = context.user_data.get('origin_iata')
            destination_iata = context.user_data.get('destination_iata')
            
            # Si tenemos múltiples opciones de aeropuertos, buscar el más barato
            # Si no, usar el que tenemos
            if isinstance(origin_iata, list):
                origin_iata = origin_iata[0]
            if isinstance(destination_iata, list):
                destination_iata = destination_iata[0]
            
            # Buscar el vuelo más barato en el rango
            search_result = self.api.search_flights_date_range(
                origin=origin_iata,
                destination=destination_iata,
                start_date=start_date,
                end_date=end_date,
                adults=1
            )
            
            if search_result.get('success'):
                best_date = search_result.get('best_date')
                best_price = search_result.get('best_price')
                
                # Guardar en BD
                success = self.db.add_watched_flight(
                    origin=origin_iata,
                    destination=destination_iata,
                    departure_date=best_date,  # Usar la mejor fecha encontrada
                    date_range_start=start_date,  # Guardar también el rango
                    date_range_end=end_date,
                    min_price=context.user_data['min_price'],
                    price_reduction_percent=reduction
                )
                
                if success:
                    message = (
                        f"✅ <b>Vuelo agregado correctamente</b>\n\n"
                        f"✈️ {format_city_name(origin_city)} → {format_city_name(destination_city)}\n"
                        f"📅 Mejor fecha encontrada: <b>{best_date}</b>\n"
                        f"💰 Precio mejor encontrado: <b>{best_price}€</b>\n"
                        f"📊 Rango buscado: {start_date} a {end_date}\n"
                        f"💯 Precio máximo aceptado: {context.user_data['min_price']}€\n"
                        f"📉 Alerta si baja: {reduction}%\n\n"
                        f"<i>Empezaré a monitorear cada 2 horas</i>"
                    )
                else:
                    message = (
                        f"⚠️ Este vuelo ya estaba en monitoreo.\n"
                        f"Usa /modificar para cambiar parámetros."
                    )
            else:
                message = (
                    f"❌ No se encontraron vuelos en el rango.\n"
                    f"{search_result.get('message', 'Intenta con otro rango de fechas')}"
                )
            
            await update.message.reply_text(message, parse_mode='HTML')
            return ConversationHandler.END
        
        except ValueError:
            await update.message.reply_text("❌ Introduce un número válido.")
            return self.AGREGAR_REDUCCION
        except Exception as e:
            logger.error(f"Error en agregar_reduccion: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return ConversationHandler.END
    
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
