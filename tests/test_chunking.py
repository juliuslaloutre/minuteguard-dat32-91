from minuteguard.chunking import split_text


def test_chunking_preserves_global_line_numbers_and_overlap() -> None:
    text = "\n".join(f"line-{index}-" + "x" * 90 for index in range(1, 7))

    chunks = split_text(text, max_chars=220, overlap_lines=1)

    assert len(chunks) == 5
    assert chunks[0].first_line == 1
    assert chunks[0].last_line == 2
    assert chunks[1].first_line == chunks[0].last_line
    assert chunks[-1].last_line == 6


def test_chunking_rejects_unsafe_configuration() -> None:
    try:
        split_text("text", max_chars=100)
    except ValueError as exc:
        assert "at least 200" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ValueError")

