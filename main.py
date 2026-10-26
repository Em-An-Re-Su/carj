import base64
import html
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

st.set_page_config(
    page_title="Auto3D Lab",
    page_icon="🚘",
    layout="wide",
)

TRIPOSR_URL = "https://huggingface.co/spaces/stabilityai/TripoSR"
MAX_IMAGE_SIZE = 20 * 1024 * 1024
MAX_MODEL_SIZE = 80 * 1024 * 1024

st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #101827, #294967);
    color: white;
    padding: 26px;
    border-radius: 18px;
    margin-bottom: 24px;
}
.hero h1 { margin: 0; font-size: 2.2rem; }
.hero p { color: #dce7f3; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🚘 Auto3D Lab</h1>
    <p>자동차 사진에서 3D 모델을 만들고 360도로 관찰하세요.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("자동차 정보")
    manufacturer = st.text_input(
        "제조사", placeholder="예: Hyundai"
    )
    model_name = st.text_input(
        "차종", placeholder="예: IONIQ 5"
    )
    year = st.text_input(
        "연식 (선택)", placeholder="예: 2025"
    )
    background = st.color_picker(
        "뷰어 배경색", "#e9edf2"
    )
    auto_rotate = st.checkbox(
        "자동 회전", value=True
    )

car_name = " ".join(
    x.strip()
    for x in [manufacturer, model_name, year]
    if x.strip()
)

st.subheader("1. 자동차 사진 업로드")

photo = st.file_uploader(
    "차량 전체가 선명하게 나온 사진을 선택하세요.",
    type=["jpg", "jpeg", "png", "webp"],
    key="car_photo",
)

if photo:
    image_bytes = photo.getvalue()

    if len(image_bytes) > MAX_IMAGE_SIZE:
        st.error("사진은 20MB 이하로 업로드해 주세요.")
    else:
        try:
            image = Image.open(photo)
            st.image(
                image,
                caption="3D 변환에 사용할 참고 사진",
                width=600,
            )
        except Exception:
            st.error("이미지를 읽을 수 없습니다.")

st.subheader("2. TripoSR로 3D 모델 생성")

st.info(
    "무료 오픈소스 모델의 공개 데모를 이용합니다. "
    "생성은 외부 서비스에서 처리되므로 데모 상태와 "
    "대기열에 따라 이용이 제한될 수 있습니다."
)

st.link_button(
    "TripoSR 공식 3D 생성기 열기 ↗",
    TRIPOSR_URL,
    type="primary",
    use_container_width=True,
)

with st.expander("앱 안에서 생성기 열기"):
    st.caption(
        "공개 데모가 iframe 표시를 허용하지 않거나 "
        "오류 상태라면 위의 외부 링크를 이용하세요."
    )
    components.iframe(
        TRIPOSR_URL,
        height=700,
        scrolling=True,
    )

st.markdown("""
**생성 순서**
1. 위 생성기에서 자동차 사진을 업로드합니다.
2. 배경 제거 옵션 등을 확인하고 Generate를 실행합니다.
3. 결과를 GLB 형식으로 다운로드합니다.
4. 아래 업로드란에서 GLB 파일을 불러옵니다.
""")

if car_name:
    st.markdown(
        f"**입력한 차종:** {html.escape(car_name)}"
    )
    q = quote(car_name + " official specifications")
    st.markdown(
        f"[차종 제원 검색](https://www.google.com/search?q={q})"
    )

st.divider()
st.subheader("3. 생성한 3D 모델 불러오기")

model_file = st.file_uploader(
    "TripoSR에서 다운로드한 GLB 파일을 선택하세요.",
    type=["glb"],
    key="model_file",
)

if model_file:
    model_bytes = model_file.getvalue()

    if len(model_bytes) > MAX_MODEL_SIZE:
        st.error("모델 파일은 80MB 이하로 업로드해 주세요.")
    elif len(model_bytes) < 4 or model_bytes[:4] != b"glTF":
        st.error("올바른 GLB 바이너리 파일이 아닙니다.")
    else:
        st.success("3D 모델을 불러왔습니다.")

        encoded = base64.b64encode(
            model_bytes
        ).decode("ascii")

        safe_bg = html.escape(background, quote=True)
        rotation = "auto-rotate" if auto_rotate else ""
        safe_name = html.escape(
            car_name or "자동차 3D 모델",
            quote=True,
        )

        viewer = f"""
        <!doctype html>
        <html>
        <head>
          <meta name="viewport"
                content="width=device-width, initial-scale=1">
          <script type="module"
            src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js">
          </script>
          <style>
            html, body {{
              margin: 0;
              padding: 0;
              background: {safe_bg};
            }}
            model-viewer {{
              width: 100%;
              height: 580px;
              background: {safe_bg};
              --poster-color: {safe_bg};
            }}
          </style>
        </head>
        <body>
          <model-viewer
            src="data:model/gltf-binary;base64,{encoded}"
            alt="{safe_name}"
            camera-controls
            {rotation}
            auto-rotate-delay="1000"
            rotation-per-second="18deg"
            shadow-intensity="1"
            exposure="1"
            environment-image="neutral"
            touch-action="pan-y">
          </model-viewer>
        </body>
        </html>
        """

        components.html(
            viewer,
            height=600,
            scrolling=False,
        )

        st.download_button(
            "GLB 모델 다운로드",
            data=model_bytes,
            file_name="car_model.glb",
            mime="model/gltf-binary",
        )

        st.caption(
            "마우스로 드래그해 회전하고 휠로 확대·축소하세요."
        )

st.divider()
st.caption(
    "Auto3D Lab · TripoSR은 단일 사진 기반 재구성 모델입니다. "
    "결과는 실제 차량의 정밀 설계도와 다를 수 있습니다."
)
