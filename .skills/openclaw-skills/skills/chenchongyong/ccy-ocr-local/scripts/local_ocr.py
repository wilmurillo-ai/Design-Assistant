#!/usr/bin/env python3
import argparse
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps
import pytesseract

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None


FAST_PSMS = (6, 7, 11)
AUTO_PSMS = (6, 7, 11, 3)
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp'}
ROTATION_ANGLES = (0, 90, 180, 270)


def fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def candidate_tesseract_paths() -> list[Path]:
    candidates: list[Path] = []

    env_cmd = os.environ.get('TESSERACT_CMD')
    if env_cmd:
        candidates.append(Path(env_cmd).expanduser())

    if os.name == 'nt':
        program_files = [
            os.environ.get('ProgramFiles'),
            os.environ.get('ProgramFiles(x86)'),
            'C:/Program Files',
            'C:/Program Files (x86)',
        ]
        for base in program_files:
            if not base:
                continue
            candidates.append(Path(base) / 'Tesseract-OCR' / 'tesseract.exe')
            candidates.append(Path(base) / 'Tesseract' / 'tesseract.exe')

    return candidates


def resolve_tesseract_cmd(explicit_cmd: str | None = None) -> str:
    if explicit_cmd:
        explicit_path = Path(explicit_cmd).expanduser()
        if explicit_path.exists():
            return str(explicit_path)
        found = shutil.which(explicit_cmd)
        if found:
            return found
        fail(f'指定的 tesseract 不可用: {explicit_cmd}')

    found = shutil.which('tesseract')
    if found:
        return found

    for candidate in candidate_tesseract_paths():
        if candidate.exists():
            return str(candidate)

    fail('未找到 tesseract。可安装 Tesseract，或通过 --tesseract-cmd / TESSERACT_CMD 显式指定路径。Windows 常见路径示例：C:/Program Files/Tesseract-OCR/tesseract.exe')


def configure_tesseract(explicit_cmd: str | None = None) -> str:
    cmd = resolve_tesseract_cmd(explicit_cmd)
    pytesseract.pytesseract.tesseract_cmd = cmd
    return cmd


def tesseract_langs(tesseract_cmd: str) -> set[str]:
    try:
        out = subprocess.check_output([tesseract_cmd, '--list-langs'], stderr=subprocess.STDOUT, text=True)
    except Exception:
        return set()
    lines = [x.strip() for x in out.splitlines() if x.strip()]
    return set(lines[1:] if lines and 'List of available languages' in lines[0] else lines)


def ensure_langs(lang_expr: str, tesseract_cmd: str) -> None:
    langs = tesseract_langs(tesseract_cmd)
    missing = [x for x in lang_expr.split('+') if x and x not in langs]
    if missing:
        hint = ''
        if 'eng' in missing:
            hint = '；当前环境缺少 eng.traineddata，建议补齐英文语言包，或改用已安装语言运行。'
        fail(f'缺少 Tesseract 语言数据：{", ".join(missing)}。当前可用：{", ".join(sorted(langs)) or "无"}{hint}')


def open_image(img_path: Path) -> Image.Image:
    try:
        img = Image.open(img_path)
        return ImageOps.exif_transpose(img)
    except Exception as exc:
        fail(f'无法打开图片 {img_path}: {exc}')


def upscale_if_small(img: Image.Image, min_edge: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest >= min_edge or longest <= 0:
        return img
    scale = min_edge / float(longest)
    return img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)


def preprocess_pil(img_path: Path, min_edge: int, sharpen: bool) -> Image.Image:
    img = open_image(img_path)
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = upscale_if_small(img, min_edge)
    if sharpen:
        img = img.filter(ImageFilter.SHARPEN)
    return img


def preprocess_cv(img_path: Path, min_edge: int, sharpen: bool) -> Image.Image:
    assert cv2 is not None
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        fail(f'无法读取图片: {img_path}')

    h, w = img.shape[:2]
    longest = max(h, w)
    if 0 < longest < min_edge:
        scale = min_edge / float(longest)
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    if sharpen:
        img = cv2.GaussianBlur(img, (0, 0), 1.0)

    return Image.fromarray(img)


