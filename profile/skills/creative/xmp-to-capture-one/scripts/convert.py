import os
import sys
import argparse
import glob
import uuid
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

XMP_NS = {
    'x': 'adobe:ns:meta/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'crs': 'http://ns.adobe.com/camera-raw-settings/1.0/',
}

COLOR_SLICES = [
    ('Red', 0.0), ('Orange', 30.0), ('Yellow', 60.0), ('Green', 120.0),
    ('Aqua', 180.0), ('Blue', 240.0), ('Purple', 270.0), ('Magenta', 300.0),
]

def hsv_to_rgb(h, s, v):
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return r + m, g + m, b + m

def c1_color_balance(hue_deg, sat):
    if sat <= 0:
        return "1;1;1"
    sat_factor = (sat / 100.0) * 0.08
    r, g, b = hsv_to_rgb(hue_deg % 360, 1.0, 1.0)
    cr = 1.0 - (1.0 - r) * sat_factor
    cg = 1.0 - (1.0 - g) * sat_factor
    cb = 1.0 - (1.0 - b) * sat_factor
    return f"{cr:.12f};{cg:.12f};{cb:.12f}"

def format_curve(pts):
    if not pts:
        return "0,0;1,1"
    formatted = []
    x0, y0 = pts[0]
    if x0 <= 3:
        formatted.append((0.0, y0 / 255.0))
    else:
        formatted.append((0.0, y0 / 255.0))
        formatted.append((x0 / 255.0, y0 / 255.0))

    for x, y in pts[1:-1]:
        formatted.append((x / 255.0, y / 255.0))

    xn, yn = pts[-1]
    if xn >= 252:
        formatted.append((1.0, yn / 255.0))
    else:
        formatted.append((xn / 255.0, yn / 255.0))
        formatted.append((1.0, yn / 255.0))

    return ";".join(f"{x:.14f},{y:.14f}".rstrip('0').rstrip('.') for x, y in formatted)

def parse_xmp(path):
    tree = ET.parse(path)
    root = tree.getroot()
    desc = root.find('.//rdf:Description', XMP_NS)
    if desc is None:
        raise ValueError(f"No rdf:Description in {path}")

    params = {}
    for k, v in desc.attrib.items():
        if 'camera-raw-settings' in k:
            attr = k.split('}')[-1]
            try:
                params[attr] = float(v.replace('+', ''))
            except ValueError:
                params[attr] = v

    name_elem = desc.find('crs:Name/rdf:Alt/rdf:li', XMP_NS)
    if name_elem is not None and name_elem.text:
        params['PresetName'] = name_elem.text.strip()
    else:
        params['PresetName'] = Path(path).stem

    curves = {}
    for c_key in ['ToneCurvePV2012', 'ToneCurvePV2012Red', 'ToneCurvePV2012Green', 'ToneCurvePV2012Blue']:
        elem = desc.find(f'crs:{c_key}', XMP_NS)
        if elem is not None:
            pts = []
            for li in elem.findall('.//rdf:li', XMP_NS):
                if li.text:
                    parts = [p.strip() for p in li.text.split(',')]
                    if len(parts) == 2:
                        pts.append((float(parts[0]), float(parts[1])))
            if pts:
                curves[c_key] = pts
    return params, curves

