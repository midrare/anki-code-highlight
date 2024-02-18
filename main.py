import pathlib
import typing

import aqt
import aqt.editor
import aqt.gui_hooks
import aqt.reviewer

ROOT_DIR: typing.Final[pathlib.Path] = \
    pathlib.Path(__file__).parent.absolute()

UserConfig = typing.TypedDict(
    'UserConfig', {
        'colorscheme': typing.Optional[str],
        'fontsize': typing.Union[None, str, int, float],
    })

DEFAULT_CONFIG: typing.Final[UserConfig] = {
    'colorscheme': None,
    'fontsize': "0.7em",
}


def _on_webview_will_set_content(
        web_content: aqt.webview.WebContent, context: typing.Optional[object]):
    if not isinstance(context,
                      (aqt.reviewer.Reviewer, aqt.previewer.BrowserPreviewer)):
        return

    pkg = aqt.mw.addonManager.addonFromModule(__name__)
    config = DEFAULT_CONFIG | (aqt.mw.addonManager.getConfig(__name__) or {})

    style = config.get("colorscheme") or "default"
    for style in [config.get("colorscheme") or "default", "default"]:
        p = sorted((ROOT_DIR / "highlightjs" / "styles").rglob(f"{style}.css"))
        if p:
            rel = str(p[0].relative_to(ROOT_DIR)).replace("\\", "/")
            web_content.css.append(f"/_addons/{pkg}/{rel}")
            break

    web_content.js.append(f"/_addons/{pkg}/highlightjs/highlight.js")
    for p in (ROOT_DIR / "highlightjs" / "languages").glob("*.js"):
        rel = str(p.relative_to(ROOT_DIR)).replace("\\", "/")
        web_content.js.append(f"/_addons/{pkg}/{rel}")

    font_size = config.get("fontsize")
    if not font_size or str(font_size).lower() == "default":
        font_size = "0.7em"

    web_content.head += f"""
    <style>
        pre code.hljs {{
            font-size: {font_size}
        }}
    </style>
    """

    web_content.head += """
    <script>
        if (typeof onUpdateHook !== 'undefined') {
            onUpdateHook.push(function() {
                if (typeof globalThis.hljs !== 'undefined') {
                    globalThis.hljs.highlightAll();
                }
            });
        }

        document.addEventListener("DOMContentLoaded", function(){
            if (typeof globalThis.hljs !== 'undefined') {
                globalThis.hljs.highlightAll();
            }
        });

        MutationObserver = (window.MutationObserver
                || window.WebKitMutationObserver);
        var observer = new MutationObserver(function(mutations, observer) {
            if (typeof globalThis.hljs !== 'undefined') {
                globalThis.hljs.highlightAll();
            }
        });

        observer.observe(document, {
            subtree: true,
            childList: true,
        });
    </script>"""


def init_addon():
    aqt.mw.addonManager.setWebExports(__name__, r".*\.(css|js|bmp|png)")
    aqt.gui_hooks.webview_will_set_content.append(_on_webview_will_set_content)
