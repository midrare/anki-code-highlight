import json
import os
import pathlib
import typing

import aqt
import aqt.editor
import aqt.gui_hooks
import aqt.reviewer
import aqt.webview

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


def _find_color_scheme(*colorscheme: str) -> typing.Optional[pathlib.Path]:
    for name in colorscheme:
        if not name or not name.strip():
            continue

        p1 = ROOT_DIR / "highlightjs" / "styles" / f"{name}.css"
        if p1.exists():
            return p1
        p2 = ROOT_DIR / "highlightjs" / "styles" / f"{name}.min.css"
        if p2.exists():
            return p2

    # return ROOT_DIR / "highlightjs" / "styles" / "default.css"
    return None


def _append_color_scheme_css(web_content: aqt.webview.WebContent):
    style = None
    config = DEFAULT_CONFIG | (aqt.mw.addonManager.getConfig(__name__) or {})
    if (s := config.get("colorscheme")) and isinstance(s, str):
        style = _find_color_scheme(s)
    if not style:
        style = _find_color_scheme("default")
    if style:
        pkg = aqt.mw.addonManager.addonFromModule(__name__)
        rel = str(style.relative_to(ROOT_DIR)).replace("\\", "/")
        web_content.css.append(f"/_addons/{pkg}/{rel}")


def _append_font_size_css(web_content: aqt.webview.WebContent):
    config = DEFAULT_CONFIG | (aqt.mw.addonManager.getConfig(__name__) or {})

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


def _append_highlightjs_scripts(web_content: aqt.webview.WebContent):
    pkg = aqt.mw.addonManager.addonFromModule(__name__)

    # web_content.head += _to_script_tag(f"/_addons/{pkg}/highlightjs/highlight.js")
    # for p in (ROOT_DIR / "highlightjs" / "languages").glob("*.js"):
    #     rel = str(p.relative_to(ROOT_DIR)).replace("\\", "/")
    #     web_content.head += _to_script_tag(f"/_addons/{pkg}/{rel}")

    wbp = aqt.webview.AnkiWebView.webBundlePath

    hl_url = wbp(f"/_addons/{pkg}/highlightjs/highlight.js")

    hl_lang_urls = []
    with os.scandir(ROOT_DIR / "highlightjs" / "languages") as it:
        for e in it:
            if e.name.lower().endswith(".js") and e.is_file():
                url = wbp(f"/_addons/{pkg}/highlightjs/languages/{e.name}")
                hl_lang_urls.append(url)

    web_content.head += f"""
    <script>
        async function _loadScriptByUrl(url) {{
            return new Promise((resolve, reject) => {{
                let script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.async = true;

                script.onload = resolve;
                script.onerror = reject;

                document.head.appendChild(script);
            }})
        }}

        var _hlLoad = null;
        async function _loadScripts() {{
            if ((typeof _hlLoad === "undefined") || _hlLoad === null) {{
                // XXX antipattern https://stackoverflow.com/a/45351652
                _hlLoad = new Promise(async (resolve, reject) => {{
                    await _loadScriptByUrl({json.dumps(hl_url)});
                    var langs = {json.dumps(hl_lang_urls)};
                    await Promise.allSettled(langs.map(_loadScriptByUrl));
                    resolve();
                }})
            }}

            return _hlLoad;
        }}

        async function _highlight() {{
            await _loadScripts();
            document.querySelectorAll('pre code:not(.hljs)').forEach(el => {{
                hljs.highlightElement(el);
            }});
        }}


        _loadScripts();

        if (typeof onUpdateHook !== 'undefined') {{
            onUpdateHook.push(function() {{
                _highlight();
            }});
        }} else {{
            document.addEventListener("DOMContentLoaded", function() {{
                var MutationObserver = (window.MutationObserver
                    || window.WebKitMutationObserver);
                globalThis._hlObserver = new MutationObserver(function(mut, obs) {{
                    _highlight();
                    /* obs.disconnect(); */
                }});
                globalThis._hlObserver.observe(document.getElementById("qa"), {{
                    subtree: true,
                    childList: true,
                }});
            }});
        }}
    </script>"""


def _on_webview_will_set_content(
        web_content: aqt.webview.WebContent, context: typing.Optional[object]):
    if not isinstance(context,
                      (aqt.reviewer.Reviewer, aqt.previewer.BrowserPreviewer)):
        return

    _append_color_scheme_css(web_content)
    _append_font_size_css(web_content)
    _append_highlightjs_scripts(web_content)


def init_addon():
    aqt.mw.addonManager.setWebExports(__name__, r".*\.(css|js|bmp|png)")
    aqt.gui_hooks.webview_will_set_content.append(_on_webview_will_set_content)
