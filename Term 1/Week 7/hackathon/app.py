import base64
import io
from collections import Counter

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------

st.set_page_config(
    page_title="Flower Welfare",
    page_icon="🌼",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }
    .app-title {
        font-size: 2.4rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 1.05rem;
        opacity: 0.75;
        margin-bottom: 1.5rem;
    }
    .result-card {
        border: 1px solid rgba(120,120,120,0.25);
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        min-height: 118px;
    }
    .result-number {
        font-size: 2rem;
        font-weight: 750;
        line-height: 1.1;
    }
    .result-label {
        font-size: 0.95rem;
        opacity: 0.75;
        margin-top: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">🌼 Flower Welfare </div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">'
    'Upload a flower photo. The model detects visible flowers and estimates whether they look Healthy or Wilted.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

with st.sidebar:
    st.header("Roboflow settings")

    api_key = st.text_input(
        "Private API key",
        type="password",
        help="Find this in Roboflow Settings → API Keys.",
    )

    model_id = st.text_input(
        "Model ID",
        value="hackathon-flowers/1",
        help="Format: project-name/version, for example hackathon-flowers/1.",
    )

    confidence_threshold = st.slider(
        "Confidence threshold",
        min_value=20,
        max_value=90,
        value=45,
        step=5,
        help="Higher values reduce weak detections. Lower values find more flowers.",
    ) / 100.0

    deduplicate = st.checkbox(
        "Remove overlapping duplicate boxes",
        value=True,
        help="Helps avoid counting the same flower more than once.",
    )

st.info(
    "The result is an estimate of **visible flower condition**, not a diagnosis of the health of the whole plant."
)


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def intersection_over_union(a, b):
    """IoU for two Roboflow-style center-x/center-y boxes."""
    ax1 = a["x"] - a["width"] / 2
    ay1 = a["y"] - a["height"] / 2
    ax2 = a["x"] + a["width"] / 2
    ay2 = a["y"] + a["height"] / 2

    bx1 = b["x"] - b["width"] / 2
    by1 = b["y"] - b["height"] / 2
    bx2 = b["x"] + b["width"] / 2
    by2 = b["y"] + b["height"] / 2

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)
    intersection = iw * ih

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - intersection

    return intersection / union if union > 0 else 0.0


def remove_overlaps(predictions, iou_threshold=0.55):
    """
    Class-agnostic NMS:
    if two boxes heavily overlap, keep the one with higher confidence.
    Useful when the model puts multiple boxes on one flower.
    """
    ordered = sorted(
        predictions,
        key=lambda p: float(p.get("confidence", 0)),
        reverse=True,
    )

    kept = []

    for candidate in ordered:
        duplicate = False

        for existing in kept:
            if intersection_over_union(candidate, existing) >= iou_threshold:
                duplicate = True
                break

        if not duplicate:
            kept.append(candidate)

    return kept


def run_roboflow(image, api_key, model_id):
    """
    Calls Roboflow's hosted object-detection endpoint directly.
    No inference-sdk is required.
    """
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=95)

    encoded = base64.b64encode(buffer.getvalue())

    url = f"https://detect.roboflow.com/{model_id.strip()}"
    params = {
        "api_key": api_key.strip(),
        "format": "json",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(
        url,
        params=params,
        data=encoded,
        headers=headers,
        timeout=90,
    )

    if not response.ok:
        raise RuntimeError(
            f"Roboflow returned HTTP {response.status_code}: {response.text[:500]}"
        )

    result = response.json()

    if not isinstance(result, dict):
        raise RuntimeError("Unexpected response from Roboflow.")

    predictions = result.get("predictions", [])

    if not isinstance(predictions, list):
        predictions = []

    return predictions


def draw_predictions(image, predictions):
    output = image.convert("RGB").copy()
    draw = ImageDraw.Draw(output)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    for pred in predictions:
        label = str(pred.get("class", "Flower"))
        confidence = float(pred.get("confidence", 0))

        x = float(pred.get("x", 0))
        y = float(pred.get("y", 0))
        width = float(pred.get("width", 0))
        height = float(pred.get("height", 0))

        left = x - width / 2
        top = y - height / 2
        right = x + width / 2
        bottom = y + height / 2

        if label.lower() == "healthy":
            box_color = "green"
        elif label.lower() == "wilted":
            box_color = "red"
        else:
            box_color = "blue"

        draw.rectangle(
            [left, top, right, bottom],
            outline=box_color,
            width=4,
        )

        text = f"{label} {confidence * 100:.0f}%"

        try:
            text_box = draw.textbbox((0, 0), text, font=font)
            text_w = text_box[2] - text_box[0]
            text_h = text_box[3] - text_box[1]
        except Exception:
            text_w = len(text) * 8
            text_h = 16

        label_top = max(0, top - text_h - 10)

        draw.rectangle(
            [left, label_top, left + text_w + 10, label_top + text_h + 8],
            fill=box_color,
        )
        draw.text(
            (left + 5, label_top + 4),
            text,
            fill=(255, 255, 255),
            font=font,
        )

    return output


def metric_card(number, label):
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-number">{number}</div>
            <div class="result-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# APP
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload a flower image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    left, right = st.columns([1, 1])

    with left:
        st.subheader("Original")
        st.image(image, use_container_width=True)

    analyze = st.button(
        "Analyze flower image",
        type="primary",
        use_container_width=True,
    )

    if analyze:
        if not api_key.strip():
            st.error("Enter your Roboflow API key in the sidebar.")
            st.stop()

        if not model_id.strip() or "/" not in model_id:
            st.error("Enter a model ID such as `hackathon-flowers/1`.")
            st.stop()

        with st.spinner("Analyzing the image..."):
            try:
                raw_predictions = run_roboflow(image, api_key, model_id)
            except Exception as exc:
                st.error(
                    "The Roboflow request failed. Check your API key and model ID."
                )
                st.code(str(exc))
                st.stop()

        predictions = [
            p for p in raw_predictions
            if float(p.get("confidence", 0)) >= confidence_threshold
        ]

        if deduplicate:
            predictions = remove_overlaps(predictions)

        annotated = draw_predictions(image, predictions)

        with right:
            st.subheader("Detected flowers")
            st.image(annotated, use_container_width=True)

        healthy = sum(
            1 for p in predictions
            if str(p.get("class", "")).strip().lower() == "healthy"
        )
        wilted = sum(
            1 for p in predictions
            if str(p.get("class", "")).strip().lower() == "wilted"
        )

        total = healthy + wilted

        st.subheader("Summary")

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(total, "Flowers detected")

        with c2:
            metric_card(healthy, "Healthy")

        with c3:
            metric_card(wilted, "Wilted")

        if total > 0:
            visible_score = healthy / total * 100

            st.write("**Visible flower condition score**")
            st.progress(int(round(visible_score)))
            st.caption(
                f"{visible_score:.0f}% of the detected flowers were classified as Healthy."
            )
        else:
            st.warning(
                "No Healthy or Wilted flowers were detected above the current confidence threshold."
            )

        if predictions:
            with st.expander("See individual predictions"):
                for i, pred in enumerate(predictions, start=1):
                    label = pred.get("class", "Unknown")
                    confidence = float(pred.get("confidence", 0)) * 100
                    st.write(f"{i}. **{label}** — {confidence:.1f}% confidence")


st.divider()

st.caption(
    "SDG 15 — Life on Land | Custom computer-vision model trained with Roboflow"
)