def preprocess_image(img_path: Path, min_edge: int, sharpen: bool, no_preprocess: bool) -> Image.Image:
    if no_preprocess:
        return open_image(img_path)
    if cv2 is not None:
        return preprocess_cv(img_path, min_edge=min_edge, sharpen=sharpen)
    return preprocess_pil(img_path, min_edge=min_edge, sharpen=sharpen)


def build_config(psm: int, dpi: int) -> str:
    return f'--oem 3 --psm {psm} -c user_defined_dpi={dpi} preserve_interword_spaces=1'


def run_text_ocr(img: Image.Image, lang: str, psm: int, dpi: int) -> str:
    return pytesseract.image_to_string(img, lang=lang, config=build_config(psm, dpi)).strip()


def score_text(text: str) -> tuple[int, int, int]:
    stripped = text.strip()
    non_space = sum(1 for ch in stripped if not ch.isspace())
    lines = sum(1 for line in stripped.splitlines() if line.strip())
    alnum = sum(1 for ch in stripped if ch.isalnum())
    return non_space, lines, alnum


def choose_psms(mode: str, manual_psm: int | None) -> tuple[int, ...]:
    if manual_psm is not None:
        return (manual_psm,)
    if mode == 'fast':
        return FAST_PSMS
    if mode == 'accurate':
        return AUTO_PSMS
    return (6,)


def run_best_text_ocr(img: Image.Image, lang: str, dpi: int, mode: str, manual_psm: int | None) -> tuple[str, int]:
    best_text = ''
    best_psm = manual_psm if manual_psm is not None else 6
    best_score = (-1, -1, -1)

    for psm in choose_psms(mode, manual_psm):
        text = run_text_ocr(img, lang=lang, psm=psm, dpi=dpi)
        score = score_text(text)
        if score > best_score:
            best_text = text
            best_psm = psm
            best_score = score
    return best_text, best_psm


def estimate_orientation_candidates(img: Image.Image) -> tuple[int, ...]:
    w, h = img.size
    if w >= h * 1.2:
        return (0, 180)
    if h >= w * 1.2:
        return (90, 270)
    return ROTATION_ANGLES


def autorotate_image(img: Image.Image, lang: str, dpi: int, mode: str, manual_psm: int | None, strategy: str) -> tuple[Image.Image, int, int, str]:
    candidate_angles = ROTATION_ANGLES if strategy == 'full' else estimate_orientation_candidates(img)

    best_img = img
    best_angle = 0
    best_psm = manual_psm if manual_psm is not None else 6
    best_text = ''
    best_score = (-1, -1, -1)

    for angle in candidate_angles:
        candidate = img.rotate(angle, expand=True) if angle else img
        text, psm = run_best_text_ocr(candidate, lang=lang, dpi=dpi, mode=mode, manual_psm=manual_psm)
        score = score_text(text)
        if score > best_score:
            best_img = candidate
            best_angle = angle
            best_psm = psm
            best_text = text
            best_score = score

    if strategy == 'smart' and len(candidate_angles) < len(ROTATION_ANGLES):
        non_space, lines, alnum = best_score
        weak_result = non_space < 12 or (lines == 0 and alnum < 8)
        if weak_result:
            return autorotate_image(img, lang=lang, dpi=dpi, mode=mode, manual_psm=manual_psm, strategy='full')

    return best_img, best_angle, best_psm, best_text


def image_to_tsv(img: Image.Image, lang: str, psm: int, dpi: int, min_conf: int) -> str:
    config = build_config(psm, dpi)
    data = pytesseract.image_to_data(img, lang=lang, config=config)
    reader = csv.DictReader(io.StringIO(data), delimiter='\t')
    out = io.StringIO()
    writer = csv.writer(out, delimiter='\t', lineterminator='\n')
    writer.writerow(['text', 'conf', 'left', 'top', 'width', 'height', 'line_num', 'block_num', 'page_num'])

    for row in reader:
        text = (row.get('text') or '').strip()
        conf_raw = (row.get('conf') or '').strip()
        try:
            conf = int(float(conf_raw))
        except Exception:
            conf = -1
        if not text or conf < min_conf:
            continue
        writer.writerow([
            text,
            conf,
            row.get('left', ''),
            row.get('top', ''),
            row.get('width', ''),
            row.get('height', ''),
            row.get('line_num', ''),
            row.get('block_num', ''),
            row.get('page_num', ''),
        ])
    return out.getvalue().rstrip('\n')


