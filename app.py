# app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Optimizador Fotográfico Pro",
    page_icon="📸",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .image-container {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<h1 class="main-header">📸 Optimizador Fotográfico Pro</h1>', unsafe_allow_html=True)

# Sidebar para controles
st.sidebar.title("⚙️ Controles de Optimización")

# Subida de imagen
uploaded_file = st.sidebar.file_uploader(
    "📤 Sube tu imagen", 
    type=['jpg', 'png', 'jpeg', 'webp'],
    help="Formatos soportados: JPG, PNG, JPEG, WEBP"
)

# Inicializar variables de estado
if 'original_image' not in st.session_state:
    st.session_state.original_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

def process_image(image, adjustments):
    """Procesa la imagen con los ajustes seleccionados"""
    try:
        # Convertir a PIL Image si es necesario
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Aplicar ajustes
        if adjustments['brightness'] != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(adjustments['brightness'])
        
        if adjustments['contrast'] != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(adjustments['contrast'])
        
        if adjustments['sharpness'] != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(adjustments['sharpness'])
        
        if adjustments['saturation'] != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(adjustments['saturation'])
        
        # Aplicar filtros
        if adjustments['blur'] > 0:
            image = image.filter(ImageFilter.GaussianBlur(adjustments['blur']))
        
        if adjustments['enhance_edges']:
            image = image.filter(ImageFilter.EDGE_ENHANCE)
        
        # Redimensionar si es necesario
        if adjustments['resize'] != 100:
            width, height = image.size
            new_width = int(width * adjustments['resize'] / 100)
            new_height = int(height * adjustments['resize'] / 100)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return image

if uploaded_file is not None:
    # Cargar y mostrar imagen original
    image = Image.open(uploaded_file)
    st.session_state.original_image = image
    
    # Mostrar información de la imagen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Formato:** {image.format}")
    with col2:
        st.info(f"**Tamaño:** {image.size[0]}x{image.size[1]} px")
    with col3:
        st.info(f"**Modo:** {image.mode}")
    
    # Controles de ajuste en sidebar
    st.sidebar.subheader("🎛️ Ajustes Básicos")
    
    brightness = st.sidebar.slider("Brillo", 0.0, 2.0, 1.0, 0.1)
    contrast = st.sidebar.slider("Contraste", 0.0, 2.0, 1.0, 0.1)
    sharpness = st.sidebar.slider("Nitidez", 0.0, 2.0, 1.0, 0.1)
    saturation = st.sidebar.slider("Saturación", 0.0, 2.0, 1.0, 0.1)
    
    st.sidebar.subheader("🔧 Efectos Avanzados")
    blur = st.sidebar.slider("Desenfoque", 0.0, 5.0, 0.0, 0.1)
    enhance_edges = st.sidebar.checkbox("Realzar bordes")
    resize = st.sidebar.slider("Redimensionar (%)", 10, 200, 100, 5)
    
    # Presets rápidos
    st.sidebar.subheader("🚀 Presets Rápidos")
    col1, col2, col3 = st.sidebar.columns(3)
    
    with col1:
        if st.button("Vibrante"):
            brightness, contrast, saturation = 1.1, 1.3, 1.4
    
    with col2:
        if st.button("Suave"):
            brightness, contrast, blur = 1.2, 0.9, 0.8
    
    with col3:
        if st.button("Nitidez Max"):
            sharpness, contrast, enhance_edges = 1.8, 1.2, True
    
    # Procesar imagen
    adjustments = {
        'brightness': brightness,
        'contrast': contrast,
        'sharpness': sharpness,
        'saturation': saturation,
        'blur': blur,
        'enhance_edges': enhance_edges,
        'resize': resize
    }
    
    processed_image = process_image(image.copy(), adjustments)
    st.session_state.processed_image = processed_image
    
    # Mostrar imágenes lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📷 Imagen Original")
        st.image(image, use_column_width=True, caption=f"Original - {image.size[0]}x{image.size[1]}")
    
    with col2:
        st.markdown("### ✨ Imagen Optimizada")
        st.image(processed_image, use_column_width=True, 
                caption=f"Procesada - {processed_image.size[0]}x{processed_image.size[1]}")
    
    # Descargar imagen procesada
    st.subheader("💾 Descargar Imagen Optimizada")
    
    # Convertir a bytes para descarga
    buf = BytesIO()
    processed_image.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.download_button(
            label="📥 Descargar Imagen Optimizada",
            data=byte_im,
            file_name=f"optimizada_{uploaded_file.name}",
            mime="image/jpeg",
            use_container_width=True
        )

else:
    # Pantalla de bienvenida
    st.markdown("""
    ## 🎯 Bienvenido al Optimizador Fotográfico
    
    **Características principales:**
    - ✅ Ajuste de brillo, contraste y saturación
    - ✅ Mejora de nitidez y realce de bordes
    - ✅ Redimensionamiento inteligente
    - ✅ Efectos de desenfoque
    - ✅ Presets rápidos
    - ✅ Descarga inmediata
    
    **Cómo usar:**
    1. Sube una imagen usando el panel izquierdo
    2. Ajusta los parámetros según tus necesidades
    3. Descarga el resultado optimizado
    """)
    
    # Ejemplo de imagen
    st.image("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400", 
             caption="Ejemplo - Sube tu imagen para comenzar", width=300)

# Footer
st.markdown("---")
st.markdown("*Creado con Streamlit y Python • Optimizador Fotográfico Pro*")