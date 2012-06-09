import unittest

import zbox_wiki_api


class TestPaginator(unittest.TestCase):
    def test_paginator(self):
        po = zbox_wiki_api.paginator.Paginator()

        po.total = 10
        po.limit = 3

        po.current_offset = 0
        self.assertEqual( po.count, 4 )
        self.assertEqual( po.has_previous_page, False )
        self.assertEqual( po.has_next_page, True )

        po.current_offset = 1
        self.assertEqual( po.count, 4 )
        self.assertEqual( po.has_previous_page, True )
        self.assertEqual( po.has_next_page, True )

        po.current_offset = 2
        self.assertEqual( po.count, 4 )
        self.assertEqual( po.has_previous_page, True )
        self.assertEqual( po.has_next_page, True )

        po.current_offset = 3
        self.assertEqual( po.count, 4 )
        self.assertEqual( po.has_previous_page, True )
        self.assertEqual( po.has_next_page, False )

if __name__ == "__main__":
    unittest.main()