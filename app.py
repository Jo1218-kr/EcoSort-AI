"""EcoSort AI - Gradio 화면 및 실행 코드."""

from __future__ import annotations

import argparse
import inspect
import os

import gradio as gr

import core


# 본인 PC에서만 실제 키를 입력하세요.
# 학생들에게는 실행 후 생성되는 HTTPS 주소를 공유하세요.
OPENAI_API_KEY= ""
core.configure_api_key(OPENAI_API_KEY)


CSS = """
.gradio-container {
    max-width: 720px !important;
    margin: auto;
}
#status {
    font-size: 1.05rem;
    font-weight: 600;
    padding: 6px 2px;
}
"""

HEADER = """
# ♻️ EcoSort AI

카메라에 물건을 비추면 예상 분류와 분리배출 방법을 안내합니다.

사진만으로 재질을 확정할 수 없으므로 제품 표시와 지역 기준도 확인하세요.
"""

HOWTO = """
### 자동 스캔
1. 카메라 권한을 허용하세요.
2. 카메라 화면의 Record 또는 시작 버튼을 누르세요.
3. 물건 하나를 중앙에 놓고 휴대폰을 잠시 고정하세요.
4. 같은 장면은 자동 재호출을 생략합니다.
5. 자동 인식이 안 되면 사진 업로드로 확인하세요.

### 사진으로 인식
1. 사진 선택 영역을 누르세요.
2. 갤러리 사진을 선택하세요.
3. 사진 미리보기가 표시되면 분석하기를 누르세요.

### 초기화와 호출 제한
초기화는 두 탭의 사진·결과와 장면 감지 상태를 지웁니다.
호출 횟수와 대기 시간은 유지됩니다.
자동 스캔과 사진 탭은 같은 호출 예산을 공유합니다.

### 사진 처리
실제 분석에서는 사진이 Gradio 서버를 거쳐 OpenAI API로 전송됩니다.
앱은 원본 사진을 별도 기록하지 않지만 Gradio 임시 파일과
브라우저 캐시가 생길 수 있습니다.
store=False는 API 응답 저장 설정이며, 공급자 데이터 정책까지
무보존으로 보장하지는 않습니다.
"""


def _appearance() -> dict:
    return {
        "theme": gr.themes.Soft(primary_hue="green"),
        "css": CSS,
    }


def _appearance_in_launch() -> bool:
    """Gradio 버전에 맞는 스타일 설정 위치를 확인합니다."""
    return "theme" in inspect.signature(gr.Blocks.launch).parameters


def _camera_kwargs() -> dict:
    """지원되는 버전에서는 후면 카메라를 우선 요청합니다."""
    params = inspect.signature(gr.Image.__init__).parameters
    constraints = {
        "video": {
            "facingMode": {"ideal": "environment"},
        }
    }

    if "webcam_options" in params:
        try:
            from gradio.components.image import WebcamOptions

            return {
                "webcam_options": WebcamOptions(
                    mirror=False,
                    constraints=constraints,
                )
            }
        except ImportError:
            pass

    kwargs = {}

    if "webcam_constraints" in params:
        kwargs["webcam_constraints"] = constraints

    if "mirror_webcam" in params:
        kwargs["mirror_webcam"] = False

    return kwargs


def scan(img, st):
    return core.process_frame(img, st, force=False)


def scan_now(img, st):
    print("수동 인식 버튼 요청 도착", flush=True)
    print("이미지 있음:", img is not None, flush=True)

    result = core.process_frame(img, st, force=True)

    print("처리 결과:", result[0], flush=True)
    return result


def reset(st):
    message = "📷 초기화했습니다. 호출 횟수와 대기 시간은 유지됩니다."

    return (
        None,
        message,
        "",
        core.reset_scene(st),
        None,
        message,
        "",
    )


