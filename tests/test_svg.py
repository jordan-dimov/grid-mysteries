from grid_mysteries.rendering import svg


def test_text_serialises_attributes_in_the_committed_order() -> None:
    assert svg.text(30, 36, "Title", size=19, weight=600) == (
        '<text x="30" y="36" font-family="system-ui, \'Segoe UI\', sans-serif" '
        f'font-size="19" font-weight="600" fill="{svg.INK}">Title</text>'
    )
    assert svg.text("12.5", 4.0, "end", size=12, fill=svg.INK_2, anchor="end") == (
        '<text x="12.5" y="4.0" font-family="system-ui, \'Segoe UI\', sans-serif" '
        f'font-size="12" fill="{svg.INK_2}" text-anchor="end">end</text>'
    )


def test_document_opens_with_root_surface_and_optional_title() -> None:
    lines = svg.document(920, 420, title="How concentrated?")
    assert lines == [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="420" viewBox="0 0 920 420">',
        f'<rect width="920" height="420" fill="{svg.SURFACE}"/>',
        svg.text(30, 36, "How concentrated?", size=19, weight=600),
    ]
    assert len(svg.document(920, 420)) == 2
