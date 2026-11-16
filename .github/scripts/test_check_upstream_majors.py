import unittest
import urllib.error

from check_upstream_majors import find_new_majors, newest_stable_major


def releases(*versions):
    return [{"version_normalized": v} for v in versions]


class NewestStableMajorTest(unittest.TestCase):
    def test_ignores_pre_releases(self):
        self.assertEqual(newest_stable_major(releases("14.0.0.0-beta1", "13.2.0.0")), 13)

    def test_none_without_a_stable_release(self):
        self.assertIsNone(newest_stable_major(releases("1.0.0.0-RC1")))


class FindNewMajorsTest(unittest.TestCase):
    def index(self, latest="13", detect=None):
        return {"frameworks": [{"name": "laravel", "label": "Laravel", "latest": latest,
                                "detect": detect or [{"composer": "laravel/framework"}]}]}

    def test_reports_a_major_above_latest(self):
        found, unchecked = find_new_majors(self.index(), lambda pkg: releases("14.0.0.0", "13.9.0.0"))
        self.assertEqual(found, [{"name": "laravel", "label": "Laravel", "package": "laravel/framework",
                                  "latest": 13, "upstream": 14}])
        self.assertEqual(unchecked, [])

    def test_quiet_when_store_is_current(self):
        found, _ = find_new_majors(self.index(), lambda pkg: releases("13.9.0.0"))
        self.assertEqual(found, [])

    def test_falls_through_to_the_next_package_on_404(self):
        def fetch(pkg):
            if pkg == "a/missing":
                raise urllib.error.HTTPError(pkg, 404, "Not Found", None, None)
            return releases("14.0.0.0")

        index = self.index(detect=[{"composer": "a/missing"}, {"composer": "laravel/framework"}])
        found, _ = find_new_majors(index, fetch)
        self.assertEqual(found[0]["package"], "laravel/framework")

    def test_lists_frameworks_it_cannot_check(self):
        index = self.index(detect=[{"file": "artisan"}])
        index["frameworks"][0]["name"] = "nocomposer"
        found, unchecked = find_new_majors(index, lambda pkg: self.fail("fetched " + pkg))
        self.assertEqual((found, unchecked), ([], ["nocomposer"]))

    def test_other_http_errors_fail_loudly(self):
        def fetch(pkg):
            raise urllib.error.HTTPError(pkg, 500, "Server Error", None, None)

        with self.assertRaises(urllib.error.HTTPError):
            find_new_majors(self.index(), fetch)


if __name__ == "__main__":
    unittest.main()
