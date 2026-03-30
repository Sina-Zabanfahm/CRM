from __future__ import annotations

import logging
from typing import Any


def log_llm_input(
    logger: logging.Logger,
    *,
    stage: str,
    run_id: str,
    url: str | None,
    page_number: Any,
    chunk: str,
    chunk_index: int,
    chunk_count: int,
    current_json: str | None = None,
) -> None:
    if not logger.isEnabledFor(logging.INFO):
        return

    base_message = (
        "Sending content to LLM. "
        "stage=%s run_id=%s url=%s page_number=%s chunk_index=%s chunk_count=%s"
    )

    if current_json is None:
        logger.info(
            base_message + "\nchunk:\n%s",
            stage,
            run_id,
            url,
            page_number,
            chunk_index + 1,
            chunk_count,
            chunk,
        )
        return

    logger.info(
        base_message + "\ncurrent_json:\n%s\nchunk:\n%s",
        stage,
        run_id,
        url,
        page_number,
        chunk_index + 1,
        chunk_count,
        current_json,
        chunk,
    )
