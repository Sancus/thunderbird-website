import json
import pytest
import os

from product_details import thunderbird_desktop

fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures/product_details')


class TestListReleases:
    def test_result_does_not_differ(self):
        """Ensure that the old list_releases behaviour does not differ aside from some 115 and above changes."""
        # Load the old list_releases result
        with open(os.path.join(fixtures_path, 'releases-old.json'), 'r') as fh:
            list_releases_old_result = dict(json.loads(fh.read()))

        # Load thunderbird.json from the point in time list_releases was re-written, and apply it to thunderbird_desktop
        with open(os.path.join(fixtures_path, 'thunderbird.json'), 'r') as fh:
            thunderbird_desktop.releases = json.loads(fh.read())

        list_releases_result = {
            k: {
                'major': v['major'],
                'minor': v['minor']
            }
            for k, v in thunderbird_desktop.list_releases()
        }

        # 128.0 wasn't in thunderbird_history_major/stability_releases.json, so it's not included here
        assert 128.0 not in list_releases_old_result

        # 115.10.2 and up are now esr builds, so this shouldn't be the same
        assert 115.0 in list_releases_result
        assert 115.0 in list_releases_old_result
        assert list_releases_result[115.0] != list_releases_old_result[115.0]

        # We're done with 128.0 and 115.0 now, bye!
        del list_releases_result[128.0]
        del list_releases_result[115.0]
        del list_releases_old_result[115.0]

        # Rest should be the same!
        assert list_releases_result == list_releases_old_result

    def test_128_esr_has_major_and_stability(self):
        """ESR builds are all labelled as esr, so we can't use the category to determine major vs minor release.
        This test ensures that our work-around works!"""
        # Load thunderbird.json from the point in time list_releases was re-written, and apply it to thunderbird_desktop
        with open(os.path.join(fixtures_path, 'thunderbird.json'), 'r') as fh:
            thunderbird_desktop.releases = json.loads(fh.read())

        list_releases_result = {
            k: v for k, v in thunderbird_desktop.list_releases()
        }

        assert 128.0 in list_releases_result
        assert '128.0.1esr' in list_releases_result[128.0]['minor']

    def test_release_and_esr_versions_coexist(self):
        """Major and ESR releases with the same base version should both exist."""

        with open('libs/product-details/public/1.0/thunderbird.json', 'r') as fh:
            thunderbird_desktop.releases = json.loads(fh.read())

        releases = thunderbird_desktop.list_releases()
        release_majors = [v['major'] for _, v in releases if v['channel'] == 'release']
        esr_majors = [v['major'] for _, v in releases if v['channel'] == 'esr']

        assert '140.0' in release_majors
        assert '140.0esr' in esr_majors
