"""XMP sidecar writer for descriptive metadata (stdlib only).

Writes ``{stem}.xmp`` next to the media file. Works for images, PSD, and
video without format-specific binary writers. Catalog remains source of truth.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from madify.models import MediaMetadata

_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_DC = "http://purl.org/dc/elements/1.1/"
_XMP = "http://ns.adobe.com/xap/1.0/"


class XmpSidecarWriter:
    """Write Dublin Core title/description/subject into an XMP sidecar."""

    def write(self, path: str, metadata: MediaMetadata) -> None:
        """Create or overwrite ``path`` with ``.xmp`` substituted for the suffix."""
        media = Path(path)
        sidecar = media.with_suffix(".xmp")
        xml_text = _render_xmp(metadata)
        sidecar.write_text(xml_text, encoding="utf-8")


def sidecar_path_for(path: str) -> str:
    """Return the sibling ``.xmp`` path for a media file."""
    return str(Path(path).with_suffix(".xmp"))


def _render_xmp(metadata: MediaMetadata) -> str:
    """Build a minimal XMP packet as indented XML."""
    ET.register_namespace("rdf", _RDF)
    ET.register_namespace("dc", _DC)
    ET.register_namespace("xmp", _XMP)

    rdf = ET.Element(f"{{{_RDF}}}RDF")
    desc = ET.SubElement(rdf, f"{{{_RDF}}}Description")
    desc.set(f"{{{_RDF}}}about", "")

    title_el = ET.SubElement(desc, f"{{{_DC}}}title")
    title_li = ET.SubElement(title_el, f"{{{_RDF}}}Alt")
    title_item = ET.SubElement(title_li, f"{{{_RDF}}}li")
    title_item.set("{http://www.w3.org/XML/1998/namespace}lang", "x-default")
    title_item.text = metadata.title

    desc_el = ET.SubElement(desc, f"{{{_DC}}}description")
    desc_li = ET.SubElement(desc_el, f"{{{_RDF}}}Alt")
    desc_item = ET.SubElement(desc_li, f"{{{_RDF}}}li")
    desc_item.set("{http://www.w3.org/XML/1998/namespace}lang", "x-default")
    desc_item.text = metadata.description

    subject = ET.SubElement(desc, f"{{{_DC}}}subject")
    bag = ET.SubElement(subject, f"{{{_RDF}}}Bag")
    for tag in metadata.tags:
        item = ET.SubElement(bag, f"{{{_RDF}}}li")
        item.text = tag

    ET.indent(rdf, space="  ")
    body = ET.tostring(rdf, encoding="unicode")
    return (
        '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        f"{body}\n"
        "</x:xmpmeta>\n"
        '<?xpacket end="w"?>\n'
    )
