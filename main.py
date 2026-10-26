# main.py
import base64
import html
import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import quote
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="Auto3D Lab",
    page_icon="🚘",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}
.hero {
    padding: 25px;
    border-radius: 18px;
    background: linear-gradient(120deg, #101827, #253b58);
    color: white;
    margin-bottom: 22px;
}
.hero h1 { margin: 0; font-size: 2.2rem; }
.hero p { color: #d5dfed; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🚘 Auto3D Lab</h1>
    <p>자동차 사진과 차종 정보를 바탕으로 자료를 탐색하고,
    3D 모델을 관찰하는 공간</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("자동차 정보")
    make = st.text_input("제조사", placeholder="예: Hyundai")
    model = st.text_input("차종", placeholder="예: IONIQ 5")
    year = st.text_input("연식 (선택)", placeholder="예: 2025")
    color = st.color_picker("뷰어 배경색", "#e9edf2")
    auto_rotate = st.checkbox("자동 회전", value=True)
    st.caption("실제 차량과 모델의 일치 여부는 별도로 확인해야 합니다.")

st.subheader("1. 참고 사진 업로드")
photos = st.file_uploader(
    "자동차 사진을 올려 주세요. 여러 방향의 사진을 권장합니다.",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
)

if photos:
    cols = st.columns(min(len(photos), 4))
    for i, photo in enumerate(photos):
        try:
            image = Image.open(BytesIO(photo.getvalue()))
            with cols[i % len(cols)]:
                st.image(image, caption=photo.name, use_container_width=True)
        except Exception:
            st.warning(f"{photo.name}: 이미지를 읽을 수 없습니다.")

car_name = " ".join(x for x in [make, model, year] if x).strip()

st.subheader("2. 차종 자료 탐색")
if car_name:
    q = quote(car_name + " 3D model GLB")
    st.markdown(
        f"- [3D 모델 검색하기](https://www.google.com/search?q={q})\n"
        f"- [Sketchfab에서 검색하기](https://sketchfab.com/search?type=models&q={quote(car_name)})\n"
        f"- [일반 이미지 검색하기](https://www.google.com/search?tbm=isch&q={quote(car_name + ' car front side rear')})"
    )
else:
    st.info("왼쪽에서 제조사와 차종을 입력하면 검색 링크가 표시됩니다.")

st.divider()
st.subheader("3. 3D 모델 불러오기")

model_file = st.file_uploader(
    "3D 모델 파일 (.glb)",
    type=["glb"],
    key="glb_upload",
    help="다운로드하거나 별도 생성한 GLB 모델을 업로드하세요.",
)

if model_file:
    data = model_file.getvalue()

    if len(data) > 80 * 1024 * 1024:
        st.error("파일이 너무 큽니다. 80MB 이하의 GLB 파일을 사용해 주세요.")
    else:
        encoded = base64.b64encode(data).decode("ascii")
        bg = html.escape(color, quote=True)
        rotation = "auto-rotate" if auto_rotate else ""

        viewer_html = f"""
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
              margin: 0; padding: 0;
              background: {bg};
              font-family: sans-serif;
            }}
            model-viewer {{
              width: 100%; height: 570px;
              background: {bg};
              --poster-color: {bg};
            }}
          </style>
        </head>
        <body>
          <model-viewer
            src="data:model/gltf-binary;base64,{encoded}"
            camera-controls
            {rotation}
            auto-rotate-delay="1000"
            rotation-per-second="18deg"
            touch-action="pan-y"
            shadow-intensity="1"
            exposure="1"
            environment-image="neutral"
            alt="업로드한 자동차 3D 모델">
          </model-viewer>
        </body>
        </html>
        """

        components.html(viewer_html, height=590, scrolling=False)

        st.success("3D 모델을 불러왔습니다.")
        st.caption(
            "마우스로 드래그하면 회전하고, 휠이나 핀치 제스처로 "
            "확대·축소할 수 있습니다."
        )

        st.download_button(
            "원본 GLB 파일 저장",
            data=data,
            file_name="car_model.glb",
            mime="model/gltf-binary",
        )

else:
    st.info(
        "아직 3D 모델이 없습니다. 위의 자료 검색에서 모델을 확보하거나 "
        "3D 생성 서비스로 만든 GLB 파일을 업로드하세요."
    )

    if photos:
        st.markdown("**업로드한 사진을 바탕으로 모델을 생성하려면**")
        st.write(
            "이미지 기반 3D 생성 API를 연결해야 합니다. "
            "현재 버전은 사진을 자동으로 3D 메시로 변환하거나 "
            "차체 형상을 자동 보정하지 않습니다."
        )

st.divider()
st.caption(
    "Auto3D Lab · 참고 자료의 저작권과 모델 라이선스를 확인한 뒤 사용하세요."
)
