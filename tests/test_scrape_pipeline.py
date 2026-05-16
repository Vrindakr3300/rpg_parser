import unittest

from rpg_parser.core.pipeline import run_scrape_pipeline
from rpg_parser.core.ports import ExportTarget, FetchRequest, RawDocument, ScrapePipelineSpec, ScrapeRequest


class FakeScraper:
    def discover(self, _request: ScrapeRequest):
        yield FetchRequest(location="https://example.test/one")
        yield FetchRequest(location="https://example.test/two")


class FakeFetcher:
    def fetch(self, request: FetchRequest) -> RawDocument:
        return RawDocument(content=request.location, source=request.location)


class FakeParser:
    def parse(self, document: RawDocument) -> dict:
        return {"Name": document.content.rsplit("/", 1)[-1]}


class FakeExporter:
    def __init__(self):
        self.calls = []

    def export(self, data: dict, target: ExportTarget) -> None:
        self.calls.append((data, target))


class TestScrapePipeline(unittest.TestCase):
    def test_run_scrape_pipeline_discovers_fetches_parses_and_exports_many(self):
        exporter = FakeExporter()
        spec = ScrapePipelineSpec(
            scraper=FakeScraper(),
            fetcher=FakeFetcher(),
            parser=FakeParser(),
            exporter=exporter,
        )

        records = run_scrape_pipeline(
            spec,
            ScrapeRequest(limit=2),
            target_factory=lambda data, index, _request: ExportTarget(location=f"{index}-{data['Name']}.json"),
        )

        self.assertEqual(records, [{"Name": "one"}, {"Name": "two"}])
        self.assertEqual(exporter.calls[0][1].location, "1-one.json")
        self.assertEqual(exporter.calls[1][1].location, "2-two.json")


if __name__ == "__main__":
    unittest.main()
