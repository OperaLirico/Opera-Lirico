"""REA cycle 01 — 核定 12 个字段待核。

对应 docs/rea-cycle-log.md 第 1 轮记录。
"""

import json
import pathlib

REG = pathlib.Path("research/evidence.json")
DATA = pathlib.Path("data/voice-structures.json")


NEW_SOURCES = [
    {"id": "E14", "kind": "review", "title": "StatPearls: Anatomy, Head and Neck, Palate (NBK557817)", "url": "https://www.ncbi.nlm.nih.gov/books/NBK557817/"},
    {"id": "E15", "kind": "review", "title": "StatPearls: Anatomy, Head and Neck, Oral Cavity (Mouth) (NBK545271)", "url": "https://www.ncbi.nlm.nih.gov/books/NBK545271/"},
    {"id": "E16", "kind": "review", "title": "StatPearls: Anatomy, Thorax, Muscles (NBK538321)", "url": "https://www.ncbi.nlm.nih.gov/books/NBK538321/"},
    {"id": "E17", "kind": "paper", "title": "International standards to document remaining autonomic function after spinal cord injury (PMC3425876)", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3425876/"},
    {"id": "E18", "kind": "review", "title": "StatPearls: Anatomy, Thorax, Lungs (NBK470197)", "url": "https://www.ncbi.nlm.nih.gov/books/NBK470197/"},
    {"id": "E19", "kind": "paper", "title": "Hirano cover-body model in a study of human vocal fold extracellular matrix (PMC7844040)", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7844040/"},
]

UPDATES = {
    "levator_veli_palatini": {
        "innervation": "迷走神经（CN X）经咽丛的咽支",
        "evidence": ["E13", "E14"],
    },
    "tensor_veli_palatini": {
        "innervation": "三叉神经下颌支（CN V3）的内侧翼突神经（软腭五肌中唯一不走迷走者）",
        "evidence": ["E13", "E14"],
    },
    "palatopharyngeus": {
        "innervation": "迷走神经（CN X）经咽丛",
        "evidence": ["E13", "E14"],
    },
    "palatoglossus": {
        "innervation": "迷走神经（CN X）经咽丛（舌肌中唯一不由舌下神经支配者）",
        "evidence": ["E13", "E14", "E15"],
    },
    "genioglossus_muscle": {
        "innervation": "舌下神经（CN XII）",
        "evidence": ["E5", "E15"],
    },
    "hyoglossus_muscle": {
        "innervation": "舌下神经（CN XII）",
        "evidence": ["E5", "E15"],
    },
    "styloglossus_muscle": {
        "innervation": "舌下神经（CN XII）",
        "evidence": ["E5", "E15"],
    },
    "diaphragm": {
        "innervation": "膈神经（C3–C5）",
        "evidence": ["E4", "E16"],
    },
    "external_intercostal": {
        "innervation": "肋间神经（T1–T11 前支）",
        "evidence": ["E4", "E16"],
    },
    "abdominal_muscles": {
        "innervation": "胸腰段脊神经前支（T7–L2；部分文献记 T6–L1，属于节段计数差异）",
        "evidence": ["E4", "E17"],
    },
    "lungs": {
        "innervation": "无自身运动肌；肺丛（迷走神经＋交感）支配气道平滑肌与腺体，胸膜与心包由膈神经（C3–C5）供应",
        "evidence": ["E3", "E18"],
    },
    "true_vocal_fold": {
        "layers": "Hirano cover-body 三组：被覆（上皮＋基底膜＋浅层固有层）｜移行（中层弹性＋深层胶原，即声韧带）｜体（甲杓肌/声带肌）。振动发生在被覆内，体提供支撑。",
        "evidence": ["E1", "E9", "E19"],
    },
}


def main():
    reg = json.loads(REG.read_text(encoding="utf-8"))
    have = {s["id"] for s in reg["sources"]}
    added = 0
    for s in NEW_SOURCES:
        if s["id"] in have:
            continue
        assert s["url"].startswith("http"), s["id"]
        reg["sources"].append(s)
        added += 1
    reg["sources"].sort(key=lambda s: int(s["id"][1:]))

    st = json.loads(DATA.read_text(encoding="utf-8"))
    by = {i["id"]: i for i in st["structures"]}
    srcs = {s["id"] for s in reg["sources"]}

    for sid, patch in UPDATES.items():
        item = by[sid]
        for k, v in patch.items():
            if k == "evidence":
                for e in v:
                    assert e in srcs, (sid, e)
                item["evidence"] = v
            else:
                assert isinstance(v, str) and v.strip(), (sid, k)
                item[k] = v
        item["pending_fields"] = [f for f in item.get("pending_fields", []) if f not in patch]
        print(sid, "pending ->", item["pending_fields"])

    left = [(i["id"], i["pending_fields"]) for i in st["structures"] if i.get("pending_fields")]
    assert not left, "still pending: %s" % left

    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DATA.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rd = pathlib.Path("research/README.md")
    text = rd.read_text(encoding="utf-8")
    if "REA 第 1 轮" not in text:
        note = (
            "\n> **2026-11-17 · REA 第 1 轮**：本文件原先的「待核清单」已并入 "
            "`data/voice-structures.json` 的 `pending_fields`，以数据门计数为准。"
            "本轮把字段级待核清空（12 → 0），结论与依据见 `docs/rea-cycle-log.md`。\n"
        )
        rd.write_text(text + note, encoding="utf-8")

    print("sources +%d -> %d; entries with pending fields: 0" % (added, len(reg["sources"])))


if __name__ == "__main__":
    main()
