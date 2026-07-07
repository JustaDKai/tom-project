import unittest

import app as app_module


class HomeRouteTests(unittest.TestCase):
    def test_home_page_contains_navigation_links(self):
        client = app_module.app.test_client()

        home_response = client.get("/")
        self.assertEqual(home_response.status_code, 200)
        body = home_response.get_data(as_text=True)
        self.assertIn("Template Generator", body)
        self.assertIn("Template Manager", body)

        generator_response = client.get("/generator")
        self.assertEqual(generator_response.status_code, 200)

    def test_manager_page_renders(self):
        client = app_module.app.test_client()

        manager_response = client.get("/manager")
        self.assertEqual(manager_response.status_code, 200)
        body = manager_response.get_data(as_text=True)
        self.assertIn("Template Manager", body)


if __name__ == "__main__":
    unittest.main()
