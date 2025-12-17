from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, DictProperty
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
import japanize_kivy

from typing import List, Tuple, Set
import json
import re
import shutil
import logging

try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None  # Pillow未インストール時のフォールバック

# Pillowのデバッグログを抑制
logging.getLogger("PIL").setLevel(logging.INFO)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.INFO)


# キーコードを日本語化する辞書
KEYCODE_JP = {
    'KC_APP': 'アプリ',
    'KC_BRID': '輝度-',
    'KC_BRIU': '輝度+',
    'KC_BSLS': '\\',
    'KC_BSPC': 'BackSpace',
    'KC_CAPS': 'CapsLock',
    'KC_COMM': ',',
    'KC_DEL': 'Delete',
    'KC_DOT': '.',
    'KC_DOWN': '↓',
    'KC_EJCT': 'イジェクト',
    'KC_END': 'End',
    'KC_ENT': 'Enter',
    'KC_EQL': '=',
    'KC_ESC': 'Esc',
    'KC_GRV': '`',
    'KC_HOME': 'Home',
    'KC_INS': 'Insert',
    'KC_LALT': '左Alt',
    'KC_LBRC': '[',
    'KC_LCTL': '左Ctrl',
    'KC_LEFT': '←',
    'KC_LGUI': '左Win',
    'KC_LSFT': '左Shift',
    'KC_MINS': '-',
    'KC_MNXT': '次の曲',
    'KC_MPLY': '再生/一時停止',
    'KC_MPRV': '前の曲',
    'KC_MS_BTN1': 'マウス左',
    'KC_MS_BTN2': 'マウス右',
    'KC_MS_BTN3': 'マウス中',
    'KC_MS_WH_DOWN': 'ホイール下',
    'KC_MS_WH_LEFT': 'ホイール左',
    'KC_MS_WH_RIGHT': 'ホイール右',
    'KC_MS_WH_UP': 'ホイール上',
    'KC_MSTP': '停止',
    'KC_MUTE': 'ミュート',
    'KC_NO': '',
    'KC_PAST': '*',
    'KC_PAUS': 'Pause',
    'KC_PGDN': 'PageDown',
    'KC_PGUP': 'PageUp',
    'KC_PMNS': '-',
    'KC_PPLS': '+',
    'KC_PSCR': 'PrintScreen',
    'KC_PSLS': '/',
    'KC_QUOT': "'",
    'KC_RALT': '右Alt',
    'KC_RBRC': ']',
    'KC_RCTL': '右Ctrl',
    'KC_RGUI': '右Win',
    'KC_RGHT': '→',
    'KC_RSFT': '右Shift',
    'KC_SCLN': ';',
    'KC_SLCK': 'ScrollLock',
    'KC_SLSH': '/',
    'KC_SPC': 'スペース',
    'KC_TAB': 'Tab',
    'KC_TRNS': '透過',
    'KC_UP': '↑',
    'KC_VOLD': '音量-',
    'KC_VOLU': '音量+',
    'RGB_HUD': 'RGB色相-',
    'RGB_HUI': 'RGB色相+',
    'RGB_MOD': 'RGBモード',
    'RGB_SAD': 'RGB彩度-',
    'RGB_SAI': 'RGB彩度+',
    'RGB_TOG': 'RGB切替',
    'RGB_VAD': 'RGB明度-',
    'RGB_VAI': 'RGB明度+',
    'S(KC_MINS)': '=',
}

