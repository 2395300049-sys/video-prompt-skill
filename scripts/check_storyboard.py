#!/usr/bin/env python3
"""Check a final-edit timeline and subject references; does not validate visual quality."""
import argparse
import json
import math
import re
import sys
from pathlib import Path


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(data):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ['根节点必须是对象'], warnings
    total = data.get('duration_seconds')
    if not number(total) or total <= 0:
        errors.append('duration_seconds 必须是有限正数')
    ratio = data.get('aspect_ratio')
    if not isinstance(ratio, str) or not re.fullmatch(r'[1-9]\d*:[1-9]\d*', ratio):
        errors.append('aspect_ratio 应为正整数宽高比，例如 9:16')
    chars = data.get('characters', {})
    if not isinstance(chars, dict):
        errors.append('characters 必须是主体ID到描述的对象；也可为空对象')
        chars = {}
    else:
        for key, value in chars.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(value, str) or not value.strip():
                errors.append('characters 的ID和描述必须是非空字符串')
    shots = data.get('shots')
    if not isinstance(shots, list) or not shots:
        return errors + ['shots 必须是非空数组'], warnings
    ids = set()
    previous_end = 0.0
    for index, shot in enumerate(shots, 1):
        label = f'第{index}镜'
        if not isinstance(shot, dict):
            errors.append(f'{label}必须是对象')
            previous_end = None
            continue
        sid = shot.get('id')
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f'{label} id 必须是非空字符串')
        elif sid in ids:
            errors.append(f'{label} id 重复：{sid}')
        else:
            ids.add(sid)
        start, end = shot.get('start'), shot.get('end')
        if not number(start) or not number(end):
            errors.append(f'{label} start/end 必须是有限数字')
            previous_end = None
        else:
            if start < 0 or end <= start:
                errors.append(f'{label}时间区间必须满足 0 <= start < end')
            if previous_end is not None and not math.isclose(start, previous_end, rel_tol=0, abs_tol=1e-6):
                issue = '重叠' if start < previous_end else '空隙'
                errors.append(f'{label}与前段出现时间{issue}：应从 {previous_end:g} 开始，实际 {start:g}')
            previous_end = end
        for field in ('scene', 'action', 'camera'):
            value = shot.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f'{label}缺少非空文字字段 {field}')
        subjects = shot.get('subjects', [])
        if not isinstance(subjects, list) or not all(isinstance(x, str) for x in subjects):
            errors.append(f'{label} subjects 必须是字符串数组')
        else:
            for subject in subjects:
                if subject not in chars:
                    errors.append(f'{label}引用了未定义主体：{subject}')
        for channel in ('dialogue', 'voiceover'):
            words = shot.get(channel, '')
            if not isinstance(words, str):
                errors.append(f'{label} {channel} 必须是字符串')
            elif words.strip():
                warnings.append(f'{label} {channel} 有文字；需用实际试读复核时长。')
    if number(total) and previous_end is not None and not math.isclose(total, previous_end, rel_tol=0, abs_tol=1e-6):
        errors.append(f'最后一镜结束 {previous_end:g} 秒，与目标 {total:g} 秒不一致')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description='检查成片时间轴、必需字段及主体引用；转场素材余量另列。')
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'读取失败：{exc}', file=sys.stderr)
        return 2
    errors, warnings = validate(data)
    print(json.dumps({'valid': not errors, 'errors': errors, 'warnings': warnings,
                      'scope': '仅验证数字、字段与主体引用，不证明画面连续性、表演可行性或生成效果。'}, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == '__main__':
    raise SystemExit(main())
