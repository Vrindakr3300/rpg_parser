import unittest

from cli import build_fetch_parser, build_scrape_parser, resolve_source


class TestResolveSource(unittest.TestCase):
    def test_source_omitted_parses_to_none(self):
        args = build_fetch_parser().parse_args(["http://example.test", "--system", "dnd5e"])
        self.assertIsNone(args.source)

    def test_dnd5e_resolves_to_open5e_when_source_omitted(self):
        args = build_scrape_parser().parse_args(["--system", "dnd5e"])
        resolve_source(args)
        self.assertEqual(args.source, "open5e")

    def test_default_system_resolves_to_aon_html(self):
        args = build_scrape_parser().parse_args([])
        resolve_source(args)
        self.assertEqual(args.source, "aon-html")

    def test_explicit_source_is_preserved(self):
        args = build_scrape_parser().parse_args(["--system", "dnd5e", "--source", "aon-html"])
        resolve_source(args)
        self.assertEqual(args.source, "aon-html")


if __name__ == "__main__":
    unittest.main()