def build_ui() -> gr.Blocks:
    blocks_kwargs = {"title": "EcoSort AI"}

    # Gradio 5에서는 Blocks, 6에서는 launch에 스타일을 전달합니다.
    if not _appearance_in_launch():
        blocks_kwargs.update(_appearance())

    with gr.Blocks(**blocks_kwargs) as demo:
        gr.Markdown(HEADER)

        if core.MOCK:
            gr.Markdown(
                "> 🧪 고정 예제 데모 모드입니다. "
                "현재 사진을 AI로 분석하지 않습니다."
            )
        elif not core.has_api_key():
            gr.Markdown(
                "> ⚠️ app.py 상단의 OPENAI_API_KEY에 "
                "실제 키를 입력하고 서버를 다시 실행하세요."
            )

        # 두 탭이 같은 세션 호출 예산을 사용합니다.
        state = gr.State(core.new_state())

        with gr.Tabs():
            with gr.Tab("📷 자동 스캔"):
                cam = gr.Image(
                    sources=["webcam"],
                    streaming=True,
                    type="pil",
                    label="카메라",
                    height=360,
                    **_camera_kwargs(),
                )

                status = gr.Markdown(
                    "📷 카메라를 허용하고 Record 버튼을 눌러 시작하세요.",
                    elem_id="status",
                )
                result = gr.Markdown()

                with gr.Row():
                    btn_now = gr.Button(
                        "🎯 지금 인식",
                        variant="primary",
                    )
                    btn_reset = gr.Button("🔄 초기화")

            with gr.Tab("🖼️ 사진으로 인식"):
                photo = gr.Image(
                    sources=["upload"],
                    type="pil",
                    label="사진 선택 또는 촬영",
                    height=360,
                )

                gr.Markdown(
                    "카메라 선택지가 없으면 기본 카메라 앱에서 "
                    "촬영한 뒤 갤러리 사진을 선택하세요."
                )

                status2 = gr.Markdown()
                result2 = gr.Markdown()

                btn_photo = gr.Button(
                    "분석하기",
                    variant="primary",
                )

            with gr.Tab("ℹ️ 사용법"):
                gr.Markdown(HOWTO)

        # 분석과 초기화가 동시에 상태를 변경하지 않도록 직렬 처리합니다.
        events = {
            "concurrency_limit": 1,
            "concurrency_id": "ecosort_scan",
            "show_progress": "hidden",
        }

        cam.stream(
            scan,
            inputs=[cam, state],
            outputs=[status, result, state],
            stream_every=1.0,
            time_limit=None,
            **events,
        )

        btn_now.click(
            scan_now,
            inputs=[cam, state],
            outputs=[status, result, state],
            **events,
        )

        btn_photo.click(
            scan_now,
            inputs=[photo, state],
            outputs=[status2, result2, state],
            **events,
        )

        btn_reset.click(
            reset,
            inputs=[state],
            outputs=[
                cam,
                status,
                result,
                state,
                photo,
                status2,
                result2,
            ],
            **events,
        )

    return demo


def main() -> None:
    parser = argparse.ArgumentParser(description="EcoSort AI")

    parser.add_argument(
        "--host",
        default=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "7860")),
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="휴대폰 접속용 임시 HTTPS 링크 생성",
    )
    parser.add_argument("--ssl-cert", help="HTTPS 인증서 경로")
    parser.add_argument("--ssl-key", help="HTTPS 개인키 경로")

    args = parser.parse_args()

    if bool(args.ssl_cert) != bool(args.ssl_key):
        parser.error("--ssl-cert와 --ssl-key는 함께 지정하세요.")

    demo = build_ui()
    demo.queue(max_size=30)

    launch_kwargs = {
        "server_name": args.host,
        "server_port": args.port,
        "share": args.share,
    }

    if _appearance_in_launch():
        launch_kwargs.update(_appearance())

    if args.ssl_cert and args.ssl_key:
        launch_kwargs.update(
            ssl_certfile=args.ssl_cert,
            ssl_keyfile=args.ssl_key,
            ssl_verify=False,
        )

    password = os.getenv("ECOSORT_PASSWORD")

    if password:
        launch_kwargs["auth"] = ("ecosort", password)

    demo.launch(**launch_kwargs)


if __name__ == "__main__":
    main()