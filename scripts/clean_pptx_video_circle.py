from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.etree import ElementTree as ET


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def remove_slide_one_circle(source: Path, target: Path) -> None:
    slide_name = "ppt/slides/slide1.xml"
    remove_ids = {"3", "4", "5"}

    with ZipFile(source) as zin:
        slide_root = ET.fromstring(zin.read(slide_name))
        sp_tree = slide_root.find(".//p:spTree", NS)
        if sp_tree is None:
            raise RuntimeError("Could not find slide shape tree.")

        removed = 0
        for child in list(sp_tree):
            c_nv_pr = child.find(".//p:cNvPr", NS)
            if c_nv_pr is not None and c_nv_pr.attrib.get("id") in remove_ids:
                sp_tree.remove(child)
                removed += 1

        if removed != len(remove_ids):
            raise RuntimeError(f"Expected to remove {len(remove_ids)} shapes, removed {removed}.")

        target.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(target, "w", ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == slide_name:
                    data = ET.tostring(slide_root, encoding="utf-8", xml_declaration=True)
                zout.writestr(item, data)


if __name__ == "__main__":
    src = Path("/Users/amielpeled/Documents/courses/sprint_tec_academy/session_01_presentation.pptx")
    dst = Path(
        "outputs/manual-20260609-video-circle/presentations/clean-video-circle/output/"
        "session_01_presentation_clean_video_circle.pptx"
    )
    remove_slide_one_circle(src, dst)
    print(dst.resolve())
