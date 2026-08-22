# -*- coding: utf-8 -*-
"""Tests for access-denied caption classification."""
from __future__ import annotations

import unittest

from youtube_common import is_access_denied_error


class AccessDeniedTests(unittest.TestCase):
    def test_members_only(self) -> None:
        self.assertTrue(
            is_access_denied_error(
                "ERROR: [youtube] abc: Join this channel to get access to members-only content"
            )
        )

    def test_channel_members_phrasing(self) -> None:
        self.assertTrue(
            is_access_denied_error(
                "This video is available to this channel's members"
            )
        )

    def test_transient_not_denied(self) -> None:
        self.assertFalse(is_access_denied_error("HTTP Error 429: Too Many Requests"))

    def test_age_gate(self) -> None:
        self.assertTrue(
            is_access_denied_error(
                "ERROR: [youtube] abc: Sign in to confirm your age. "
                "Use --cookies-from-browser or --cookies for the authentication."
            )
        )


if __name__ == "__main__":
    unittest.main()