def build_costyle(params, curves):
    c1 = {}
    name = params.get('PresetName', 'Style')
    c1['Name'] = name
    c1['UUID'] = str(uuid.uuid4()).upper()
    c1['StyleSource'] = "Styles"

    if 'Exposure2012' in params:
        c1['Exposure'] = f"{params['Exposure2012']:.4f}"
    if 'Contrast2012' in params:
        c1['Contrast'] = f"{params['Contrast2012']:.4f}"

    if 'Highlights2012' in params:
        c1['HighlightRecoveryEx'] = f"{-params['Highlights2012']:.4f}"
    if 'Shadows2012' in params:
        c1['ShadowRecovery'] = f"{params['Shadows2012']:.4f}"
    if 'Whites2012' in params:
        c1['WhiteRecovery'] = f"{params['Whites2012']:.4f}"
    if 'Blacks2012' in params:
        c1['BlackRecovery'] = f"{params['Blacks2012']:.4f}"

    if 'Clarity2012' in params:
        c1['Clarity'] = f"{params['Clarity2012']:.4f}"
        c1['ClarityMethod'] = "1"
    if 'Texture' in params:
        c1['ClarityStructure'] = f"{params['Texture']:.4f}"

    sat = params.get('Saturation', 0.0)
    vib = params.get('Vibrance', 0.0)
    combined_sat = sat + 0.6 * vib
    if abs(combined_sat) > 0.01:
        c1['Saturation'] = f"{combined_sat:.4f}"

    if 'ToneCurvePV2012' in curves:
        c1['GradationCurve'] = format_curve(curves['ToneCurvePV2012'])
    if 'ToneCurvePV2012Red' in curves:
        c1['GradationCurveRed'] = format_curve(curves['ToneCurvePV2012Red'])
    if 'ToneCurvePV2012Green' in curves:
        c1['GradationCurveGreen'] = format_curve(curves['ToneCurvePV2012Green'])
    if 'ToneCurvePV2012Blue' in curves:
        c1['GradationCurveBlue'] = format_curve(curves['ToneCurvePV2012Blue'])

    sh_hue = params.get('SplitToningShadowHue', 0.0)
    sh_sat = params.get('SplitToningShadowSaturation', 0.0)
    hi_hue = params.get('SplitToningHighlightHue', 0.0)
    hi_sat = params.get('SplitToningHighlightSaturation', 0.0)

    if sh_sat > 0 or hi_sat > 0:
        c1['ColorBalance'] = "1;1;1"
        c1['ColorBalanceMidtone'] = "1;1;1"
        c1['ColorBalanceShadow'] = c1_color_balance(sh_hue, sh_sat)
        c1['ColorBalanceHighlight'] = c1_color_balance(hi_hue, hi_sat)

    hsl = {color: {'h': params.get(f'HueAdjustment{color}', 0.0),
                   's': params.get(f'SaturationAdjustment{color}', 0.0),
                   'l': params.get(f'LuminanceAdjustment{color}', 0.0)}
           for color, _ in COLOR_SLICES}

    hsl['Red']['h'] += 0.5 * params.get('RedHue', 0.0)
    hsl['Red']['s'] += 0.5 * params.get('RedSaturation', 0.0)
    hsl['Green']['h'] += 0.5 * params.get('GreenHue', 0.0)
    hsl['Green']['s'] += 0.5 * params.get('GreenSaturation', 0.0)
    hsl['Blue']['h'] += 0.5 * params.get('BlueHue', 0.0)
    hsl['Blue']['s'] += 0.5 * params.get('BlueSaturation', 0.0)

    segs = []
    has_hsl = False
    for color, center in COLOR_SLICES:
        h_shift = hsl[color]['h'] * 0.3
        s_shift = hsl[color]['s'] * 0.8
        l_shift = hsl[color]['l'] * 0.02
        if abs(h_shift) > 0.01 or abs(s_shift) > 0.01 or abs(l_shift) > 0.001:
            has_hsl = True
        segs.append(f"1,1,1,{h_shift:.6f},{s_shift:.6f},{l_shift:.6f},255,0,{center:.12f},-22.500000000000,22.500000000000,-100,100,15,0,0,0,0")

    if has_hsl:
        segs.append("0,1,1,0,0,0,0,128,0,-2,2,-100,100,0,0,0,0,0")
        c1['ColorCorrections'] = ";".join(segs)

    grain = params.get('GrainAmount', 0.0)
    if grain > 0:
        c1['FilmGrainAmount'] = f"{grain:.4f}"
        c1['FilmGrainType'] = "2"
        c1['FilmGrainGranularity'] = f"{params.get('GrainSize', 30.0):.4f}"

    sharp = params.get('Sharpness', 0.0)
    if sharp > 0:
        c1['UsmAmount'] = f"{sharp * 2.0:.4f}"
        if 'SharpenRadius' in params:
            c1['UsmRadius'] = f"{params['SharpenRadius']:.2f}"

    xml_lines = ['<?xml version="1.0"?>', '<SL Engine="1300">']
    for k in sorted(c1.keys()):
        xml_lines.append(f'\t<E K="{k}" V="{c1[k]}" />')
    xml_lines.append('</SL>')
    return '\n'.join(xml_lines) + '\n'

def main():
    parser = argparse.ArgumentParser(description="Convert Lightroom XMP presets to Capture One .costyle")
    parser.add_argument("--input", "-i", required=True, help="Directory containing .xmp files")
    parser.add_argument("--name", "-n", default=None, help="Pack name (defaults to input folder name)")
    parser.add_argument("--no-install", action="store_true", help="Do not copy to AppData Styles")
    args = parser.parse_args()

    src_dir = Path(args.input)
    if not src_dir.exists():
        print(f"Error: directory does not exist: {src_dir}")
        sys.exit(1)

    pack_name = args.name or src_dir.name
    xmp_files = sorted(list(src_dir.glob("*.xmp")))
    if not xmp_files:
        print(f"No .xmp files found in {src_dir}")
        sys.exit(1)

    output_styles = src_dir / "Capture One Styles" / pack_name
    output_styles.mkdir(parents=True, exist_ok=True)

    target_dirs = [output_styles]
    if not args.no_install:
        appdata_c1 = Path(os.path.expandvars(r"%LOCALAPPDATA%\CaptureOne"))
        if appdata_c1.exists():
            target_dirs.append(appdata_c1 / "Styles" / pack_name)
            target_dirs.append(appdata_c1 / "Styles50" / pack_name)
            for td in target_dirs:
                td.mkdir(parents=True, exist_ok=True)

    converted = 0
    for xmp_p in xmp_files:
        try:
            params, curves = parse_xmp(xmp_p)
            content = build_costyle(params, curves)
            out_file = output_styles / f"{xmp_p.stem}.costyle"
            out_file.write_text(content, encoding='utf-8')
            if not args.no_install:
                for td in target_dirs[1:]:
                    (td / f"{xmp_p.stem}.costyle").write_text(content, encoding='utf-8')
            converted += 1
        except Exception as e:
            print(f"Error processing {xmp_p.name}: {e}")

    pack_path = src_dir / f"{pack_name} (Capture One).costylepack"
    with zipfile.ZipFile(pack_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in output_styles.glob("*.costyle"):
            zf.write(f, arcname=f"{pack_name}/{f.name}")

    print(f"OK: Converted {converted} presets to {pack_name}.")
    print(f"Pack: {pack_path}")

if __name__ == '__main__':
    main()
