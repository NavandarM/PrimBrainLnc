import shutil
import tempfile
from pathlib import Path

from Application import views

FIXTURES_DIR = Path(__file__).resolve().parent / 'fixtures'


class StaticFixturesMixin:
    """Points settings.STATIC_DIR at a throwaway copy of the small test fixtures
    (instead of the real multi-MB expression/fasta files) with a writable Tmp/ dir."""

    def setUp(self):
        super().setUp()
        self.static_dir = Path(tempfile.mkdtemp(prefix='pbl_static_'))
        shutil.copytree(FIXTURES_DIR / 'files', self.static_dir / 'files')
        (self.static_dir / 'Tmp').mkdir()

        override = self.settings(STATIC_DIR=self.static_dir)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.static_dir, ignore_errors=True)

        views._load_expression_data.cache_clear()
        self.addCleanup(views._load_expression_data.cache_clear)
