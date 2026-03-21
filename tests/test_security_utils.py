import unittest

from github_repohunter.security_utils import (
    SlidingWindowRateLimiter,
    validate_markdown_output_path,
    parse_api_keys,
)


class TestSecurityUtils(unittest.TestCase):
    def test_validate_markdown_path_valid(self):
        path = validate_markdown_output_path("docs/architecture.md")
        self.assertEqual(path.as_posix(), "docs/architecture.md")

    def test_validate_markdown_path_rejects_absolute(self):
        with self.assertRaises(ValueError):
            validate_markdown_output_path("/tmp/architecture.md")

    def test_validate_markdown_path_rejects_traversal(self):
        with self.assertRaises(ValueError):
            validate_markdown_output_path("../architecture.md")

    def test_validate_markdown_path_rejects_non_md(self):
        with self.assertRaises(ValueError):
            validate_markdown_output_path("architecture.txt")

    def test_rate_limiter_enforces_limit(self):
        limiter = SlidingWindowRateLimiter(limit_per_minute=2)
        limiter.check("client-a", 100.0)
        limiter.check("client-a", 110.0)
        with self.assertRaises(ValueError):
            limiter.check("client-a", 120.0)

    def test_rate_limiter_window_expires(self):
        limiter = SlidingWindowRateLimiter(limit_per_minute=1)
        limiter.check("client-a", 100.0)
        limiter.check("client-a", 161.0)  # Old request expired

    def test_parse_api_keys_rotation(self):
        keys = parse_api_keys("k1, k2 ,k3", "k4")
        self.assertEqual(keys, {"k1", "k2", "k3", "k4"})


if __name__ == "__main__":
    unittest.main()
