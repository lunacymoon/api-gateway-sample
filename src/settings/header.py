from dataclasses import dataclass
from typing import Optional


@dataclass
class Header:
    token: str
    x_request_id: Optional[str] = None

    def dict(self, exclude_none: bool = True) -> dict:
        headers = {'Authorization': f'Bearer {self.token}'}
        if self.x_request_id is not None:
            headers['X-Request-ID'] = self.x_request_id

        return headers