def collect_images(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if not input_path.is_dir():
        fail(f'输入路径不存在: {input_path}')
    walker = input_path.rglob('*') if recursive else input_path.glob('*')
    return sorted(p for p in walker if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def safe_relative_output_path(base_input: Path, img_path: Path, out_dir: Path, suffix: str) -> Path:
    try:
        rel = img_path.relative_to(base_input)
        return out_dir / rel.parent / f'{rel.stem}{suffix}'
    except Exception:
        return out_dir / f'{img_path.stem}{suffix}'


def build_json_payload(result: dict) -> dict:
    return {
        'path': result['path'],
        'format': result['format'],
        'mode': result['mode'],
        'lang': result['lang'],
        'psm': result['psm'],
        'rotation_angle': result['rotation_angle'],
        'orientation_strategy': result['orientation_strategy'],
        'elapsed_ms': result['elapsed_ms'],
        'chars': result['chars'],
        'content': result['content'],
        'tesseract_cmd': result['tesseract_cmd'],
    }


def process_one(img_path: Path, args: argparse.Namespace) -> dict:
    started = time.perf_counter()
    img = preprocess_image(
        img_path,
        min_edge=max(1, args.min_edge),
        sharpen=args.sharpen,
        no_preprocess=args.no_preprocess,
    )

    rotation_angle = 0
    best_psm = args.psm if args.psm is not None else 6
    orientation_strategy = 'off'

    if args.format == 'text':
        if args.autorotate:
            orientation_strategy = args.autorotate_strategy
            img, rotation_angle, best_psm, content = autorotate_image(
                img,
                lang=args.lang,
                dpi=args.dpi,
                mode=args.mode,
                manual_psm=args.psm,
                strategy=args.autorotate_strategy,
            )
        else:
            content, best_psm = run_best_text_ocr(img, lang=args.lang, dpi=args.dpi, mode=args.mode, manual_psm=args.psm)
    else:
        if args.autorotate:
            orientation_strategy = args.autorotate_strategy
            img, rotation_angle, best_psm, _ = autorotate_image(
                img,
                lang=args.lang,
                dpi=args.dpi,
                mode=args.mode,
                manual_psm=args.psm,
                strategy=args.autorotate_strategy,
            )
        psm = args.psm if args.psm is not None else best_psm
        content = image_to_tsv(img, lang=args.lang, psm=psm, dpi=args.dpi, min_conf=args.min_conf)
        best_psm = psm

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        'path': str(img_path),
        'content': content,
        'psm': best_psm,
        'elapsed_ms': elapsed_ms,
        'chars': len(content),
        'rotation_angle': rotation_angle,
        'format': args.format,
        'mode': args.mode,
        'lang': args.lang,
        'orientation_strategy': orientation_strategy,
        'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd,
    }


def print_single_result(result: dict, out: str | None, json_mode: bool) -> None:
    rendered = json.dumps(build_json_payload(result), ensure_ascii=False, indent=2) if json_mode else result['content']

    if not out:
        print(rendered)
        return
    out_path = Path(out).expanduser().resolve()
    ensure_parent(out_path)
    out_path.write_text(rendered, encoding='utf-8')
    print(str(out_path))


def run_batch(images: list[Path], args: argparse.Namespace, base_input: Path) -> int:
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else None
    manifest = []
    failed = 0

    for img_path in images:
        try:
            result = process_one(img_path, args)
            record = {
                'path': result['path'],
                'elapsed_ms': result['elapsed_ms'],
                'chars': result['chars'],
                'psm': result['psm'],
                'rotation_angle': result['rotation_angle'],
                'orientation_strategy': result['orientation_strategy'],
                'format': result['format'],
                'mode': result['mode'],
                'tesseract_cmd': result['tesseract_cmd'],
                'status': 'ok',
            }
            if out_dir:
                suffix = '.json' if args.json else ('.tsv' if args.format == 'tsv' else '.txt')
                out_path = safe_relative_output_path(base_input, img_path, out_dir, suffix)
                ensure_parent(out_path)
                rendered = json.dumps(build_json_payload(result), ensure_ascii=False, indent=2) if args.json else result['content']
                out_path.write_text(rendered, encoding='utf-8')
                record['output'] = str(out_path)
            else:
                if args.json:
                    print(json.dumps(build_json_payload(result), ensure_ascii=False, indent=2))
                else:
                    print(f'===== {img_path} =====')
                    print(result['content'])
            manifest.append(record)
        except Exception as exc:
            failed += 1
            manifest.append({'path': str(img_path), 'status': 'error', 'error': str(exc)})
            print(f'[ERROR] {img_path}: {exc}', file=sys.stderr)

    if out_dir:
        manifest_path = out_dir / 'manifest.json'
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        print(str(manifest_path))
    return failed


def main() -> None:
    parser = argparse.ArgumentParser(description='Local offline OCR for image files.')
    parser.add_argument('image_path', help='本地图片路径，或目录（配合 --batch）')
    parser.add_argument('--lang', default='eng', help='OCR 语言，默认 eng，可传 chi_sim+eng')
    parser.add_argument('--psm', type=int, help='显式指定 Tesseract PSM；指定后不再自动尝试多个模式')
    parser.add_argument('--mode', choices=['balanced', 'fast', 'accurate'], default='balanced', help='OCR 模式：balanced 默认单次识别；fast/accurate 会自动尝试多个 PSM')
    parser.add_argument('--format', choices=['text', 'tsv'], default='text', help='输出格式：text 或 tsv')
    parser.add_argument('--json', action='store_true', help='以 JSON 输出 OCR 结果和元数据，适合自动化接入')
    parser.add_argument('--tesseract-cmd', help='显式指定 tesseract 可执行文件路径；Windows 未继承 PATH 时可用')
    parser.add_argument('--min-conf', type=int, default=0, help='TSV 模式下过滤低置信度文本，默认 0')
    parser.add_argument('--dpi', type=int, default=300, help='传给 Tesseract 的逻辑 DPI，默认 300')
    parser.add_argument('--min-edge', type=int, default=1800, help='较小图片会放大到该长边，默认 1800')
    parser.add_argument('--sharpen', action='store_true', help='启用轻量锐化，适合稍糊的图')
    parser.add_argument('--no-preprocess', action='store_true', help='关闭基础预处理')
    parser.add_argument('--autorotate', action='store_true', help='自动尝试方向并选择更优结果')
    parser.add_argument('--autorotate-strategy', choices=['smart', 'full'], default='smart', help='自动旋转策略：smart 先轻判再必要时全试；full 始终检查四个方向')
    parser.add_argument('--out', help='单文件模式下将结果写入文件；不传则输出到 stdout')
    parser.add_argument('--batch', action='store_true', help='批量模式：将 image_path 当作目录或多图入口处理')
    parser.add_argument('--recursive', action='store_true', help='批量模式下递归扫描子目录')
    parser.add_argument('--out-dir', help='批量模式下将每张图输出到目录，并生成 manifest.json')
    args = parser.parse_args()

    input_path = Path(args.image_path).expanduser().resolve()
    tesseract_cmd = configure_tesseract(args.tesseract_cmd)
    ensure_langs(args.lang, tesseract_cmd)

    if args.batch:
        images = collect_images(input_path, recursive=args.recursive)
        if not images:
            fail(f'未找到可处理图片: {input_path}')
        failed = run_batch(images, args, base_input=input_path)
        sys.exit(1 if failed else 0)

    if not input_path.exists() or not input_path.is_file():
        fail(f'图片不存在: {input_path}')

    result = process_one(input_path, args)
    print_single_result(result, args.out, json_mode=args.json)


if __name__ == '__main__':
    main()