def translate_keycode(keycode: str) -> str:
    """キーコードを日本語に変換"""
    keycode = keycode.strip()

    # 直接辞書にある場合
    if keycode in KEYCODE_JP:
        return KEYCODE_JP[keycode]

    # F1-F24
    if keycode.startswith('KC_F') and keycode[4:].isdigit():
        return keycode[3:]  # KC_F13 -> F13

    # A-Z, 0-9
    if re.match(r'^KC_[A-Z0-9]$', keycode):
        return keycode[3:]  # KC_A -> A

    # S(キー) - Shift+キー
    m = re.match(r'^S\((.+)\)$', keycode)
    if m:
        inner = translate_keycode(m.group(1))
        return f'Shift+{inner}'

    # C(キー) - Ctrl+キー
    m = re.match(r'^C\((.+)\)$', keycode)
    if m:
        inner = translate_keycode(m.group(1))
        return f'Ctrl+{inner}'

    # A(キー) - Alt+キー
    m = re.match(r'^A\((.+)\)$', keycode)
    if m:
        inner = translate_keycode(m.group(1))
        return f'Alt+{inner}'

    # LCA(キー) - Ctrl+Alt+キー
    m = re.match(r'^LCA\((.+)\)$', keycode)
    if m:
        inner = translate_keycode(m.group(1))
        return f'Ctrl+Alt+{inner}'

    # MEH(キー) - Ctrl+Shift+Alt+キー
    m = re.match(r'^MEH\((.+)\)$', keycode)
    if m:
        inner = translate_keycode(m.group(1))
        return f'Ctrl+Shift+Alt+{inner}'

    # TO(レイヤー番号)
    m = re.match(r'^TO\((\d+)\)$', keycode)
    if m:
        return f'レイヤー{m.group(1)}'

    # MACRO(番号)
    m = re.match(r'^MACRO\((\d+)\)$', keycode)
    if m:
        return f'マクロ{m.group(1)}'

    # その他はそのまま返す
    return keycode


def format_label_text(text: str, max_line_length: int = 10) -> str:
    """ラベル用にテキストを整形（+の後で改行）"""
    if not text or '+' not in text:
        return text

    # +で分割
    parts = text.split('+')
    lines = []
    current_line = []
    current_length = 0

    for i, part in enumerate(parts):
        # 最後のパート以外は+を付ける
        if i < len(parts) - 1:
            part_with_plus = part + '+'
        else:
            part_with_plus = part

        # 現在の行に追加すると長くなりすぎる場合は改行
        if current_length + len(part_with_plus) > max_line_length and current_line:
            lines.append(''.join(current_line))
            current_line = [part_with_plus]
            current_length = len(part_with_plus)
        else:
            current_line.append(part_with_plus)
            current_length += len(part_with_plus)

    # 残りを追加
    if current_line:
        lines.append(''.join(current_line))

    return '\n'.join(lines)


class RootWidget(RelativeLayout):
    centers = ListProperty([])  # 画像座標系の重心リスト [(cx, cy), ...]
    number_map = DictProperty({})  # インデックス -> 表示番号のマッピング
    label_positions = {}  # インデックス -> widget のマッピング
    current_edit_label = None  # 編集対象のラベル参照
    layers = []  # layout.jsonから読み込んだレイヤーデータ
    encoders = []  # エンコーダー情報
    current_layer = 0  # 現在選択中のレイヤー
    json_file_path = 'layout.json'  # 読み込むJSONファイルパス


def _load_image_rgb(path: str) -> Tuple[List[Tuple[int, int, int]], int, int]:
    if PILImage is None:
        raise RuntimeError('Pillow (PIL) が見つかりません。Pillow をインストールしてください。')
    im = PILImage.open(path).convert('RGB')
    w, h = im.size
    pixels = list(im.getdata())
    return pixels, w, h


def _black_mask(pixels: List[Tuple[int, int, int]], w: int, h: int, threshold: int = 40) -> List[bool]:
    mask = [False] * (w * h)
    for i, (r, g, b) in enumerate(pixels):
        if r < threshold and g < threshold and b < threshold:
            mask[i] = True
    return mask


def _neighbors(x: int, y: int, w: int, h: int):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx, ny


