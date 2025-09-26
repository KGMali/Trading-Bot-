from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List

_config: Dict[str, Any] = {"processors": []}


class processors:
    @staticmethod
    def add_log_level(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        event_dict["level"] = method_name
        return event_dict

    class TimeStamper:
        def __init__(self, fmt: str = "iso") -> None:
            self.fmt = fmt

        def __call__(
            self, logger: Any, method_name: str, event_dict: Dict[str, Any]
        ) -> Dict[str, Any]:
            event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
            return event_dict

    @staticmethod
    def JSONRenderer(sort_keys: bool = True) -> Callable[[Any, str, Dict[str, Any]], str]:
        def _render(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> str:
            return json.dumps(event_dict, sort_keys=sort_keys)

        return _render


class stdlib:
    class LoggerFactory:
        def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pragma: no cover
            return None


class BoundLogger:
    def __init__(self, name: str) -> None:
        self.name = name

    def bind(self, **kwargs: Any) -> "BoundLogger":  # pragma: no cover
        return self

    def _log(self, level: str, event: str, **kwargs: Any) -> None:
        event_dict: Dict[str, Any] = {"event": event}
        event_dict.update(kwargs)
        for processor in _config.get("processors", []):
            result = processor(self, level, event_dict)
            if isinstance(result, str):
                event_dict = {"message": result}
            else:
                event_dict = result
        print(json.dumps(event_dict))

    def info(self, event: str, **kwargs: Any) -> None:
        self._log("info", event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._log("error", event, **kwargs)


def configure(
    processors: Iterable[Callable[..., Any]] | None = None, logger_factory: Any | None = None
) -> None:
    _config["processors"] = list(processors or [])
    _config["factory"] = logger_factory


def get_logger(name: str) -> BoundLogger:
    return BoundLogger(name)
