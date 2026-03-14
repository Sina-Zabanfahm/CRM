
import asyncio
from typing import Any

import requests
from dataclasses import replace
from playwright.async_api import async_playwright

from src.executions.base_execution import (BaseExecution,
                                           InputSpec)
from src.executions.input_kinds import InputKinds
from src.states.artifact import Artifact
from src.states.execution_state import ExecutionState
from src.states.web_resources import MetaDataKind, ResourceKind, WebResource

#Fetch Response metadata and bytes
class FetchExecution(BaseExecution):
    input_spec = (
        InputSpec(role = "web_resource", kind = InputKinds.WEBRESOURCE.value),
    )

    def __init__(self, name = None, id = None, timeout: int = 30):
        self.timeout = timeout
        super().__init__(name, id)

    async def aexecute(self, state: ExecutionState, run_id, inputs) -> Artifact[WebResource]:
        resource: WebResource = inputs["web_resource"].content
        fetched_res = await asyncio.to_thread(
            self._fetch_resource, resource
        )
        return Artifact(
            id = self.id,
            kind = InputKinds.WEBRESOURCE.value,
            name = self.name,
            content = fetched_res
        )

    def _fetch_resource(self, resource: WebResource) -> WebResource:
        if (resource.content is not None and len(resource.content)) >= 5:
            resource.kind = ResourceKind.MARKDOWN
            return resource
        
        if resource.kind == ResourceKind.PDF:
            return self._fetch_full_body(resource)
        
        return self._sniff_unknown(resource)
    
    def _sniff_unknown(self, resource: WebResource) -> WebResource:
        try:
            with requests.get(
                resource.target_url,
                stream=True,
                allow_redirects=True,
                timeout=self.timeout
            ) as response:
                final_url = response.url
                status_code = response.status_code
                response.raise_for_status()

                content_type = response.headers.get("Content-Type")
                prefix_body = resource.body if resource.body is not None else self._read_prefix(response)
                resource_kind = self._detect_from_bytes(content_type, prefix_body)

                resource_mod = replace(
                    resource,
                    final_url=final_url,
                    status_code=status_code,
                    content_type=content_type,
                    kind=resource_kind,
                    meta_data=self._merge_meta_data(
                        resource,
                        MetaDataKind.REQUESTS,
                        {"headers": self._headers_to_dict(response.headers)},
                    ),
                    error=None,
                )

                if resource_kind == ResourceKind.PDF:
                    return self._fetch_full_body(resource_mod)

                return resource_mod


        except requests.exceptions.SSLError:
            # Fallback: use Playwright with ignore_https_errors for broken TLS chains.
            try:
                final_url, status_code, content_type, headers, body = (
                    self._fetch_full_body_playwright_sync(resource.target_url)
                )
                prefix_body = body[:4096]
                resource_kind = self._detect_from_bytes(content_type, prefix_body)

                enriched = replace(
                    resource,
                    final_url=final_url,
                    status_code=status_code,
                    content_type=content_type,
                    kind=resource_kind,
                    meta_data=self._merge_meta_data(
                        resource,
                        MetaDataKind.PLAYWRIGHT,
                        {"headers": headers},
                    ),
                    error=None,
                )

                if resource_kind == ResourceKind.PDF:
                    return replace(enriched, body=body, kind=ResourceKind.PDF)

                # For non-PDF types, keep bytes out of state by default.
                return enriched
            except Exception as exc:
                return replace(resource, status_code=None, error=str(exc))

        except requests.HTTPError as exc:
            resp = exc.response
            return replace(
                resource,
                final_url=(resp.url if resp is not None else resource.final_url),
                status_code=(resp.status_code if resp is not None else None),
                content_type=(resp.headers.get("Content-Type") if resp is not None else None),
                meta_data=self._merge_meta_data(
                    resource,
                    MetaDataKind.REQUESTS,
                    {
                        "headers": (
                            self._headers_to_dict(resp.headers) if resp is not None else {}
                        ),
                        "error_type": exc.__class__.__name__,
                    },
                ),
                error=str(exc),
            )
        except requests.RequestException as exc:
            # DNS/TLS/timeout/connection errors have no HTTP response.
            return replace(
                resource,
                status_code=None,
                meta_data=self._merge_meta_data(
                    resource,
                    MetaDataKind.REQUESTS,
                    {"error_type": exc.__class__.__name__},
                ),
                error=str(exc),
            )
        
    @staticmethod
    def _read_prefix(response: requests.Response, 
                     max_bytes: int = 4096):
        chunks: list[bytes] = []
        total = 0

        for chunk in response.iter_content(chunk_size= 1024):
            if not chunk: continue

            chunks.append(chunk)
            total += len(chunk)
            if total >= max_bytes:
                break
        return b"".join(chunks)[:max_bytes]
    
    @staticmethod
    def _detect_from_bytes(content_type:str, prefix: bytes) -> ResourceKind:
        content_type_normalized = (content_type or "").lower()
        if( "pdf" in content_type_normalized or 
            prefix[:4] == b"%PDF"):
            return ResourceKind.PDF
        else:
            return ResourceKind.UNKNOWN

    def _fetch_full_body(self, resource: WebResource):
        try:
            with requests.get(
                resource.target_url,
                allow_redirects= True,
                timeout = self.timeout
            ) as response:
                final_url = response.url
                status_code = response.status_code
                content_type = response.headers.get("Content-Type")
                response.raise_for_status()
                return replace(
                        resource,
                        final_url=final_url,
                        content_type=content_type,
                        status_code=status_code,
                        body=response.content,
                        kind=ResourceKind.PDF,
                        meta_data=self._merge_meta_data(
                            resource,
                            MetaDataKind.REQUESTS,
                            {"headers": self._headers_to_dict(response.headers)},
                        ),
                        error=None,
                    )
        except requests.exceptions.SSLError:
            try:
                final_url, status_code, content_type, headers, body = (
                    self._fetch_full_body_playwright_sync(resource.target_url)
                )
                return replace(
                    resource,
                    final_url=final_url,
                    content_type=content_type,
                    status_code=status_code,
                    body=body,
                    kind=ResourceKind.PDF,
                    meta_data=self._merge_meta_data(
                        resource,
                        MetaDataKind.PLAYWRIGHT,
                        {"headers": headers},
                    ),
                    error=None,
                )
            except Exception as exc:
                return replace(
                    resource,
                    status_code=None,
                    meta_data=self._merge_meta_data(
                        resource,
                        MetaDataKind.PLAYWRIGHT,
                        {"error_type": exc.__class__.__name__},
                    ),
                    error=str(exc),
                )
        except requests.HTTPError as exc:
            resp = exc.response
            return replace(
                resource,
                final_url=(resp.url if resp is not None else resource.final_url),
                status_code=(resp.status_code if resp is not None else None),
                content_type=(resp.headers.get("Content-Type") if resp is not None else None),
                meta_data=self._merge_meta_data(
                    resource,
                    MetaDataKind.REQUESTS,
                    {
                        "headers": (
                            self._headers_to_dict(resp.headers) if resp is not None else {}
                        ),
                        "error_type": exc.__class__.__name__,
                    },
                ),
                error=str(exc),
            )
        except requests.RequestException as exc:
            return replace(
                resource,
                status_code=None,
                meta_data=self._merge_meta_data(
                    resource,
                    MetaDataKind.REQUESTS,
                    {"error_type": exc.__class__.__name__},
                ),
                error=str(exc),
            )

    def _fetch_full_body_playwright_sync(
        self, url: str
    ) -> tuple[str, int | None, str | None, dict[str, str], bytes]:
        return asyncio.run(self._fetch_full_body_playwright(url))

    async def _fetch_full_body_playwright(
        self, url: str
    ) -> tuple[str, int | None, str | None, dict[str, str], bytes]:
        async with async_playwright() as playwright:
            ctx = await playwright.request.new_context(ignore_https_errors=True)
            resp = await ctx.get(url, timeout=self.timeout * 1000)
            body = await resp.body()
            final_url = resp.url
            status_code = resp.status
            content_type = resp.headers.get("content-type")
            headers = dict(resp.headers)
            await ctx.dispose()
            return final_url, status_code, content_type, headers, body

    @staticmethod
    def _headers_to_dict(headers: Any) -> dict[str, str]:
        return {str(key): str(value) for key, value in dict(headers).items()}

    @staticmethod
    def _merge_meta_data(
        resource: WebResource,
        meta_kind: MetaDataKind,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        merged_meta = dict(resource.meta_data)
        existing_payload = merged_meta.get(meta_kind.value, {})

        if isinstance(existing_payload, dict):
            merged_meta[meta_kind.value] = {
                **existing_payload,
                **payload,
            }
        else:
            merged_meta[meta_kind.value] = payload

        return merged_meta
