import os
import wave
import pyperclip
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
import json
from datetime import datetime

class PodcastGeneratorWithGCS:
    def __init__(self, gemini_api_key, bucket_name, credentials_path=None):
        """
        Inicializa el generador de podcast con Gemini y Google Cloud Storage
        """
        # Configuración de Gemini
        self.client = genai.Client(api_key=gemini_api_key)
        self.tts_model = "gemini-2.5-flash-preview-tts"
        
        # Configuración fija de voces
        self.speakers_config = {
            "Mujer": "aoede",    # Voz femenina melodiosa
            "Hombre": "puck"     # Voz masculina animada
        }
        
        # Directorio fijo para todos los podcasts
        self.fixed_directory = "Audios_Secretos"
        
        # Configuración de Google Cloud Storage
        self.bucket_name = bucket_name
        
        # Tipos de archivo soportados para GCS
        self.ALLOWED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
        self.CONTENT_TYPES = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg'
        }
        self.MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
        
        # Inicializar cliente de GCS
        if credentials_path and os.path.exists(credentials_path):
            print(f"🔑 Usando credenciales GCS desde: {credentials_path}")
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            print("🔑 Usando credenciales GCS por defecto")
            self.storage_client = storage.Client()
        
        self.bucket = self.storage_client.bucket(bucket_name)
    
    def save_wave_file(self, filename, pcm_data, channels=1, rate=24000, sample_width=2):
        """
        Guarda los datos de audio PCM en un archivo WAV
        """
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            wf.writeframes(pcm_data)
        print(f"✅ Audio guardado localmente en: {filename}")
    
    def load_script_from_file(self, file_path):
        """
        Carga un guión desde un archivo de texto
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            print(f"✅ Guión cargado desde: {file_path}")
            return content
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {file_path}")
            return None
        except Exception as e:
            print(f"❌ Error al cargar archivo: {e}")
            return None
    
    def validate_script(self, script):
        """
        Valida que el guión tenga el formato correcto con los speakers esperados
        """
        lines = script.split('\n')
        valid_speakers = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ':' not in line:
                print(f"⚠️ Línea sin formato correcto (debe usar 'Speaker: texto'): {line}")
                continue
            
            speaker = line.split(':', 1)[0].strip()
            valid_speakers.add(speaker)
        
        print(f"📋 Speakers detectados en el guión: {list(valid_speakers)}")
        
        # Verificar que solo se usen Mujer y Hombre
        invalid_speakers = valid_speakers - {"Mujer", "Hombre"}
        if invalid_speakers:
            print(f"⚠️ Speakers no válidos encontrados: {invalid_speakers}")
            print("✅ Solo usa 'Mujer:' y 'Hombre:' en tu guión")
            return False
        
        if not valid_speakers:
            print("❌ No se encontraron speakers válidos en el guión")
            return False
        
        return True
    
    def _format_file_size(self, size_bytes):
        """Convierte bytes a formato legible"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _validate_audio_file(self, file_path):
        """Valida que el archivo de audio sea válido para subir"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Tipo de archivo no soportado: {file_extension}")
        
        file_size = os.path.getsize(file_path)
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"Archivo demasiado grande: {file_size / (1024*1024):.1f}MB")
        
        return file_extension, file_size
    
    def generate_podcast_uuid(self):
        """
        Genera un UUID único para el podcast
        """
        return str(uuid.uuid4())
    
    def get_public_url(self, destination_name):
        """
        Genera diferentes formatos de URL para acceder al archivo
        """
        urls = {
            'direct': f"https://storage.googleapis.com/{self.bucket_name}/{destination_name}",
            'cloud_storage': f"https://storage.cloud.google.com/{self.bucket_name}/{destination_name}",
            'googleapis': f"https://storage.googleapis.com/{self.bucket_name}/{destination_name}"
        }
        return urls
    
    def upload_to_gcs(self, local_file_path, podcast_uuid):
        """
        Sube archivo de audio a Google Cloud Storage en el directorio fijo Audios_Secretos
        """
        try:
            # Validar archivo
            file_extension, file_size = self._validate_audio_file(local_file_path)
            
            # Crear nombre del archivo con UUID en directorio fijo
            destination_name = f"{self.fixed_directory}/{podcast_uuid}.wav"
            
            # Crear blob y subir
            blob = self.bucket.blob(destination_name)
            
            print(f"☁️ Subiendo a Google Cloud Storage...")
            print(f"📁 Directorio fijo: {self.fixed_directory}")
            print(f"🆔 UUID del podcast: {podcast_uuid}")
            print(f"📊 Tamaño: {self._format_file_size(file_size)}")
            
            # Obtener content type
            content_type = self.CONTENT_TYPES.get(file_extension, 'audio/wav')
            
            # Subir archivo con metadata
            blob.upload_from_filename(
                local_file_path, 
                content_type=content_type
            )
            
            # Agregar metadata personalizada
            blob.metadata = {
                'uploaded_at': datetime.now().isoformat(),
                'original_filename': os.path.basename(local_file_path),
                'podcast_uuid': podcast_uuid,
                'directory': self.fixed_directory,
                'file_size': str(file_size),
                'generated_by': 'PodcastGenerator',
                'audio_type': 'podcast'
            }
            blob.patch()
            
            # Hacer público automáticamente
            blob.make_public()
            print("🌐 Archivo configurado como público automáticamente")
            
            # Generar múltiples formatos de URL
            urls = self.get_public_url(destination_name)
            
            print(f"✅ ¡Subido exitosamente a GCS!")
            print(f"📂 Ruta completa en bucket: gs://{self.bucket_name}/{destination_name}")
            print(f"🔗 URL principal: {urls['direct']}")
            print(f"🔗 URL alternativa: {urls['cloud_storage']}")
            
            # Verificar que el archivo sea accesible
            try:
                blob.reload()
                if blob.exists():
                    print("✅ Archivo confirmado como accesible públicamente")
                else:
                    print("⚠️ Advertencia: No se pudo confirmar la accesibilidad del archivo")
            except Exception as verify_error:
                print(f"⚠️ No se pudo verificar accesibilidad: {verify_error}")
            
            return {
                'success': True,
                'urls': urls,
                'primary_url': urls['direct'],
                'bucket_path': f"gs://{self.bucket_name}/{destination_name}",
                'filename': destination_name,
                'podcast_uuid': podcast_uuid,
                'directory': self.fixed_directory,
                'size': file_size,
                'size_formatted': self._format_file_size(file_size),
                'content_type': content_type,
                'is_public': True,
                'blob_name': destination_name
            }
            
        except Exception as e:
            print(f"❌ Error subiendo a GCS: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_url_access(self, url):
        """
        Prueba si la URL es accesible (opcional - requiere requests)
        """
        try:
            import requests
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ URL accesible: {url}")
                return True
            else:
                print(f"⚠️ URL no accesible (código {response.status_code}): {url}")
                return False
        except ImportError:
            print("💡 Instala 'requests' para verificar URLs automáticamente")
            return None
        except Exception as e:
            print(f"⚠️ Error verificando URL: {e}")
            return False
    
    def generate_and_upload_podcast(self, script_file_path, keep_local=False, test_url=False):
        """
        Genera el podcast y lo sube automáticamente a Google Cloud Storage
        """
        # Cargar el guión
        script = self.load_script_from_file(script_file_path)
        if not script:
            return None
        
        # Validar el guión
        if not self.validate_script(script):
            return None
        
        # Generar UUID único para el podcast
        podcast_uuid = self.generate_podcast_uuid()
        
        # Generar nombre de archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"podcast_temp_{timestamp}.wav"
        
        print("🎙️ Generando audio del podcast...")
        print(f"🆔 UUID del podcast: {podcast_uuid}")
        print(f"📁 Directorio de destino: {self.fixed_directory}")
        print(f"👩 Mujer → Voz: {self.speakers_config['Mujer']}")
        print(f"👨 Hombre → Voz: {self.speakers_config['Hombre']}")
        
        # Crear configuración de speakers para la API
        speaker_voice_configs = [
            types.SpeakerVoiceConfig(
                speaker="Mujer",
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.speakers_config["Mujer"]
                    )
                )
            ),
            types.SpeakerVoiceConfig(
                speaker="Hombre",
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.speakers_config["Hombre"]
                    )
                )
            )
        ]
        
        # Prompt optimizado para el podcast
        styled_prompt = f"""
        Convierte el siguiente guión de podcast en audio natural y conversacional.
        Respeta exactamente el texto proporcionado y las pausas naturales entre los speakers.
        Haz que suene profesional, fluido y como una conversación real entre dos personas.
        
        Guión del Podcast:
        {script}
        """
        
        try:
            # Generar audio con Gemini
            response = self.client.models.generate_content(
                model=self.tts_model,
                contents=styled_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=speaker_voice_configs
                        )
                    )
                )
            )
            
            # Extraer y guardar el audio localmente
            audio_data = response.candidates[0].content.parts[0].inline_data.data
            self.save_wave_file(temp_filename, audio_data)
            
            # Subir automáticamente a Google Cloud Storage
            print("\n☁️ Subiendo podcast a Google Cloud Storage automáticamente...")
            upload_result = self.upload_to_gcs(temp_filename, podcast_uuid)
            
            # Guardar información del procesamiento
            if upload_result['success']:
                info_filename = self.save_script_info(script, script_file_path, upload_result)
                
                # Probar accesibilidad de URL si se solicita
                if test_url:
                    print("\n🧪 Probando accesibilidad de la URL...")
                    self.test_url_access(upload_result['primary_url'])
                
                # Limpiar archivo temporal si no se quiere mantener local
                if not keep_local:
                    try:
                        os.remove(temp_filename)
                        print(f"🗑️ Archivo temporal eliminado: {temp_filename}")
                    except:
                        print(f"⚠️ No se pudo eliminar archivo temporal: {temp_filename}")
                
                print(f"\n🎉 ¡Podcast generado y subido exitosamente!")
                print(f"🆔 UUID permanente: {podcast_uuid}")
                print(f"📁 Directorio: {self.fixed_directory}")
                print(f"📂 Ruta completa: {upload_result['bucket_path']}")
                print(f"🎵 URL principal del podcast: {upload_result['primary_url']}")
                print(f"🔗 URL alternativa: {upload_result['urls']['cloud_storage']}")
                print(f"📄 Información guardada en: {info_filename}")
                
                # Intentar copiar URL al portapapeles
                try:
                    pyperclip.copy(upload_result['primary_url'])
                    print("📋 URL principal copiada al portapapeles")
                except ImportError:
                    print("💡 Instala 'pyperclip' para copiar URLs automáticamente")
                except Exception as e:
                    print(f"⚠️ No se pudo copiar al portapapeles: {e}")
                
                return {
                    'success': True,
                    'podcast_uuid': podcast_uuid,
                    'local_file': temp_filename if keep_local else None,
                    'gcs_result': upload_result,
                    'info_file': info_filename,
                    'urls': upload_result['urls'],
                    'primary_url': upload_result['primary_url']
                }
            else:
                print(f"❌ Error en la subida: {upload_result['error']}")
                return {'success': False, 'error': upload_result['error']}
            
        except Exception as e:
            print(f"❌ Error al generar audio: {e}")
            # Limpiar archivo temporal en caso de error
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass
            return {'success': False, 'error': str(e)}
    
    def save_script_info(self, script, original_file, upload_result):
        """
        Guarda información del guión procesado incluyendo datos de GCS
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        podcast_uuid = upload_result['podcast_uuid']
        
        info_filename = f"info_podcast_{podcast_uuid}_{timestamp}.txt"
        with open(info_filename, 'w', encoding='utf-8') as f:
            f.write("INFORMACIÓN DEL PODCAST GENERADO\n")
            f.write("="*50 + "\n\n")
            f.write(f"UUID del Podcast: {podcast_uuid}\n")
            f.write(f"Archivo de guión original: {original_file}\n")
            f.write(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("CONFIGURACIÓN DE VOCES:\n")
            f.write("• Mujer: aoede (voz femenina melodiosa)\n")
            f.write("• Hombre: puck (voz masculina animada)\n\n")
            
            f.write("INFORMACIÓN DE GOOGLE CLOUD STORAGE:\n")
            f.write(f"• Bucket: {self.bucket_name}\n")
            f.write(f"• Ruta completa: {upload_result['bucket_path']}\n")
            f.write(f"• Directorio: {upload_result['directory']}\n")
            f.write(f"• Archivo: {upload_result['filename']}\n")
            f.write(f"• UUID: {podcast_uuid}\n")
            f.write(f"• Tamaño: {upload_result['size_formatted']}\n")
            f.write(f"• Tipo: {upload_result['content_type']}\n")
            f.write(f"• Público: Sí (automático)\n\n")
            
            f.write("URLS DE ACCESO:\n")
            for url_type, url in upload_result['urls'].items():
                f.write(f"• {url_type.upper()}: {url}\n")
            f.write(f"\n• URL PRINCIPAL (recomendada): {upload_result['primary_url']}\n\n")
            
            f.write("="*50 + "\n\n")
            f.write("GUIÓN PROCESADO:\n\n")
            f.write(script)
        
        print(f"📄 Información completa guardada en: {info_filename}")
        return info_filename
    
    def get_podcast_info(self, podcast_uuid):
        """
        Obtiene información de un podcast ya subido usando su UUID
        """
        try:
            blob_name = f"{self.fixed_directory}/{podcast_uuid}.wav"
            blob = self.bucket.blob(blob_name)
            
            if blob.exists():
                blob.reload()
                urls = self.get_public_url(blob_name)
                
                return {
                    'exists': True,
                    'uuid': podcast_uuid,
                    'blob_name': blob_name,
                    'urls': urls,
                    'primary_url': urls['direct'],
                    'size': blob.size,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'content_type': blob.content_type,
                    'metadata': blob.metadata
                }
            else:
                return {'exists': False, 'uuid': podcast_uuid}
                
        except Exception as e:
            return {'exists': False, 'error': str(e), 'uuid': podcast_uuid}

def main():
    """
    Función principal
    """
    # ===== CONFIGURACIÓN =====
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  #  API key de Gemini
    GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME',"project-hackathon-2025-bucket")
    GCS_CREDENTIALS_FILE = os.getenv('GCS_CREDENTIALS_PATH', "gcp-credentials.json")
    
    print("🎙️ Generador de Podcast - Directorio Fijo: Audios_Secretos")
    print("="*60)
    
    # Validaciones iniciales
    if not GEMINI_API_KEY or GEMINI_API_KEY == "TU_API_KEY":
        print("❌ Error: Configura tu API key de Gemini")
        return
    
    if not os.path.exists(GCS_CREDENTIALS_FILE):
        print(f"❌ No se encuentra el archivo de credenciales: {GCS_CREDENTIALS_FILE}")
        print("📋 Obtén credenciales en: console.cloud.google.com")
        return
    
    try:
        # Inicializar generador
        generator = PodcastGeneratorWithGCS(
            gemini_api_key=GEMINI_API_KEY,
            bucket_name=GCS_BUCKET_NAME,
            credentials_path=GCS_CREDENTIALS_FILE
        )
        
        print(f"☁️ Bucket configurado: {GCS_BUCKET_NAME}")
        print(f"📁 Directorio fijo: Audios_Secretos")
        print("👩 Oradora femenina: aoede")
        print("👨 Orador masculino: puck")
        print("\n📋 Formato del guión:")
        print("Mujer: [texto de la mujer]")
        print("Hombre: [texto del hombre]")
        print("="*60)
        
        # Mostrar opciones
        print("\n🎯 Opciones disponibles:")
        print("1. Generar nuevo podcast")
        print("2. Consultar información de podcast existente")
        
        option = input("\n🔢 Selecciona una opción (1-2): ").strip()
        
        if option == "1":
            # Solicitar archivo de guión
            file_path = input("\n📁 Ingresa la ruta del archivo .txt con el guión: ").strip().strip('"')
            
            if not file_path:
                print("❌ No se especificó ningún archivo")
                return
            
            # Configuración de archivo local
            keep_local_input = input("💾 ¿Mantener copia local del archivo? (s/N): ").strip().lower()
            keep_local = keep_local_input in ['s', 'si', 'sí', 'y', 'yes']
            
            # Opción de probar URL
            test_url_input = input("🧪 ¿Probar accesibilidad de la URL? (s/N): ").strip().lower()
            test_url = test_url_input in ['s', 'si', 'sí', 'y', 'yes']
            
            print(f"\n⏳ Procesando...")
            print(f"📤 Se subirá automáticamente a: gs://{GCS_BUCKET_NAME}/Audios_Secretos/")
            print(f"🆔 Se generará un UUID único e inmutable para el archivo")
            
            # Generar y subir podcast
            result = generator.generate_and_upload_podcast(
                script_file_path=file_path,
                keep_local=keep_local,
                test_url=test_url
            )
            
            if result and result['success']:
                print(f"\n🎊 ¡PROCESO COMPLETADO EXITOSAMENTE!")
                print(f"🆔 UUID del podcast: {result['podcast_uuid']}")
                print(f"🌐 Tu podcast está disponible en:")
                print(f"   📎 URL Principal: {result['primary_url']}")
                
                for url_type, url in result['urls'].items():
                    if url_type != 'direct':  # Ya mostramos la principal
                        print(f"   📎 URL {url_type.title()}: {url}")
                
                if result['local_file']:
                    print(f"💾 Copia local: {result['local_file']}")
            else:
                error_msg = result['error'] if result else "Error desconocido"
                print(f"❌ No se pudo completar el proceso: {error_msg}")
        
        elif option == "2":
            # Consultar podcast existente
            podcast_uuid = input("\n🆔 Ingresa el UUID del podcast: ").strip()
            
            if not podcast_uuid:
                print("❌ No se especificó UUID")
                return
            
            print("🔍 Consultando información del podcast...")
            info = generator.get_podcast_info(podcast_uuid)
            
            if info['exists']:
                print(f"\n✅ Podcast encontrado:")
                print(f"🆔 UUID: {info['uuid']}")
                print(f"📂 Archivo: {info['blob_name']}")
                print(f"📊 Tamaño: {generator._format_file_size(info['size'])}")
                print(f"📅 Creado: {info['created']}")
                print(f"🔄 Actualizado: {info['updated']}")
                print(f"📋 Tipo: {info['content_type']}")
                print(f"\n🌐 URLs de acceso:")
                for url_type, url in info['urls'].items():
                    print(f"   📎 {url_type.upper()}: {url}")
                
                # Copiar URL principal al portapapeles
                try:
                    pyperclip.copy(info['primary_url'])
                    print("\n📋 URL principal copiada al portapapeles")
                except:
                    pass
            else:
                print(f"❌ No se encontró podcast con UUID: {podcast_uuid}")
                if 'error' in info:
                    print(f"   Error: {info['error']}")
        
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n❌ Proceso cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()