def _connected_components(mask: List[bool], w: int, h: int, min_pixels: int = 8) -> List[List[Tuple[int, int]]]:
    visited: Set[int] = set()
    comps: List[List[Tuple[int, int]]] = []
    for y in range(h):
        for x in range(w):
            idx = y * w + x
            if not mask[idx] or idx in visited:
                continue
            stack = [(x, y)]
            visited.add(idx)
            comp: List[Tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for nx, ny in _neighbors(cx, cy, w, h):
                    nidx = ny * w + nx
                    if mask[nidx] and nidx not in visited:
                        visited.add(nidx)
                        stack.append((nx, ny))
            if len(comp) >= min_pixels:
                comps.append(comp)
    return comps


def _centroid(points: List[Tuple[int, int]]) -> Tuple[float, float]:
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    n = max(1, len(points))
    return sx / n, sy / n


class MyApp(App):
    title = 'DOIO配置'

    def build(self):
        from kivy.core.window import Window

        root = RootWidget()
        # 固定サイズ設定
        root.size = (800, 600)
        root.size_hint = (None, None)

        # ファイルドロップイベントをバインド（Kivy 2.1+推奨の on_drop_file）
        Window.bind(on_drop_file=self._on_file_drop)
        # Kivyが旧on_dropfileへ転送する際の非推奨警告を抑制
        Window.on_dropfile = lambda *args: None

        # レイアウト完了後に配置
        Clock.schedule_once(lambda dt: self._place_labels(root), 0)
        return root

    def _on_file_drop(self, window, file_path, *args):
        """ファイルがドロップされた時の処理"""
        file_path_str = file_path.decode('utf-8') if isinstance(file_path, bytes) else file_path

        # .jsonファイルのみ受け付ける
        if not file_path_str.lower().endswith('.json'):
            return

        # rootウィジェットを取得
        root = self.root
        if not isinstance(root, RootWidget):
            return

        # ドロップされたJSONで既存ファイルを置き換える
        dest_path = root.json_file_path or 'layout.json'
        try:
            shutil.copyfile(file_path_str, dest_path)
            root.json_file_path = dest_path
        except Exception as e:
            print(f"JSONファイルの入れ替えに失敗しました: {e}")
            return

        # レイヤーを再読み込みして表示を更新
        self._reload_layout(root)

    def _place_labels(self, root: RootWidget):
        # kv上のImage（id: bg）とオーバーレイ取得
        bg_img = root.ids.get('bg') if hasattr(root, 'ids') else None
        overlay = root.ids.get('overlay') if hasattr(root, 'ids') else None
        if bg_img is None or overlay is None:
            return

        # 画像のピクセル解析
        try:
            pixels, iw, ih = _load_image_rgb('DOIO.png')
        except Exception as e:
            # Pillowが無い・ファイルが無い等。静かに諦める。
            return

        mask = _black_mask(pixels, iw, ih, threshold=40)
        comps = _connected_components(mask, iw, ih, min_pixels=12)
        centers = [_centroid(comp) for comp in comps]

        # ウィンドウサイズに対する画像のスケール計算
        window_w, window_h = 800, 600
        scale_x = window_w / iw
        scale_y = window_h / ih
        scale = min(scale_x, scale_y)  # アスペクト比維持

        # 画像の表示サイズ
        disp_w = iw * scale
        disp_h = ih * scale

        # センタリングオフセット
        off_x = (window_w - disp_w) / 2.0
        off_y = (window_h - disp_h) / 2.0

        # 重心リストを更新
        root.centers = centers

        # 番号マッピング（連続した状態でインデックス5と6の位置を入れ替え）
        root.centers.insert(10,root.centers.pop(5))
        root.centers.insert(10,root.centers.pop(9))

        root.centers.extend([(750, 200),(870, 200),(820, 510)])

        root.number_map = {i: i for i in range(len(root.centers))}

        # 指定されたJSONファイルから全レイヤーとエンコーダー情報を読み込む
        try:
            with open(root.json_file_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
                root.layers = layout_data['layers']
                root.encoders = layout_data.get('encoders', [])
        except Exception as e:
            root.layers = []
            root.encoders = []
            print(f"JSONファイル読み込みエラー: {e}")

        if root.encoders:
            root.encoders=list(zip(*root.encoders))


        # ラジオボタンのイベントバインディング
        if hasattr(root, 'ids'):
            for i, radio_id in enumerate(['layer0_radio', 'layer1_radio', 'layer2_radio', 'layer3_radio']):
                radio = root.ids.get(radio_id)
                if radio:
                    radio.bind(active=lambda cb, val, layer_idx=i: self._on_layer_change(root, layer_idx, val))

        # 初期レイヤー（レイヤー1 = layers[0]）で表示
        self._update_labels(root, overlay, off_x, off_y, scale, ih)

    def _update_labels(self, root: RootWidget, overlay, off_x, off_y, scale, ih):
        """ラベルの表示内容を更新"""
        layer_data = root.layers[root.current_layer] if root.current_layer < len(root.layers) else []

        # 既存の自動配置Labelを一旦掃除（再実行に備え）
        for child in list(overlay.children):
            if getattr(child, '_auto_generated', False):
                overlay.remove_widget(child)

        # 各センタへLabelを配置（小さめのバッジ）
        root.label_positions.clear()
        for idx, (cx, cy) in enumerate(root.centers[:19]):
            # PIL座標は上原点、Kivyは下原点のため反転
            kx = off_x + cx * scale
            ky = off_y + (ih - cy) * scale
            # kv側で定義した BorderLabel を生成
            display_num = root.number_map.get(idx, idx)
            # layer_dataからテキストを取得（最後の1つは無視）して日本語化
            key_code = layer_data[idx] if idx < len(layer_data) - 1 else ""
            key_text = translate_keycode(key_code)
            # +の位置で改行を挿入
            formatted_text = format_label_text(key_text)
            lbl = Factory.ButtonPushLabel(text=formatted_text)
            lbl._auto_generated = True
            lbl._label_index = idx
            # 中心合わせ（Labelは左下起点）
            lbl.pos = (kx - lbl.width / 2.0, ky - lbl.height / 2.0)
            root.label_positions[idx] = lbl
            overlay.add_widget(lbl)

        encoder_data = root.encoders[root.current_layer]


        for i, enc in enumerate(root.centers[19:]):

            cx, cy = enc[0],enc[1]
            kx = off_x + cx * scale
            ky = off_y + (ih - cy) * scale

            # 回転方向の情報を取得
            encoder_actions = encoder_data[i]
            if len(encoder_actions) >= 2:
                # 上ラベル（左回転）
                h = 35 if i!=2 else 60
                up_key = translate_keycode(encoder_actions[0])
                up_lbl = Factory.ButtonRotateLabel(text=f'{up_key}')
                up_lbl._auto_generated = True
                up_lbl.pos = (kx - up_lbl.width / 1.5, ky + h)
                overlay.add_widget(up_lbl)

                # 下ラベル（右回転）
                h = 50 if i!=2 else 75
                down_key = translate_keycode(encoder_actions[1])
                down_lbl = Factory.ButtonRotateLabel(text=f'{down_key}')
                down_lbl._auto_generated = True
                down_lbl.pos = (kx - down_lbl.width / 2.5, ky - h)
                overlay.add_widget(down_lbl)

    def _reload_layout(self, root: RootWidget):
        """JSONファイルを再読み込みして表示を更新"""
        overlay = root.ids.get('overlay') if hasattr(root, 'ids') else None
        if not overlay:
            return

        try:
            pixels, iw, ih = _load_image_rgb('DOIO.png')
            window_w, window_h = 800, 600
            scale = min(window_w / iw, window_h / ih)
            disp_w = iw * scale
            disp_h = ih * scale
            off_x = (window_w - disp_w) / 2.0
            off_y = (window_h - disp_h) / 2.0

            # JSONファイルから再読み込み
            try:
                with open(root.json_file_path, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                    root.layers = layout_data['layers']
                    root.encoders = layout_data.get('encoders', [])
                    if root.encoders:
                        root.encoders = list(zip(*root.encoders))
            except Exception as e:
                print(f"JSONファイル読み込みエラー: {e}")
                return

            # ラベルを再生成
            self._update_labels(root, overlay, off_x, off_y, scale, ih)
        except Exception as e:
            print(f"レイアウト更新エラー: {e}")

    def _on_layer_change(self, root: RootWidget, layer_idx: int, is_active: bool):
        """レイヤー選択変更時のコールバック"""
        if not is_active:
            return
        root.current_layer = layer_idx
        # オーバーレイとパラメータを再取得して更新
        overlay = root.ids.get('overlay') if hasattr(root, 'ids') else None
        if overlay:
            # 画像解析パラメータを再取得（前回の値を保持）
            try:
                pixels, iw, ih = _load_image_rgb('DOIO.png')
                window_w, window_h = 800, 600
                scale = min(window_w / iw, window_h / ih)
                disp_w = iw * scale
                disp_h = ih * scale
                off_x = (window_w - disp_w) / 2.0
                off_y = (window_h - disp_h) / 2.0
                self._update_labels(root, overlay, off_x, off_y, scale, ih)
            except:
                pass


if __name__ == '__main__':
    from kivy.config import Config
    # ウィンドウサイズを固定し、リサイズ不可に設定
    Config.set('graphics', 'resizable', '0')
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '600')
    Config.write()

    MyApp().run()
